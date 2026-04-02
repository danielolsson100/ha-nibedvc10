"""Select platform for NIBE DVC 10 — fan speed, mode, and airflow direction."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AIRFLOW_ONEWAY,
    AIRFLOWS,
    DOMAIN,
    FAN_SPEED_LOW,
    FAN_SPEEDS,
    MODE_DAY,
    MODES,
)
from .entity import NibeDVC10Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    hub = data["hub"]
    host = entry.data[CONF_HOST]

    async_add_entities([
        NibeDVC10FanSpeedSelect(coordinator, hub, entry.entry_id, host),
        NibeDVC10ModeSelect(coordinator, hub, entry.entry_id, host),
        NibeDVC10AirflowSelect(coordinator, hub, entry.entry_id, host),
    ])


class NibeDVC10FanSpeedSelect(NibeDVC10Entity, SelectEntity):
    """Select the fan speed preset (Low / Medium / High)."""

    _attr_name = "Fan Speed"
    _attr_icon = "mdi:fan-speed-1"
    _attr_options = FAN_SPEEDS

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "fan_speed")

    @property
    def current_option(self) -> str:
        value = self.coordinator.data.get("fan_speed", FAN_SPEED_LOW)
        return value if value in self._attr_options else FAN_SPEED_LOW

    async def async_select_option(self, option: str) -> None:
        await self._hub.async_set_fan_speed(option)
        await self.coordinator.async_request_refresh()


class NibeDVC10ModeSelect(NibeDVC10Entity, SelectEntity):
    """Select the ventilation mode (Day / Night)."""

    _attr_name = "Mode"
    _attr_icon = "mdi:weather-night"
    _attr_options = MODES

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "mode")

    @property
    def current_option(self) -> str:
        value = self.coordinator.data.get("mode", MODE_DAY)
        return value if value in self._attr_options else MODE_DAY

    async def async_select_option(self, option: str) -> None:
        await self._hub.async_set_mode(option)
        await self.coordinator.async_request_refresh()


class NibeDVC10AirflowSelect(NibeDVC10Entity, SelectEntity):
    """Select the airflow direction (One-Way supply / Two-Way balanced / In only)."""

    _attr_name = "Airflow Direction"
    _attr_icon = "mdi:arrow-decision"
    _attr_options = AIRFLOWS

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "airflow")

    @property
    def current_option(self) -> str:
        value = self.coordinator.data.get("airflow", AIRFLOW_ONEWAY)
        return value if value in self._attr_options else AIRFLOW_ONEWAY

    async def async_select_option(self, option: str) -> None:
        await self._hub.async_set_airflow(option)
        await self.coordinator.async_request_refresh()
