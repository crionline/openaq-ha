"""Sensor platform for OpenAQ integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from . import OpenAQDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenAQ sensors from a config entry."""
    coordinator: OpenAQDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for sensor_id, sensor_data in coordinator.data["sensors"].items():
        sensors.append(OpenAQSensor(coordinator, sensor_id, sensor_data))

    async_add_entities(sensors, update_before_add=True)


class OpenAQSensor(CoordinatorEntity, SensorEntity):
    """Representation of an OpenAQ sensor."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: OpenAQDataUpdateCoordinator,
        sensor_id: int,
        sensor_data: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        param = sensor_data["parameter"]
        self._param_name = param["name"]  # e.g. "no2"
        self._unit = param["units"]       # e.g. "µg/m³"
        self._display_name = param.get("displayName", self._param_name)

        self._attr_unique_id = f"openaq_{sensor_id}"
        self._attr_name = f"openaq_{self._param_name}"
        self._attr_native_unit_of_measurement = self._unit

    @property
    def _sensor_data(self) -> dict[str, Any]:
        return self.coordinator.data["sensors"].get(self._sensor_id, {})

    @property
    def native_value(self) -> float | None:
        """Return the latest measurement value."""
        latest = self._sensor_data.get("latest", {})
        return latest.get("value")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        data = self._sensor_data
        latest = data.get("latest", {})
        summary = data.get("summary", {})
        datetime_info = latest.get("datetime", {})

        return {
            "latest_datetime_local": datetime_info.get("local"),
            "latest_datetime_utc": datetime_info.get("utc"),
            "display_name": self._display_name,
            "summary_min": summary.get("min"),
            "summary_max": summary.get("max"),
            "summary_avg": summary.get("avg"),
            "summary_median": summary.get("median"),
            "sensor_id": self._sensor_id,
        }

    @property
    def icon(self) -> str:
        """Return an icon based on parameter type."""
        icons = {
            "no2": "mdi:molecule",
            "o3": "mdi:weather-sunny-alert",
            "pm25": "mdi:air-filter",
            "pm10": "mdi:air-filter",
            "so2": "mdi:gas-cylinder",
            "co": "mdi:molecule-co",
            "no": "mdi:molecule",
        }
        return icons.get(self._param_name, "mdi:air-purifier")
