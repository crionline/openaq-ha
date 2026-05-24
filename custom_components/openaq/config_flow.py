"""Config flow for OpenAQ integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    SelectOptionDict,
)

from .const import DOMAIN, CONF_API_KEY, CONF_LOCATION_ID, OPENAQ_BASE_URL, DEFAULT_RADIUS

_LOGGER = logging.getLogger(__name__)


class OpenAQConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenAQ."""

    VERSION = 1

    def __init__(self) -> None:
        self._api_key: str = ""
        self._locations: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Step 1 – API key
    # ------------------------------------------------------------------
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Ask for the API key and validate it."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            try:
                session = async_get_clientsession(self.hass)
                url = f"{OPENAQ_BASE_URL}/locations?limit=1"
                headers = {"X-API-Key": api_key}
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 401 or resp.status == 403:
                        errors["base"] = "invalid_auth"
                    elif resp.status >= 400:
                        errors["base"] = "cannot_connect"
                    else:
                        self._api_key = api_key
                        return await self.async_step_location()
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during API key validation")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Step 2 – location selection (geospatial or manual)
    # ------------------------------------------------------------------
    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Let the user pick a nearby location or enter an ID manually."""
        errors: dict[str, str] = {}

        # Fetch nearby locations on first visit (no user_input yet)
        if user_input is None:
            await self._fetch_nearby_locations(errors)
            return self._show_location_form(errors)

        # ---- Process submitted form ----
        manual = user_input.get("manual_location_id", False)

        if manual:
            location_id = user_input.get(CONF_LOCATION_ID)
            if not location_id:
                errors[CONF_LOCATION_ID] = "required"
                return self._show_location_form(errors, user_input)
            location_id = int(location_id)
            location_name, err = await self._validate_location_id(location_id)
            if err:
                errors["base"] = err
                return self._show_location_form(errors, user_input)
        else:
            chosen = user_input.get("location_choice")
            if not chosen:
                errors["base"] = "no_locations_nearby"
                return self._show_location_form(errors, user_input)
            location_id = int(chosen)
            # Get name from cached list, fall back to API
            location_name = next(
                (loc["label"] for loc in self._locations if loc["value"] == chosen),
                None,
            )
            if not location_name:
                location_name, err = await self._validate_location_id(location_id)
                if err:
                    errors["base"] = err
                    return self._show_location_form(errors, user_input)

        await self.async_set_unique_id(f"openaq_{location_id}")
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=location_name,
            data={CONF_API_KEY: self._api_key, CONF_LOCATION_ID: location_id},
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    async def _fetch_nearby_locations(self, errors: dict[str, str]) -> None:
        """Query OpenAQ for locations near the HA home coordinates."""
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude
        try:
            session = async_get_clientsession(self.hass)
            url = (
                f"{OPENAQ_BASE_URL}/locations"
                f"?coordinates={lat},{lon}&radius={DEFAULT_RADIUS}&limit=50"
            )
            headers = {"X-API-Key": self._api_key}
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    errors["base"] = "geo_query_failed"
                    return
                data = await resp.json()
                results = data.get("results", [])
                if not results:
                    errors["base"] = "no_locations_nearby"
                    return
                self._locations = [
                    {
                        "value": str(loc["id"]),
                        "label": self._format_location_label(loc),
                    }
                    for loc in results
                ]
        except aiohttp.ClientError:
            errors["base"] = "geo_query_failed"
        except Exception:
            _LOGGER.exception("Unexpected error fetching nearby locations")
            errors["base"] = "geo_query_failed"

    @staticmethod
    def _format_location_label(loc: dict[str, Any]) -> str:
        name = loc.get("name", "")
        locality = loc.get("locality") or ""
        country_code = loc.get("country", {}).get("code", "")
        parts = [p for p in [name, locality] if p]
        label = " – ".join(parts) if parts else str(loc["id"])
        if country_code:
            label += f" ({country_code})"
        return label

    async def _validate_location_id(
        self, location_id: int
    ) -> tuple[str, str | None]:
        """Return (name, error_key). error_key is None on success."""
        try:
            session = async_get_clientsession(self.hass)
            url = f"{OPENAQ_BASE_URL}/locations/{location_id}"
            headers = {"X-API-Key": self._api_key}
            async with session.get(url, headers=headers) as resp:
                if resp.status == 404:
                    return "", "location_not_found"
                resp.raise_for_status()
                data = await resp.json()
                results = data.get("results", [])
                if not results:
                    return "", "location_not_found"
                return results[0].get("name", str(location_id)), None
        except aiohttp.ClientResponseError as err:
            if err.status in (401, 403):
                return "", "invalid_auth"
            return "", "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected error validating location ID")
            return "", "unknown"

    def _show_location_form(
        self,
        errors: dict[str, str],
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Build the location selection form dynamically."""
        has_nearby = bool(self._locations)

        schema_dict: dict = {}

        if has_nearby:
            options = [
                SelectOptionDict(value=loc["value"], label=loc["label"])
                for loc in self._locations
            ]
            schema_dict[vol.Optional("location_choice")] = SelectSelector(
                SelectSelectorConfig(
                    options=options,
                    mode=SelectSelectorMode.LIST,
                )
            )

        schema_dict[vol.Optional("manual_location_id", default=not has_nearby)] = bool
        schema_dict[vol.Optional(CONF_LOCATION_ID)] = str

        return self.async_show_form(
            step_id="location",
            data_schema=vol.Schema(schema_dict),
            errors=errors,
            description_placeholders={
                "radius_km": str(DEFAULT_RADIUS // 1000),
                "lat": str(round(self.hass.config.latitude, 4)),
                "lon": str(round(self.hass.config.longitude, 4)),
            },
        )
