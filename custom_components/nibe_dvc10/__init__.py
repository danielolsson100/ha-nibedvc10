"""NIBE DVC 10 ventilation unit integration for Home Assistant.

Communicates via UDP (port 4000) using a reverse-engineered protocol.
Provides a power switch and selects for fan speed, mode, and airflow direction.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import NibeDVC10Coordinator
from .hub import NibeDVC10Hub

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NIBE DVC 10 from a config entry."""
    host = entry.data[CONF_HOST]

    hub = NibeDVC10Hub(hass, host)
    coordinator = NibeDVC10Coordinator(hass, hub)
    # No blocking first refresh — coordinator pre-initialises data with safe
    # defaults and marks last_update_success=False so entities start unavailable.
    # The first real poll fires after update_interval (30 s).

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "hub": hub,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options (IP address) change."""
    await hass.config_entries.async_reload(entry.entry_id)
