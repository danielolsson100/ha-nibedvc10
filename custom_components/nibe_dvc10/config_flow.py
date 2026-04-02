"""Config flow for NIBE DVC 10 integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from .const import DOMAIN
from .hub import NibeDVC10Hub

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class NibeDVC10ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NIBE DVC 10."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            hub = NibeDVC10Hub(self.hass, host)
            try:
                await hub.async_validate()
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"NIBE DVC 10 ({host})",
                    data=user_input,
                )
            except (OSError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during NIBE DVC 10 setup")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> NibeDVC10OptionsFlow:
        return NibeDVC10OptionsFlow()


class NibeDVC10OptionsFlow(OptionsFlow):
    """Allow changing the IP address after initial setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        current_host = self.config_entry.data.get(CONF_HOST, "")

        if user_input is not None:
            host = user_input[CONF_HOST]
            hub = NibeDVC10Hub(self.hass, host)
            try:
                await hub.async_validate()
                return self.async_create_entry(title="", data=user_input)
            except (OSError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during NIBE DVC 10 options update")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_host): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
