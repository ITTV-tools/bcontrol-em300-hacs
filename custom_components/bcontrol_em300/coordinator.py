"""Data coordinator for bcontrol_em300."""

from __future__ import annotations

from typing import Any

from bcontrolpy import (
    AuthenticationError,
    BControl,
    BControlCommunicationError,
    BControlError,
)

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER, get_update_interval


class BControlEM300Coordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and hold meter data from bcontrolpy."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: BControl,
        config_entry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=get_update_interval(config_entry),
            config_entry=config_entry,
        )
        self._client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch latest data from the meter."""
        try:
            return await self._client.async_get_data()
        except AuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except BControlCommunicationError as err:
            raise UpdateFailed(f"Communication error: {err}") from err
        except BControlError as err:
            raise UpdateFailed(f"Unexpected API error: {err}") from err
