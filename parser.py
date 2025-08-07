"""Parser for the Bluetooth Water Softener BLE data."""
import struct
from typing import Any, Dict

class WaterSoftenerBluetoothDeviceData:
    """Data parser for the water softener."""

    def __init__(self):
        """Initialize the data parser."""
        self._data = {}

    def parse_data(self, data: bytes) -> Dict[str, Any]:
        """Parse the raw BLE data."""
        if len(data) < 2:
            return None

        header = data[:2]

        if header == b'tt':
            self._parse_tt_packet(data)
        elif header == b'uu':
            self._parse_uu_packet(data)
        elif header == b'vv':
            self._parse_vv_packet(data)
        elif header == b'ww':
        	self._parse_ww_packet(data)

        return self._data

    @property
    def data(self) -> Dict[str, Any]:
        """Return the parsed data."""
        return self._data

    def _parse_tt_packet(self, data: bytes):
        """Parse the 'tt' packet for firmware version."""
        # (0x) 74-74-00-01-00-04-38-80-04-03-00-36-00-00-71-47-78-00
        if len(data) >= 7:
            major = data[5]
            minor = data[6]
            self._data["firmware_version"] = f"C{major}.{minor}"

    def _parse_uu_packet(self, data: bytes):
        """Parse the 'uu' packet for sensor data."""
        # (0x) 75-75-00-01-1C-01-7C-00-07-0A-ED-00-5F-01-D9-08-02-00-00-39
        # (0x) 75-75-01-05-03-00-00-00-00-01-00-00-00-01-02-10-18-0A-00-3A
        if len(data) < 20:
            return

        packet_type = data[2]

        if packet_type == 0: # Main dashboard data
            try:
                flow, remaining, today_usage, peak_flow, hardness, regen_hr, regen_min = struct.unpack(
                    '>xxxxHhHhBbbxx', data[2:20]
                )
                self._data["current_water_flow"] = flow / 100.0
                self._data["soft_water_remaining"] = remaining
                self._data["treated_water_usage_today"] = today_usage
                self._data["peak_flow_today"] = peak_flow / 100.0
                self._data["water_hardness"] = hardness
                self._data["regeneration_time"] = f"{regen_hr:02d}:{regen_min:02d}"
            except struct.error:
                pass # Ignore malformed packets
        
        elif packet_type == 1: # Advanced settings
        	try:
        		days_until_regen, regen_override, reserve, resin_grains, soak_hr = struct.unpack(
        			'>xxBBHHIx', data[2:14] # Simplified, needs verification
        		)
        		self._data["days_until_regeneration"] = days_until_regen
        		self._data["regeneration_day_override"] = regen_override
        		self._data["reserve_capacity"] = reserve
        		self._data["resin_grains_capacity"] = resin_grains
        		self._data["brine_soak_duration"] = soak_hr
        	except struct.error:
        		pass

    def _parse_vv_packet(self, data: bytes):
        """Parse the 'vv' packet for settings data."""
        # (0x) 76-76-01-0A-3C-0A-0A-00-00-00-00-00-00-00-00-00-00-00-00-43
        if len(data) >= 5 and data[2:4] == b'\x01\x0A':
            self._data["brine_tank_level"] = data[4]

    def _parse_ww_packet(self, data: bytes):
        """Parse the 'ww' packet for history data."""
        # (0x) 77-77-00-00-05-02-91-DD-01-90-DD-01-19-01-19-00-00-00-43
        if len(data) >= 16:
            try:
                total_gallons, total_gallons_reset, total_regens, total_regens_reset = struct.unpack(
                    '>xxxxIIHH', data[2:18]
                )
                self._data["total_gallons_treated"] = total_gallons
                self._data["total_gallons_treated_since_reset"] = total_gallons_reset
                self._data["total_regenerations"] = total_regens
                self._data["total_regenerations_since_last_reset"] = total_regens_reset
            except struct.error:
                pass
