"""Base entity for NIBE DVC 10 integration."""
from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NibeDVC10Coordinator
from .hub import NibeDVC10Hub


class NibeDVC10Entity(CoordinatorEntity[NibeDVC10Coordinator]):
    """Base class for all NIBE DVC 10 entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NibeDVC10Coordinator,
        hub: NibeDVC10Hub,
        entry_id: str,
        host: str,
        unique_suffix: str,
    ) -> None:
        super().__init__(coordinator)
        self._hub = hub
        self._attr_unique_id = f"{entry_id}_{unique_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"NIBE DVC 10 ({host})",
            manufacturer="NIBE",
            model="DVC 10",
        )
