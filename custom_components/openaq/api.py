"""OpenAQ API client."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import OPENAQ_BASE_URL

_LOGGER = logging.getLogger(__name__)


class OpenAQApiClient:
    """Client to interact with the OpenAQ v3 API."""

    def __init__(self, session: aiohttp.ClientSession, api_key: str, location_id: int) -> None:
        self._session = session
        self._api_key = api_key
        self._location_id = location_id
        self._headers = {"X-API-Key": self._api_key}

    async def _get(self, url: str) -> dict[str, Any]:
        """Perform a GET request."""
        async with self._session.get(url, headers=self._headers) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_location(self) -> dict[str, Any]:
        """Fetch location info and sensors list."""
        url = f"{OPENAQ_BASE_URL}/locations/{self._location_id}"
        data = await self._get(url)
        results = data.get("results", [])
        if not results:
            raise ValueError(f"No location found for id {self._location_id}")
        return results[0]

    async def fetch_sensor(self, sensor_id: int) -> dict[str, Any]:
        """Fetch latest data for a single sensor."""
        url = f"{OPENAQ_BASE_URL}/sensors/{sensor_id}"
        data = await self._get(url)
        results = data.get("results", [])
        if not results:
            raise ValueError(f"No data found for sensor id {sensor_id}")
        return results[0]

    async def fetch_all_sensors_data(self) -> dict[str, Any]:
        """Fetch location + all sensor data, return structured dict."""
        location = await self.fetch_location()
        sensors_meta = location.get("sensors", [])

        sensors_data = {}
        for sensor_meta in sensors_meta:
            sensor_id = sensor_meta["id"]
            try:
                sensor_data = await self.fetch_sensor(sensor_id)
                sensors_data[sensor_id] = sensor_data
            except Exception as err:
                _LOGGER.warning("Failed to fetch sensor %s: %s", sensor_id, err)

        return {
            "location": location,
            "sensors": sensors_data,
        }
