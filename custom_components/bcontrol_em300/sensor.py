"""Sensor platform for bcontrol_em300."""

from __future__ import annotations

from dataclasses import dataclass
import re

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfReactiveEnergy,
    UnitOfReactivePower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import BControlEM300ConfigEntry
from .const import STATIC_KEYS
from .entity import BControlEM300Entity

PARALLEL_UPDATES = 0

_NUMBER_PATTERN = re.compile(r"[-+]?\d*\.?\d+")


def _slug(text: str) -> str:
    """Return a simple slug for unique IDs."""
    text = text.replace("+", " plus")
    text = text.replace("-", " minus ")
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return normalized or "metric"


@dataclass(frozen=True)
class BControlSensorEntityDescription(SensorEntityDescription):
    """Description for bcontrol_em300 sensor entities."""

    numeric: bool = True


def _description_for_key(key: str) -> BControlSensorEntityDescription:
    """Build an entity description for a specific payload key."""
    if "Total Energy" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )

    if "Reactive Energy" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfReactiveEnergy.VOLT_AMPERE_REACTIVE_HOUR,
            device_class=SensorDeviceClass.REACTIVE_ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )

    if "Apparent Energy" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement="VAh",
            state_class=SensorStateClass.TOTAL_INCREASING,
        )

    if "Active Power" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfPower.WATT,
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if "Reactive Power" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE,
            device_class=SensorDeviceClass.REACTIVE_POWER,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if "Apparent Power" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
            device_class=SensorDeviceClass.APPARENT_POWER,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if "Current" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if "Voltage" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if "Frequency" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=UnitOfFrequency.HERTZ,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if "Power Factor" in key:
        return BControlSensorEntityDescription(
            key=key,
            native_unit_of_measurement=PERCENTAGE,
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
        )

    if key == "Status":
        return BControlSensorEntityDescription(
            key=key,
            icon="mdi:information-outline",
            numeric=False,
        )

    return BControlSensorEntityDescription(key=key)


def _coerce_numeric(value: StateType) -> float | int | None:
    """Parse a numeric value from meter payload values."""
    if value is None:
        return None

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        return value

    if not isinstance(value, str):
        return None

    number_match = _NUMBER_PATTERN.search(value.replace(",", "."))
    if not number_match:
        return None

    parsed = float(number_match.group())
    if parsed.is_integer():
        return int(parsed)

    return parsed


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BControlEM300ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up bcontrol_em300 sensors from a config entry."""
    coordinator = entry.runtime_data.coordinator
    if not coordinator.data:
        return

    metric_keys = [
        metric_key
        for metric_key in sorted(coordinator.data)
        if metric_key not in STATIC_KEYS
    ]

    async_add_entities(
        BControlEM300Sensor(
            entry=entry,
            metric_key=metric_key,
            entity_description=_description_for_key(metric_key),
        )
        for metric_key in metric_keys
    )


class BControlEM300Sensor(BControlEM300Entity, SensorEntity):
    """Representation of a bcontrol_em300 metric."""

    entity_description: BControlSensorEntityDescription

    def __init__(
        self,
        entry: BControlEM300ConfigEntry,
        metric_key: str,
        entity_description: BControlSensorEntityDescription,
    ) -> None:
        """Initialize sensor entity."""
        super().__init__(entry)
        self.entity_description = entity_description
        self._metric_key = metric_key
        self._attr_name = metric_key
        self._attr_unique_id = f"{entry.runtime_data.device_id}_{_slug(metric_key)}"

    @property
    def native_value(self) -> StateType:
        """Return the state for this sensor."""
        raw_value = self.coordinator.data.get(self._metric_key)

        if not self.entity_description.numeric:
            return None if raw_value is None else str(raw_value)

        return _coerce_numeric(raw_value)
