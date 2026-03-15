"""Constants for the bcontrol_em300 integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry

DOMAIN = "bcontrol_em300"

LOGGER = logging.getLogger(__package__)
MANUFACTURER = "B-Control"
MODEL = "EM300"

CONF_POLL_INTERVAL_SECONDS = "poll_interval_seconds"

DEFAULT_POLL_INTERVAL_SECONDS = 10
MIN_POLL_INTERVAL_SECONDS = 1

STATIC_KEYS: set[str] = {
    "serial",
    "Serial",
    "status",
    "Status",
    "app_version",
    "authentication",
}


def _coerce_interval_seconds(raw: str | int | None) -> int:
    """Coerce an interval value to a clamped integer seconds value."""
    if raw is None:
        return DEFAULT_POLL_INTERVAL_SECONDS

    try:
        seconds = int(raw)
    except (TypeError, ValueError):
        LOGGER.warning(
            "Invalid interval value '%s', using default %s seconds",
            raw,
            DEFAULT_POLL_INTERVAL_SECONDS,
        )
        return DEFAULT_POLL_INTERVAL_SECONDS

    if seconds < MIN_POLL_INTERVAL_SECONDS:
        LOGGER.warning(
            "Interval %s is below minimum %s, clamping",
            seconds,
            MIN_POLL_INTERVAL_SECONDS,
        )
        seconds = MIN_POLL_INTERVAL_SECONDS

    return seconds


def get_update_interval(config_entry: ConfigEntry | None = None) -> timedelta:
    """Return polling interval for coordinator updates."""
    if config_entry is None:
        return timedelta(seconds=DEFAULT_POLL_INTERVAL_SECONDS)

    seconds = _coerce_interval_seconds(
        config_entry.options.get(
            CONF_POLL_INTERVAL_SECONDS,
            DEFAULT_POLL_INTERVAL_SECONDS,
        )
    )
    return timedelta(seconds=seconds)
