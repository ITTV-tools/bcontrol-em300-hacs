"""Entity base class for bcontrol_em300."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BControlEM300ConfigEntry
from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import BControlEM300Coordinator


class BControlEM300Entity(CoordinatorEntity[BControlEM300Coordinator]):
    """Common behavior for bcontrol_em300 entities."""

    _attr_has_entity_name = True

    def __init__(self, config_entry: BControlEM300ConfigEntry) -> None:
        """Initialize common fields for entities."""
        super().__init__(config_entry.runtime_data.coordinator)
        runtime_data = config_entry.runtime_data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, runtime_data.device_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            serial_number=runtime_data.serial,
            sw_version=runtime_data.app_version,
            name=f"{MODEL} {runtime_data.host}",
            configuration_url=f"http://{runtime_data.host}",
        )
