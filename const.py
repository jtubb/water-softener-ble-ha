"""Constants for the Bluetooth Water Softener integration."""

DOMAIN = "water_softener_ble"

# UUIDs for the Nordic UART Service
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
UART_RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UART_TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Command to trigger regeneration
REGEN_NOW_COMMAND = b"\x72\x72\x01"

# Command to set the salt level.
# The format is: 0x76 0x76 <page> <setting_id> <value>
# Based on the log, setting salt level seems to be page 1, setting_id 10.
# The value is a single byte.
SET_SALT_LEVEL_COMMAND_PREFIX = b"\x76\x76\x01\x0A"
