"""Button platform for Bluetooth Water Softener."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WaterSoftenerDataUpdateCoordinator

BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="regenerate_now",
    name="Regenerate Now",
    icon="mdi:reiterate",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator: WaterSoftenerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WaterSoftenerRegenerateNowButton(coordinator, BUTTON_DESCRIPTION)])


class WaterSoftenerRegenerateNowButton(CoordinatorEntity, ButtonEntity):
    """A button to trigger regeneration on the Bluetooth Water Softener."""

    def __init__(
        self,
        coordinator: WaterSoftenerDataUpdateCoordinator,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.address}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.address)},
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.regenerate_now()
