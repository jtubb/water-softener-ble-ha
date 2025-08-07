"""Sensor platform for Bluetooth Water Softener."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WaterSoftenerDataUpdateCoordinator

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="current_water_flow",
        name="Current Water Flow",
        native_unit_of_measurement="GPM",
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-pump",
    ),
    SensorEntityDescription(
        key="soft_water_remaining",
        name="Soft Water Remaining",
        native_unit_of_measurement=UnitOfVolume.GALLONS,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL,
        icon="mdi:water-minus",
    ),
    SensorEntityDescription(
        key="treated_water_usage_today",
        name="Treated Water Usage Today",
        native_unit_of_measurement=UnitOfVolume.GALLONS,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:water-sync",
    ),
    SensorEntityDescription(
        key="peak_flow_today",
        name="Peak Flow Today",
        native_unit_of_measurement="GPM",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-peak",
    ),
    SensorEntityDescription(
        key="water_hardness",
        name="Water Hardness",
        native_unit_of_measurement="GPG",
        icon="mdi:water-opacity",
    ),
    SensorEntityDescription(
        key="regeneration_time",
        name="Regeneration Time",
        icon="mdi:clock-start",
    ),
    SensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
    ),
    SensorEntityDescription(
        key="days_until_regeneration",
        name="Days Until Regeneration",
        native_unit_of_measurement="days",
        icon="mdi:calendar-clock",
    ),
    SensorEntityDescription(
        key="total_gallons_treated",
        name="Total Gallons Treated",
        native_unit_of_measurement=UnitOfVolume.GALLONS,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:chart-waterfall",
    ),
    SensorEntityDescription(
        key="brine_tank_level",
        name="Brine Tank Level",
        native_unit_of_measurement="lbs",
        icon="mdi:gauge",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: WaterSoftenerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        WaterSoftenerSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class WaterSoftenerSensor(CoordinatorEntity, SensorEntity):
    """A sensor for the Bluetooth Water Softener."""

    def __init__(
        self,
        coordinator: WaterSoftenerDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
            "name": "Water Softener",
            "manufacturer": "Unknown (from Bluetooth data)",
        }

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
