"""The bcontrol_em300 integration."""

from __future__ import annotations

from dataclasses import dataclass

from bcontrolpy import AuthenticationError, BControl, BControlCommunicationError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import BControlEM300Coordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]


@dataclass
class BControlEM300RuntimeData:
    """Runtime data for the bcontrol_em300 integration."""

    client: BControl
    coordinator: BControlEM300Coordinator
    device_id: str
    serial: str | None
    app_version: str | None
    host: str


type BControlEM300ConfigEntry = ConfigEntry[BControlEM300RuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: BControlEM300ConfigEntry
) -> bool:
    """Set up bcontrol_em300 from a config entry."""
    host = entry.data[CONF_HOST]
    client = BControl(
        ip=host,
        password=entry.data[CONF_PASSWORD],
        session=async_get_clientsession(hass),
    )

    try:
        login_data = await client.login()
    except AuthenticationError as err:
        raise ConfigEntryAuthFailed from err
    except BControlCommunicationError as err:
        raise ConfigEntryNotReady(f"Failed to connect to {host}") from err

    coordinator = BControlEM300Coordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    serial = login_data.get("serial")
    entry.runtime_data = BControlEM300RuntimeData(
        client=client,
        coordinator=coordinator,
        device_id=serial or host,
        serial=serial,
        app_version=login_data.get("app_version"),
        host=host,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: BControlEM300ConfigEntry
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.client.close()
    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant, entry: BControlEM300ConfigEntry
) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
