"""Sensor platform for NIBE DVC 10 — read-only state sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AIRFLOW_BYTE_TO_OPT,
    AIRFLOW_ONEWAY,
    DOMAIN,
    FAN_BYTE_TO_OPT,
    FAN_SPEED_LOW,
    MODE_BYTE_TO_OPT,
    MODE_DAY,
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
        NibeDVC10FanSpeedSensor(coordinator, hub, entry.entry_id, host),
        NibeDVC10ModeSensor(coordinator, hub, entry.entry_id, host),
        NibeDVC10AirflowSensor(coordinator, hub, entry.entry_id, host),
        NibeDVC10ManualFanSpeedSensor(coordinator, hub, entry.entry_id, host),
    ])


class NibeDVC10FanSpeedSensor(NibeDVC10Entity, SensorEntity):
    """Reports the active fan speed preset as a text state."""

    _attr_name = "Fan Speed"
    _attr_icon = "mdi:fan"

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "sensor_fan_speed")

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get("fan_speed", FAN_SPEED_LOW)

    @property
    def extra_state_attributes(self) -> dict:
        raw = self.coordinator.data.get("fan_speed_raw")
        label = FAN_BYTE_TO_OPT.get(raw, "manual") if raw is not None else None
        return {"raw_byte": raw, "preset": label}


class NibeDVC10ModeSensor(NibeDVC10Entity, SensorEntity):
    """Reports the active ventilation mode (day / night)."""

    _attr_name = "Mode"
    _attr_icon = "mdi:weather-night"

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "sensor_mode")

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get("mode", MODE_DAY)


class NibeDVC10AirflowSensor(NibeDVC10Entity, SensorEntity):
    """Reports the active airflow direction."""

    _attr_name = "Airflow Direction"
    _attr_icon = "mdi:arrow-decision"

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "sensor_airflow")

    @property
    def native_value(self) -> str:
        return self.coordinator.data.get("airflow", AIRFLOW_ONEWAY)


class NibeDVC10ManualFanSpeedSensor(NibeDVC10Entity, SensorEntity):
    """Reports the manual fan speed setting as a percentage (9–100 %)."""

    _attr_name = "Manual Fan Speed"
    _attr_icon = "mdi:speedometer"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, hub, entry_id, host):
        super().__init__(coordinator, hub, entry_id, host, "sensor_fan_manual_pct")

    @property
    def native_value(self) -> int | None:
        return self.coordinator.data.get("fan_manual_pct")
