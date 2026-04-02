"""NIBE DVC 10 UDP hub — manages raw UDP communication with the ventilation unit.

Protocol (reverse-engineered, no vendor docs):
  Port : 4000/UDP
  Send : b'mobile' (6d6f62696c65) + command bytes
  Recv : b'master' (6d6173746572) + status payload (~36 bytes)

All I/O runs in a thread-pool executor so HA's event loop is never blocked.
"""
from __future__ import annotations

import logging
import socket
from typing import TYPE_CHECKING

from .const import (
    AIRFLOW_BYTE_TO_OPT,
    AIRFLOW_IN,
    AIRFLOW_ONEWAY,
    AIRFLOW_TWOWAY,
    CMD_AIRFLOW_IN,
    CMD_AIRFLOW_ONEWAY,
    CMD_AIRFLOW_TWOWAY,
    CMD_FAN_HIGH,
    CMD_FAN_LOW,
    CMD_FAN_MEDIUM,
    CMD_GET_STATUS,
    CMD_TOGGLE_MODE,
    CMD_TOGGLE_POWER,
    FAN_BYTE_TO_OPT,
    FAN_SPEED_HIGH,
    FAN_SPEED_LOW,
    FAN_SPEED_MEDIUM,
    IDX_AIRFLOW,
    IDX_FAN,
    IDX_FAN_MANUAL,
    IDX_MODE,
    IDX_POWER,
    MODE_BYTE_TO_OPT,
    MODE_DAY,
    MODE_NIGHT,
    UDP_PORT,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

_DATAGRAM_SIZE = 4096
_UDP_TIMEOUT_SEC = 2


_MIN_RESPONSE_LEN = 24  # need at least bytes 0-23


def _parse_status(data: bytes) -> dict:
    """Decode a status response into a typed dict.

    Byte layout (0-based):
      [7]  Power  01=ON / 00=OFF
      [9]  Mode   00=Day / 01=Night / 02=Party
      [19] Fan    01=Low / 02=Medium / 03=High / 04=Manual
      [21] Manual fan speed  0x00=9% ... 0xFF=100%
      [23] Airflow 00=OneWay / 01=TwoWay / 02=In
    """
    if len(data) < _MIN_RESPONSE_LEN:
        raise ValueError(
            f"NIBE DVC 10 response too short: {len(data)} bytes (expected >= {_MIN_RESPONSE_LEN}). "
            f"Raw: {data.hex()}"
        )

    # Manual fan speed: 0x00 = 9%, 0xFF = 100% — scale linearly to integer %
    raw_manual = data[IDX_FAN_MANUAL]
    manual_pct = round(9 + (raw_manual / 255) * 91)

    return {
        "power":          data[IDX_POWER] == 1,
        "mode":           MODE_BYTE_TO_OPT.get(data[IDX_MODE], MODE_DAY),
        "fan_speed":      FAN_BYTE_TO_OPT.get(data[IDX_FAN], FAN_SPEED_LOW),
        "fan_speed_raw":  data[IDX_FAN],
        "fan_manual_pct": manual_pct,
        "airflow":        AIRFLOW_BYTE_TO_OPT.get(data[IDX_AIRFLOW], AIRFLOW_ONEWAY),
    }


class NibeDVC10Hub:
    """UDP hub for the NIBE DVC 10 ventilation unit.

    Public async methods are awaitable from HA coroutines; the actual UDP I/O
    runs in a background thread via hass.async_add_executor_job.
    """

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        self._hass = hass
        self._host = host

    # ------------------------------------------------------------------
    # Sync helpers (run inside executor threads)
    # ------------------------------------------------------------------

    def _send_sync(self, cmd_hex: str) -> bytes:
        """Send a UDP command and return the raw response."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(_UDP_TIMEOUT_SEC)
        try:
            payload = bytes.fromhex(cmd_hex)
            sock.sendto(payload, (self._host, UDP_PORT))
            data, _ = sock.recvfrom(_DATAGRAM_SIZE)
            return data
        finally:
            sock.close()

    def _get_status_sync(self) -> dict:
        data = self._send_sync(CMD_GET_STATUS)
        return _parse_status(data)

    def _set_power_sync(self, on: bool) -> None:
        """Toggle power only when the current state differs from the requested one."""
        data = self._send_sync(CMD_GET_STATUS)
        current = data[IDX_POWER] == 1
        if current != on:
            self._send_sync(CMD_TOGGLE_POWER)

    def _set_mode_sync(self, mode: str) -> None:
        """Toggle day/night only when the current mode differs."""
        data = self._send_sync(CMD_GET_STATUS)
        current = MODE_BYTE_TO_OPT.get(data[IDX_MODE], MODE_DAY)
        if current != mode:
            self._send_sync(CMD_TOGGLE_MODE)

    def _set_fan_speed_sync(self, speed: str) -> None:
        cmd = {
            FAN_SPEED_LOW:    CMD_FAN_LOW,
            FAN_SPEED_MEDIUM: CMD_FAN_MEDIUM,
            FAN_SPEED_HIGH:   CMD_FAN_HIGH,
        }[speed]
        self._send_sync(cmd)

    def _set_airflow_sync(self, airflow: str) -> None:
        cmd = {
            AIRFLOW_ONEWAY: CMD_AIRFLOW_ONEWAY,
            AIRFLOW_TWOWAY: CMD_AIRFLOW_TWOWAY,
            AIRFLOW_IN:     CMD_AIRFLOW_IN,
        }[airflow]
        self._send_sync(cmd)

    # ------------------------------------------------------------------
    # Public async API
    # ------------------------------------------------------------------

    async def async_get_status(self) -> dict:
        """Fetch and return the current device state dict."""
        return await self._hass.async_add_executor_job(self._get_status_sync)

    async def async_validate(self) -> None:
        """Validate connectivity — raises OSError/TimeoutError on failure."""
        await self._hass.async_add_executor_job(self._get_status_sync)

    async def async_set_power(self, on: bool) -> None:
        await self._hass.async_add_executor_job(self._set_power_sync, on)

    async def async_set_mode(self, mode: str) -> None:
        await self._hass.async_add_executor_job(self._set_mode_sync, mode)

    async def async_set_fan_speed(self, speed: str) -> None:
        await self._hass.async_add_executor_job(self._set_fan_speed_sync, speed)

    async def async_set_airflow(self, airflow: str) -> None:
        await self._hass.async_add_executor_job(self._set_airflow_sync, airflow)
