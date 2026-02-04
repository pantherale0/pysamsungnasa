"""Error mapping for NASA devices."""

ERROR_CODES = {
    0: None,
    101: "hydro_outdoor_comm_error",
    120: "room_temp_sensor_zone2_error",
    121: "room_temp_sensor_zone1_error",
    122: "eva_inlet_temp_sensor_error",
    123: "eva_outlet_temp_sensor_error",
    162: "eeprom_error",
    198: "thermal_fuse_error",
    604: "hydro_wired_remote_comm_error",
    653: "wired_remote_temp_sensor_error",
    654: "wired_remote_eeprom_error",
    897: "water_tank_sensor_error",
    899: "water_outlet_temp_zone1_error",
    900: "water_outlet_temp_zone2_error",
    901: "water_inlet_temp_sensor_error",
    902: "water_outlet_temp_sensor_error",
    903: "backup_heater_temp_sensor_error",
    904: "dhw_tank_temp_sensor_error",
    906: "refrigerant_inlet_temp_sensor_error",
    907: "pipe_rupture_protection_error",
    908: "freeze_prevention_error_recoverable",
    909: "freeze_prevention_error_fatal",
    910: "water_outlet_sensor_detached",
    911: "flow_switch_error",
    912: "flow_rate_error",
    913: "flow_switch_fatal_error",
    914: "thermostat_connection_error",
    915: "dc_fan_error",
    916: "mixing_valve_sensor_error",
    917: "water_tank_config_error",
    919: "disinfection_temp_error",
    920: "fsv_sd_card_error",
    973: "water_pressure_sensor_error",
}


def get_error_code(code):
    """Retrieve the error description for a given error code."""
    return ERROR_CODES.get(code, f"E{str(code)}")
