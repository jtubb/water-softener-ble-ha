"""Data update coordinator for the Bluetooth Water Softener integration."""
import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError

from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UART_RX_CHAR_UUID,
    UART_TX_CHAR_UUID,
    REGEN_NOW_COMMAND,
    SET_SALT_LEVEL_COMMAND_PREFIX,
)
from .parser import WaterSoftenerBluetoothDeviceData

_LOGGER = logging.getLogger(__name__)


class WaterSoftenerDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the water softener."""

    def __init__(self, hass: HomeAssistant, address: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self.address = address
        self.parser = WaterSoftenerBluetoothDeviceData()
        self._client: BleakClient | None = None
        self._lock = asyncio.Lock()

    async def _async_update_data(self):
        """Fetch data from the device."""
        async with self._lock:
            if not self._client or not self._client.is_connected:
                await self._connect()

            return self.parser.data

    async def _connect(self):
        """Connect to the BLE device."""
        _LOGGER.debug("Connecting to %s", self.address)
        device = async_ble_device_from_address(self.hass, self.address)
        if not device:
            raise UpdateFailed(f"Device not found: {self.address}")

        self._client = BleakClient(device)
        try:
            await self._client.connect()
            await self._client.start_notify(
                UART_TX_CHAR_UUID, self._notification_handler
            )
            _LOGGER.debug("Connected and subscribed to notifications")
        except (BleakError, asyncio.TimeoutError) as e:
            raise UpdateFailed(f"Failed to connect: {e}")

    def _notification_handler(self, sender: int, data: bytearray):
        """Handle incoming BLE notifications."""
        _LOGGER.debug("Received notification: %s", data.hex())
        parsed_data = self.parser.parse_data(data)
        if parsed_data:
            self.async_set_updated_data(parsed_data)

    async def regenerate_now(self):
        """Send the 'Regenerate Now' command."""
        async with self._lock:
            if not self._client or not self._client.is_connected:
                await self._connect()
            
            try:
                _LOGGER.debug("Sending 'Regenerate Now' command")
                await self._client.write_gatt_char(
                    UART_RX_CHAR_UUID, REGEN_NOW_COMMAND, response=False
                )
            except BleakError as e:
                _LOGGER.error("Failed to send command: %s", e)
                await self._connect_and_retry(
                    self._client.write_gatt_char, UART_RX_CHAR_UUID, REGEN_NOW_COMMAND, response=False
                )

    async def set_salt_level(self, level: int):
        """Send the command to set the salt level."""
        command = SET_SALT_LEVEL_COMMAND_PREFIX + level.to_bytes(1, 'big')
        async with self._lock:
            if not self._client or not self._client.is_connected:
                await self._connect()
            
            try:
                _LOGGER.debug("Sending 'Set Salt Level' command: %s", command.hex())
                await self._client.write_gatt_char(
                    UART_RX_CHAR_UUID, command, response=False
                )
            except BleakError as e:
                _LOGGER.error("Failed to send command: %s", e)
                await self._connect_and_retry(
                    self._client.write_gatt_char, UART_RX_CHAR_UUID, command, response=False
                )

    async def _connect_and_retry(self, func, *args, **kwargs):
        """Attempt to reconnect and retry a BLE command."""
        try:
            await self._connect()
            await func(*args, **kwargs)
        except BleakError as e:
            _LOGGER.error("Failed to send command after reconnect: %s", e)

