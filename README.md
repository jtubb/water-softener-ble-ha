# CS Meter Soft - Water Softener Integration for Home Assistant

This is a custom component for Home Assistant to integrate with Bluetooth-enabled water softeners that identify as "CS_Meter_Soft".

## Features

* Discovers and connects to your water softener via Bluetooth LE.
* Creates sensors in Home Assistant for various metrics from the device.
* Real-time updates.

## Installation

1.  Copy the `cs_meter_soft` directory into your Home Assistant `custom_components` directory.
2.  Restart Home Assistant.
3.  Go to **Settings** -> **Devices & Services**.
4.  Click **Add Integration** and search for "CS Meter Soft".
5.  Follow the on-screen instructions to select your device.

## Configuration

Configuration is handled via the UI. The integration will automatically scan for and list nearby "CS_Meter_Soft" devices.

## Sensors

This integration will create the following sensors (based on initial analysis):

* **Remaining Capacity**: An estimate of the remaining water softening capacity.
* **Current Flow Rate**: An estimate of the current water flow.
* **Parameter 1 & 2**: Additional metrics from the device. The exact meaning is unknown.

**IMPORTANT: Customizing Data Parsing**

The Bluetooth communication for this device is not publicly documented. The sensor values are based on reverse-engineering the communication logs. You will likely need to adjust the parsing logic to match your specific device's data.

The core parsing logic is located in the file: `custom_components/cs_meter_soft/api.py` within the `_notification_callback` method.

To customize:
1.  Enable `debug` logging for the component in your `configuration.yaml` to see the raw data coming from the device:
    ```yaml
    logger:
      default: info
      logs:
        custom_components.cs_meter_soft: debug
    ```
2.  Open the `api.py` file.
3.  Look for the `_notification_callback` function. You will see sections for parsing data packets that start with `75-75-00`.
4.  Observe the values in your device's official mobile app and compare them to the debug logs in Home Assistant.
5.  Adjust the byte indices and calculations in `api.py` to correctly interpret the data for sensors like "Remaining Capacity", "Flow Rate", etc.

For example, `capacity = int.from_bytes(data[6:8], byteorder='little')` reads two bytes starting at the 7th position to determine the capacity. If you find the capacity is actually in a different position, you would change `data[6:8]` to the correct slice.

## Disclaimer

This is an unofficial integration and is not affiliated with the manufacturer of the "CS_Meter_Soft" device. Use at your own risk.
