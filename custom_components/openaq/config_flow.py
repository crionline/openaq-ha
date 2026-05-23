"""Config flow for OpenAQ integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_API_KEY, CONF_LOCATION_ID, OPENAQ_BASE_URL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_LOCATION_ID): int,
    }
)


class OpenAQConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAQ."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            location_id = user_input[CONF_LOCATION_ID]

            try:
                session = async_get_clientsession(self.hass)
                url = f"{OPENAQ_BASE_URL}/locations/{location_id}"
                headers = {"X-API-Key": api_key}
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    results = data.get("results", [])
                    if not results:
                        errors["base"] = "location_not_found"
                    else:
                        location_name = results[0].get("name", str(location_id))
                        await self.async_set_unique_id(f"openaq_{location_id}")
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title=location_name,
                            data=user_input,
                        )
            except aiohttp.ClientResponseError as err:
                if err.status == 401:
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception during config flow")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
