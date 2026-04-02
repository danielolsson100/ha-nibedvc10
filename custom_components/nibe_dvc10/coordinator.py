"""DataUpdateCoordinator for NIBE DVC 10."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    AIRFLOW_ONEWAY,
    DOMAIN,
    FAN_SPEED_LOW,
    MODE_DAY,
    SCAN_INTERVAL,
)
from .hub import NibeDVC10Hub

_LOGGER = logging.getLogger(__name__)

# Safe defaults used before the first successful poll.
_DEFAULT_STATE: dict = {
    "power":          False,
    "mode":           MODE_DAY,
    "fan_speed":      FAN_SPEED_LOW,
    "fan_speed_raw":  1,
    "fan_manual_pct": 9,
    "airflow":        AIRFLOW_ONEWAY,
}


class NibeDVC10Coordinator(DataUpdateCoordinator[dict]):
    """Polls the NIBE DVC 10 every SCAN_INTERVAL seconds."""

    def __init__(self, hass: HomeAssistant, hub: NibeDVC10Hub) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self._hub = hub
        # Pre-populate data so entity properties never receive None.
        # Entities will be marked unavailable until last_update_success is True.
        self.data = _DEFAULT_STATE.copy()
        self.last_update_success = False

    async def _async_update_data(self) -> dict:
        try:
            return await self._hub.async_get_status()
        except (OSError, TimeoutError) as exc:
            _LOGGER.warning("nibe_dvc10: cannot reach device: %s", exc)
            raise UpdateFailed(f"Cannot reach NIBE DVC 10: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            _LOGGER.error(
                "nibe_dvc10: unexpected error fetching status: %s — %s",
                type(exc).__name__,
                exc,
            )
            raise UpdateFailed(f"Unexpected error from NIBE DVC 10: {exc}") from exc
