"""Switch platform for NIBE DVC 10 — controls power on/off."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import NibeDVC10Entity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        NibeDVC10PowerSwitch(
            data["coordinator"],
            data["hub"],
            entry.entry_id,
            entry.data[CONF_HOST],
        )
    ])


class NibeDVC10PowerSwitch(NibeDVC10Entity, SwitchEntity):
    """Switch that turns the ventilation unit on or off."""

    _attr_name = "Power"
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "power")

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("power", False)

    async def async_turn_on(self, **kwargs) -> None:
        await self._hub.async_set_power(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self._hub.async_set_power(False)
        await self.coordinator.async_request_refresh()
