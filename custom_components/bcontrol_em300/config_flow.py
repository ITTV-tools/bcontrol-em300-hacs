"""Config flow for the bcontrol_em300 integration."""

from __future__ import annotations

from typing import Any

from bcontrolpy import (
    AuthenticationError,
    BControl,
    BControlCommunicationError,
    BControlError,
)
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_POLL_INTERVAL_SECONDS,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DOMAIN,
    LOGGER,
    MIN_POLL_INTERVAL_SECONDS,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate user input and return display metadata for the entry."""
    client = BControl(
        ip=data[CONF_HOST],
        password=data[CONF_PASSWORD],
        session=async_get_clientsession(hass),
    )

    login_data = await client.login()
    serial = login_data.get("serial")

    return {
        "title": serial or data[CONF_HOST],
        "unique_id": serial or data[CONF_HOST],
    }


class BControlEM300ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for bcontrol_em300."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> BControlEM300OptionsFlow:
        """Return the options flow handler."""
        return BControlEM300OptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
            try:
                info = await validate_input(self.hass, user_input)
            except BControlCommunicationError:
                errors["base"] = "cannot_connect"
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except BControlError:
                errors["base"] = "unknown"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured(
                    updates={
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    }
                )

                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class BControlEM300OptionsFlow(OptionsFlowWithReload):
    """Handle options flow for bcontrol_em300."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the integration options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_POLL_INTERVAL_SECONDS,
            DEFAULT_POLL_INTERVAL_SECONDS,
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_POLL_INTERVAL_SECONDS,
                        default=current_interval,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(min=MIN_POLL_INTERVAL_SECONDS),
                    )
                }
            ),
        )
