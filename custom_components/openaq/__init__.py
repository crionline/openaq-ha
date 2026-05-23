"""OpenAQ custom integration for Home Assistant."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_KEY, CONF_LOCATION_ID, SCAN_INTERVAL
from .api import OpenAQApiClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenAQ from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    location_id = entry.data[CONF_LOCATION_ID]

    session = async_get_clientsession(hass)
    client = OpenAQApiClient(session, api_key, location_id)

    coordinator = OpenAQDataUpdateCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class OpenAQDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage data fetching from OpenAQ."""

    def __init__(self, hass: HomeAssistant, client: "OpenAQApiClient") -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self):
        """Fetch data from OpenAQ."""
        try:
            return await self.client.fetch_all_sensors_data()
        except Exception as err:
            raise UpdateFailed(f"Error communicating with OpenAQ API: {err}") from err
