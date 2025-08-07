"""Number platform for Bluetooth Water Softener."""
from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WaterSoftenerDataUpdateCoordinator

NUMBER_DESCRIPTION = NumberEntityDescription(
    key="brine_tank_level",
    name="Brine Tank Level",
    icon="mdi:gauge",
    mode=NumberMode.BOX,
    native_min_value=0,
    native_max_value=200,  # Adjust as needed
    native_step=1,
    native_unit_of_measurement="lbs",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator: WaterSoftenerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WaterSoftenerSaltLevelNumber(coordinator, NUMBER_DESCRIPTION)])


class WaterSoftenerSaltLevelNumber(CoordinatorEntity, NumberEntity):
    """A number entity to set the salt level on the Bluetooth Water Softener."""

    def __init__(
        self,
        coordinator: WaterSoftenerDataUpdateCoordinator,
        description: NumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}_set"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }

    @property
    def native_value(self) -> float | None:
        """Return the current salt level."""
        return self.coordinator.data.get(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        """Set the salt level."""
        await self.coordinator.set_salt_level(int(value))
        # We optimistically update the state. The coordinator will get the
        # real value from the device notification shortly.
        self.async_write_ha_state()

