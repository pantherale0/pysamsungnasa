# Message Numbers Reference

A comprehensive overview of NASA protocol message numbers. Complete documentation for all message numbers is not available, but the following information has been collected from various sources.

## Message Number Overview

The message number field (bytes 13-14) determines both the type and size of the message payload:

| Type | Enum Value | Payload Size |
|------|-----------|--------------|
| Byte | 0 | 1 byte |
| Variable | 1 | 2 bytes |
| LongVariable | 2 | 4 bytes |
| Structure | 3 | All remaining bytes (minus 3 end bytes) |

## Information Sources

- **NASA.ptc** - Samsung SNET Pro service software (v1.5.3 available [here](https://s3.amazonaws.com/samsung-files/Tech_Files/SNET+Pro+and+SNET+Pro+2+Service+Software/Snet+Pro+v1.5.3.zip))
- **NasaConst.java** - WiFiKit source code (from WiFiKit_Source.zip on [Samsung Open Source](https://opensource.samsung.com/uploadList?menuItem=home_appliances&classification1=airconditioners&classification2=control_solutions))
- **Active Research** - Messages discovered from live system monitoring

## Message Type Prefixes

Messages are typically prefixed based on their scope:

- **ENUM_** - Enumeration type (fixed set of values)
- **VAR_** - Variable/measurement (16-bit)
- **LVAR_** - Long variable (32-bit)
- **STR_** - Structure type
- **AD_** - Address-related (device addressing)
- **OUT_** - Outdoor unit
- **IN_** - Indoor unit
- **NM_** - Network management
- **IM_** - Indoor management
- **OD_** - Outdoor device

## Common Message Categories

### Error Codes (0x0202-0x0206)
- 0x0202: Error Code 1
- 0x0203: Error Code 2
- 0x0204: Error Code 3
- 0x0205: Error Code 4
- 0x0206: Error Code 5

### Indoor Unit Messages (0x4000+)
Indoor units report operating modes, temperatures, and settings.

**Power & Mode:**
- 0x4000: Power On/Off (values: 0=Off, 1=On, 2=On)
- 0x4001: Operation Mode (0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat, 21=Cool Storage, 24=Hot Water)
- 0x4002: Real Operation Mode (actual current mode)

**Temperature:**
- 0x4201: Set Temperature (divided by 10)
- 0x4203: Room Temperature (divided by 10)
- 0x4205: Eva In Temperature (divided by 10)
- 0x4206: Eva Out Temperature (divided by 10)
- 0x420B: Discharge Temperature (divided by 10)

**Capacity:**
- 0x4211: Capacity Request
- 0x4212: Absolute Capacity

**Fan Control:**
- 0x4006: Fan Speed
- 0x4007: Fan Mode Real
- 0x4008: Fan Ventilation Mode

**Air Flow Control:**
- 0x4011: Up/Down Air Flow (Louver HL Swing)
- 0x407E: Left/Right Air Flow (Louver LR Swing)

### Outdoor Unit Messages (0x8000+)
Outdoor units report operational status, temperatures, pressures, and component states.

**Operation Status:**
- 0x8001: Operation Status (Stop, Safety, Normal, Balance, Recovery, Deice, Compdown, Prohibit, etc.)
- 0x8003: Cooling/Heating Mode (1=Cool, 2=Heat, 3=Cool Main, 4=Heat Main)

**Compressor Control:**
- 0x8010: Compressor 1 Status
- 0x8011: Compressor 2 Status
- 0x8012: Compressor 3 Status
- 0x8236-0x8238: Compressor 1 Frequency (Order, Target, Current)
- 0x8274-0x8276: Compressor 2 Frequency

**Temperatures:**
- 0x8204: Outdoor Temperature (divided by 10)
- 0x820A: Discharge Temperature 1 (divided by 10)
- 0x820C: Discharge Temperature 2 (divided by 10)
- 0x8218: Main Heat Exchanger Outlet (divided by 10)
- 0x821A: Suction Temperature (divided by 10)

**Pressures:**
- 0x8206: High Pressure (divided by 10, unit: kgf/cm²)
- 0x8208: Low Pressure (divided by 10, unit: kgf/cm²)
- 0x82B8: Medium Pressure

**Valves & Components:**
- 0x8017-0x8018: Hot Gas 1/2
- 0x8019: Liquid Bypass Valve
- 0x801A: 4-Way Valve
- 0x8026: Water Valve
- 0x8027: Pump Out Valve

**EEV (Electronic Expansion Valve):**
- 0x8229-0x822D: Main EEV 1-5
- 0x822E: EVI EEV

**Power Consumption:**
- 0x8411: Instantaneous Power (single unit)
- 0x8413: Sum of Modules Instantaneous Power
- 0x8414: Cumulative Power Consumption
- 0x8415: Total (Indoor + Outdoor) Instantaneous Power

**Running Time:**
- 0x8405: Compressor 1 Running Time (hours)
- 0x8406: Compressor 2 Running Time

### Network Management (0x2000+)
Network configuration and device addressing messages.

- 0x2003: Addressing
- 0x200F: Network Layer
- 0x2010: Tracking Result

## Data Type Notes

### Temperature Values
Most temperature values are signed 16-bit integers divided by 10, resulting in 0.1°C resolution.
- Formula: `(raw_value / 10)` = temperature in °C
- Range typically: -41°C to +150°C

### Pressure Values
Pressures are typically divided by 10 with unit kgf/cm².
- Formula: `(raw_value / 10)` = pressure in kgf/cm²

### Power Values
Power measurements are often divided by 8.6 to get kW.
- Example: 0x4211 (Capacity Request) = `(value / 8.6)` kW
- Cumulative energy in Wh: divide by 1000 for kWh

### Capacity Values
Operating capacity is often expressed as a percentage or in relative units.

## Special Cases

### Water Heater (DHW)
- 0x4065: Power (0=Off, 1=On)
- 0x4066: Mode (0=Eco, 1=Standard, 2=Power, 3=Force)
- 0x4235: DHW Target Temperature (divided by 10)
- 0x4237: DHW Current Temperature (divided by 10)

### Ventilation (ERV)
- 0x4003: Operation Mode
- 0x4004: Operation Mode Details
- 0x4008: Fan Speed

### Hydro System (Water Heating/Cooling)
Multiple temperature and valve control messages for water-based systems.

## Incomplete Documentation

Many message numbers lack complete documentation (marked with `??` in the source). If you encounter these in your monitoring, please document them and consider contributing to the project.

## Version Notes

The latest S-Net protocol version implemented in pysamsungnasa may include additional message types not yet documented in public sources. The NASA.ptc file and MyEHS wiki are good references for discovering new message numbers.

## Complete Message Number Table

Below is a comprehensive reference of NASA message numbers extracted from NASA.ptc and NasaConst.java source files. Note that many message numbers lack complete documentation (marked with `??` in the original sources).

### System Control & Addressing (0x0000-0x0217)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Remarks |
|-----|---|---|---|---|
| 0x0000 | NASA_IM_MASTER_NOTIFY | | Master notification | |
| 0x0004 | NASA_INSPECTION_MODE | | Inspection mode | |
| 0x0007 | NASA_GATHER_INFORMATION | | Gather information | |
| 0x0008 | NASA_GATHER_INFORMATION_COUNT | | Information count | |
| 0x000A | NASA_ENABLEDOWNLOAD | | Enable download mode | |
| 0x000D | NASA_DETECTION_TYPE | | Detection type | |
| 0x000E | NASA_PEAK_LEVEL | | Peak level | |
| 0x000F | NASA_PEAK_MODE | | Peak mode | |
| 0x0010 | NASA_PEAK_CONTROL_PERIOD | | Peak control period | |
| 0x0011 | NASA_POWER_MANUFACTURE | | Power manufacturer | |
| 0x0012-0x0019 | NASA_POWER_CHANNEL_TYPE | | Power channel type (1-8) | |
| 0x001A-0x0021 | NASA_POWER_CHANNEL_USED | | Power channel used (1-8) | |
| 0x0023 | NASA_STANDBY_MODE | | Standby mode | |
| 0x0025 | ENUM_AD_MULTI_TENANT_NO | | WiFi Kit multi tenant number | |
| 0x0202 | VAR_AD_ERROR_CODE1 | NASA_ERROR_CODE1 | Error code | |
| 0x0203 | NASA_ERROR_CODE2 | | Error code 2 | |
| 0x0204-0x0206 | NASA_ERROR_CODE[3-5] | | Error codes 3-5 | |
| 0x0207 | VAR_AD_INSTALL_NUMBER_INDOOR | NASA_OUTDOOR_INDOORCOUNT | Number of indoor units | |
| 0x0208 | NASA_OUTDOOR_ERVCOUNT | | Number of ERV units | |
| 0x0209 | NASA_OUTDOOR_EHSCOUNT | | Number of EHS units | |
| 0x0210 | NASA_NET_ADDRESS | | Network address | |
| 0x0211 | VAR_AD_INSTALL_NUMBER_MCU | NASA_OUTDOOR_MCUCOUNT | Number of MCUs | |
| 0x0213 | NASA_DEMAND_SYNC_TIME | | Demand sync time | |
| 0x0214 | NASA_PEAK_TARGET_DEMAND | | Peak target demand | |
| 0x0217 | NASA_PNP_NET_ADDRESS | | PnP network address | PnP only |

### Addressing & Remote Control (0x0401-0x0448)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Remarks |
|-----|---|---|---|---|
| 0x0401 | LVAR_AD_ADDRESS_MAIN | NASA_CONFIRM_ADDRESS | Main address confirmation | |
| 0x0402 | LVAR_AD_ADDRESS_RMC | NASA_RMCADDRESS | Remote controller address | LogicalAnd 0xFF |
| 0x0403 | NASA_RANDOM_ADDRESS | | Random address | |
| 0x0406 | NASA_ALL_POWER_CONSUMPTION_SET | | Total instantaneous power | |
| 0x0407 | NASA_ALL_POWER_CONSUMPTION_CUMULATIVE | | Total cumulative power | |
| 0x0408 | LVAR_AD_ADDRESS_SETUP | NASA_SETUP_ADDRESS | Setup address | |
| 0x0409 | LVAR_AD_INSTALL_LEVEL_ALL | NASA_ALL_REMOTE_LEVEL | All remote levels | |
| 0x040A | LVAR_AD_INSTALL_LEVEL_OPERATION_POWER | NASA_LEVEL_POWER | Remote level power control | |
| 0x040B | LVAR_AD_INSTALL_LEVEL_OPERATION_MODE | NASA_LEVEL_OPMODE | Remote level operation mode | LogicalAnd 0xFF |
| 0x040C | LVAR_AD_INSTALL_LEVEL_FAN_MODE | NASA_LEVEL_FANSPEED | Remote level fan speed | |
| 0x040D | LVAR_AD_INSTALL_LEVEL_FAN_DIRECTION | NASA_LEVEL_AIRSWING | Remote level air swing | |
| 0x040E | LVAR_AD_INSTALL_LEVEL_TEMP_TARGET | NASA_LEVEL_SETTEMP | Remote level set temperature | |
| 0x040F | LVAR_AD_INSTALL_LEVEL_KEEP_INDIVIDUAL_CONTROL | NASA_LEVEL_KEEP_ALTERNATIVE_MODE | Keep alternative mode | |
| 0x0410 | LVAR_AD_INSTALL_LEVEL_OPERATION_MODE_ONLY | NASA_LEVEL_OPMODE_LIMIT | Operation mode limit | |
| 0x0411 | LVAR_AD_INSTALL_LEVEL_COOL_MODE_UPPER | NASA_LEVEL_COOL_HIGH_TEMP_LIMIT | Cool mode upper limit | (value & 0xFFFF0000u) >> 16) / 10.0 |
| 0x0412 | LVAR_AD_INSTALL_LEVEL_COOL_MODE_LOWER | NASA_LEVEL_COOL_LOW_TEMP_LIMIT | Cool mode lower limit | (value & 0xFFFF0000u) >> 16) / 10.0 |
| 0x0413 | LVAR_AD_INSTALL_LEVEL_HEAT_MODE_UPPER | NASA_LEVEL_HEAT_HIGH_TEMP_LIMIT | Heat mode upper limit | (value & 0xFFFF0000u) >> 16) / 10.0 |
| 0x0414 | LVAR_AD_INSTALL_LEVEL_HEAT_MODE_LOWER | NASA_LEVEL_HEAT_LOW_TEMP_LIMIT | Heat mode lower limit | (value & 0xFFFF0000u) >> 16) / 10.0 |
| 0x0415-0x0419 | LVAR_AD_INSTALL_LEVEL_* | NASA_*_ADDRESS | Various address levels | |
| 0x041C-0x0423 | NASA_POWER_CHANNEL[1-8]_ELECTRIC_VALUE | | Power channel values | |
| 0x0434-0x0445 | NASA_PEAK_* | | Peak control messages | |
| 0x0448 | LVAR_AD_MCU_PORT_SETUP | | MCU port setup | |

### Device Configuration (0x0600-0x061F)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Remarks |
|-----|---|---|---|---|
| 0x0600 | STR_AD_OPTION_BASIC | NASA_PRODUCT_OPTION | Product option | |
| 0x0601 | STR_AD_OPTION_INSTALL | NASA_INSTALL_OPTION | Installation option | |
| 0x0602 | STR_AD_OPTION_INSTALL_2 | NASA_INSTALLOPTION2 | Installation option 2 | |
| 0x0603 | STR_AD_OPTION_CYCLE | NASA_CYCLEOPTION | Cycle option | |
| 0x0604 | NASA_PBAOPTION | | PBA option | |
| 0x0605 | STR_AD_INFO_EQUIP_POSITION | NASA_NAME | Equipment position/name | |
| 0x0607 | STR_AD_ID_SERIAL_NUMBER | NASA_SERIAL_NO | Serial number | OutdoorTableSerialNumber |
| 0x0608 | STR_AD_DBCODE_MICOM_MAIN | NASA_MICOM_CODE | Main MICOM DB code | OutdoorUnitMainDBCodeVersion |
| 0x060C | STR_AD_DBCODE_EEPROM | NASA_EEPROM_CODE | EEPROM DB code | OutdoorTableEEPROMDBCodeVersion |
| 0x0613 | NASA_SIMPIM_SYNC_DATETIME | | SimplePIM sync datetime | |
| 0x0619 | NASA_SIMPIM_PASSWORD | | SimplePIM password | |
| 0x061A | STR_AD_PRODUCT_MODEL_NAME | NASA_PRODUCT_MODEL_NAME | Product model name | |
| 0x061C | STR_AD_PRODUCT_MAC_ADDRESS | | WiFi Kit MAC address | |
| 0x061F | STR_AD_ID_MODEL_NAME | | Model name | |

### Network Management (0x2000-0x2018)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Remarks |
|-----|---|---|---|---|
| 0x2000 | NASA_IM_MASTER | | IM master notification | |
| 0x2001 | NASA_CHANGE_POLAR | | Change polarity | |
| 0x2002 | NASA_ADDRESSING_ASSIGN_CONFIRM_ADDRESS | | Addressing confirmation | |
| 0x2003 | NASA_ADDRESSING | | Network addressing | |
| 0x2004 | ENUM_NM* | NASA_PNP | PnP mode | |
| 0x2006 | NASA_CHANGE_CONTROL_NETWORK_STATUS | | Change control network status | |
| 0x2007 | NASA_CHANGE_SET_NETWORK_STATUS | | Change set network status | |
| 0x2008 | NASA_CHANGE_LOCAL_NETWORK_STATUS | | Change local network status | |
| 0x2009 | NASA_CHANGE_MODULE_NETWORK_STATUS | | Change module network status | |
| 0x200A | NASA_CHANGE_ALL_NETWORK_STATUS | | Change all network status | |
| 0x200F | ENUM_NM_NETWORK_POSITINON_LAYER | NASA_LAYER | Network position layer | Enumeration type |
| 0x2010 | ENUM_NM_NETWORK_TRACKING_STATE | NASA_TRACKING_RESULT | Network tracking result | |
| 0x2017 | NASA_COMMU_MICOM_LED | | MICOM LED control | |
| 0x2018 | NASA_COMMU_MICOM_BUTTON | | MICOM button input | |

### Indoor Unit Messages - Power & Modes (0x4000-0x4010)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Values |
|-----|---|---|---|---|
| 0x4000 | ENUM_IN_OPERATION_POWER | NASA_POWER | Power on/off | 0=Off, 1=On, 2=On |
| 0x4001 | ENUM_IN_OPERATION_MODE | NASA_INDOOR_OPMODE | Operation mode | 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat, 21=Cool Storage, 24=Hot Water |
| 0x4002 | ENUM_IN_OPERATION_MODE_REAL | NASA_INDOOR_REAL_OPMODE | Real operation mode | 0=Auto, 1=Cool, 2=Dry, 3=Fan, 4=Heat, 11=Auto Cool, 12=Auto Dry, 13=Auto Fan, 14=Auto Heat, 21=Cool Storage, 24=Hot Water, 255=NULL |
| 0x4003 | ENUM_IN_OPERATION_VENT_POWER | NASA_ERV_POWER | ERV power | |
| 0x4004 | ENUM_IN_OPERATION_VENT_MODE | NASA_ERV_OPMODE | ERV operation mode | |
| 0x4006 | ENUM_IN* | NASA_FANSPEED | Fan speed | |
| 0x4007 | ENUM_IN_FAN_MODE_REAL | | Fan mode real | |
| 0x4008 | ENUM_IN_FAN_VENT_MODE | NASA_ERV_FANSPEED | ERV fan speed | |

### Indoor Unit Messages - Temperatures (0x4201-0x4248)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Unit/Notes |
|-----|---|---|---|---|
| 0x4201 | VAR_IN_TEMP_TARGET_F | NASA_SET_TEMP | Set temperature | °C / 10 |
| 0x4203 | VAR_IN_TEMP_ROOM_F | NASA_CURRENT_TEMP | Room temperature | °C / 10 |
| 0x4205 | VAR_IN_TEMP_EVA_IN_F | NASA_EVA_IN_TEMP | Indoor Eva in temperature | °C / 10 |
| 0x4206 | VAR_IN_TEMP_EVA_OUT_F | NASA_EVA_OUT_TEMP | Indoor Eva out temperature | °C / 10 |
| 0x420B | VAR_IN_TEMP_DISCHARGE | NASA_CURRENT_DISCHARGE | Discharge temperature (Duct, AHU) | °C / 10 |
| 0x4211 | VAR_IN_CAPACITY_REQUEST | NASA_INDOOR_CAPACITY | Capacity request | divided by 8.6 = kW |
| 0x4212 | VAR_IN_CAPACITY_ABSOLUTE | NASA_INDOOR_ABSOLUTE_CAPACITY | Absolute capacity | divided by 8.6 = kW |
| 0x4235 | VAR_IN_TEMP_WATER_HEATER_TARGET_F | NASA_INDOOR_DHW_SET_TEMP | DHW target temperature | °C / 10 |
| 0x4236 | VAR_IN_TEMP_WATER_IN_F | NASA_INDOOR_WATER_IN_TEMP | Water in temperature | °C / 10 |
| 0x4237 | VAR_IN_TEMP_WATER_TANK_F | NASA_INDOOR_DHW_CURRENT_TEMP | DHW tank temperature | °C / 10 |
| 0x4238 | VAR_IN_TEMP_WATER_OUT_F | NASA_INDOOR_WATER_OUT_TEMP | Water out temperature | °C / 10 |
| 0x4247 | VAR_IN_TEMP_WATER_OUTLET_TARGET_F | NASA_INDOOR_SETTEMP_WATEROUT | Water outlet target temperature | °C / 10 |

### Smart Grid Mode Control (0x4124)

| Hex | NASA.ptc Label | Description | Type | Values |
|-----|---|---|---|---|
| **0x4124** | **ENUM_IN_SG_READY_MODE_STATE** | **Enables or disables the Smart Grid Ready feature** | **Enum** | **0=Off, 1=On** |

**Smart Grid Operation Modes (Terminal Control):**

When Smart Grid is enabled (via `0x4124` set to 1), the system's operation mode is determined by the state of two physical terminals, not by this message. The modes are as follows:

| **Value** | **Hex** | **Mode Name** | **Terminal 1** | **Terminal 2** | **Behavior** |
|---|---|---|---|---|---|
| **1** | 0x01 | Forced Thermostat Off | Short (0V) | Open | All heating/cooling stops (emergency load shedding) |
| **2** | 0x02 | Normal Operation | Open | Open | System operates normally with user setpoints |
| **3** | 0x03 | Load Increase | Open | Short (0V) | Heating/DHW temps raised for pre-heating (off-peak, abundance) |
| **4** | 0x04 | Load Decrease | Short (0V) | Short (0V) | Aggressive demand response (behavior per FSV #5094) |

**Related Settings:**

When sending mode via 0x4124, the system's response is further configured by:
- **FSV #5091 (0x411C)**: Must be 1 (enabled) for mode to take effect
- **FSV #5092 (0x42DD)**: Temperature shift for heating during Mode 3/4
- **FSV #5093 (0x42DE)**: Temperature shift for DHW during Mode 3
- **FSV #5094 (0x411D)**: DHW behavior control during Mode 4

**See Also:** [Smart Grid Control Guide](../user-guide/smart-grid-control.md) for detailed configuration and code examples.

### Indoor Unit Messages - Water Heating (0x4065-0x4070)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Values |
|-----|---|---|---|---|
| 0x4065 | ENUM_IN_WATER_HEATER_POWER | NASA_DHW_POWER | Water heater power | 0=Off, 1=On |
| 0x4066 | ENUM_IN_WATER_HEATER_MODE | NASA_DHW_OPMODE | Water heater mode | 0=Eco, 1=Standard, 2=Power, 3=Force |
| 0x4067 | ENUM_IN_3WAY_VALVE | NASA_DHW_VALVE | 3-way valve | 0=Room, 1=Tank |
| 0x4068 | ENUM_IN_SOLAR_PUMP | NASA_SOLAR_PUMP | Solar pump control | |

### Outdoor Unit Messages - Status (0x8000-0x8003)

```

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Values |
|-----|---|---|---|---|
| 0x4065 | ENUM_IN_WATER_HEATER_POWER | NASA_DHW_POWER | Water heater power | 0=Off, 1=On |
| 0x4066 | ENUM_IN_WATER_HEATER_MODE | NASA_DHW_OPMODE | Water heater mode | 0=Eco, 1=Standard, 2=Power, 3=Force |
| 0x4067 | ENUM_IN_3WAY_VALVE | NASA_DHW_VALVE | 3-way valve | 0=Room, 1=Tank |
| 0x4068 | ENUM_IN_SOLAR_PUMP | NASA_SOLAR_PUMP | Solar pump control | |

### Outdoor Unit Messages - Status (0x8000-0x8003)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Values |
|-----|---|---|---|---|
| 0x8000 | ENUM_OUT_OPERATION_SERVICE_OP | | Service operation | 2=Heating test, 3=Pump out, 13=Cooling test, 14=Pump down |
| 0x8001 | ENUM_OUT_OPERATION_ODU_MODE | NASA_OUTDOOR_OPERATION_STATUS | Outdoor operation status | 0=Stop, 1=Safety, 2=Normal, 3=Balance, 4=Recovery, 5=Deice, ... (36 modes) |
| 0x8003 | ENUM_OUT_OPERATION_HEATCOOL | NASA_OUTDOOR_OPERATION_MODE | Cooling/heating mode | 1=Cool, 2=Heat, 3=Cool Main, 4=Heat Main |

### Outdoor Unit Messages - Compressor Control (0x8010-0x8027)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | |
|-----|---|---|---|---|
| 0x8010 | ENUM_OUT_LOAD_COMP1 | NASA_OUTDOOR_COMP1_STATUS | Compressor 1 on/off | |
| 0x8011 | ENUM_OUT_LOAD_COMP2 | NASA_OUTDOOR_COMP2_STATUS | Compressor 2 on/off | |
| 0x8012 | ENUM_OUT_LOAD_COMP3 | NASA_OUTDOOR_COMP3_STATUS | Compressor 3 on/off | |
| 0x8013 | ENUM_OUT_LOAD_CCH1 | NASA_OUTDOOR_CCH1_STATUS | CCH1 on/off | |
| 0x8014 | ENUM_OUT_LOAD_CCH2 | NASA_OUTDOOR_CCH2_STATUS | CCH2 on/off | |
| 0x8017 | ENUM_OUT_LOAD_HOTGAS | NASA_OUTDOOR_HOTGAS1 | Hot gas 1 on/off | |
| 0x8018 | ENUM_OUT_LOAD_HOTGAS2 | NASA_OUTDOOR_HOTGAS2 | Hot gas 2 on/off | |
| 0x8019 | ENUM_OUT_LOAD_LIQUID | NASA_OUTDOOR_LIQUID_BYPASS_VALVE | Liquid bypass valve | |
| 0x801A | ENUM_OUT_LOAD_4WAY | NASA_OUTDOOR_4WAY_VALVE | 4-way valve on/off | |
| 0x8026 | ENUM_OUT_LOAD_WATER | NASA_OUTDOOR_WATER_VALVE | 2-way water valve | |
| 0x8027 | ENUM_OUT_LOAD_PUMPOUT | NASA_OUTDOOR_PUMPOUT_VALVE | Pump out valve | |

### Outdoor Unit Messages - Temperatures (0x8204-0x82C3)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Unit/Notes |
|-----|---|---|---|---|
| 0x8204 | VAR_OUT_SENSOR_AIROUT | NASA_OUTDOOR_OUT_TEMP | Outdoor air temperature | °C / 10 |
| 0x8206 | VAR_OUT_SENSOR_HIGHPRESS | NASA_OUTDOOR_HIGH_PRESS | High pressure | kgf/cm² / 10 |
| 0x8208 | VAR_OUT_SENSOR_LOWPRESS | NASA_OUTDOOR_LOW_PRESS | Low pressure | kgf/cm² / 10 |
| 0x820A | VAR_OUT_SENSOR_DISCHARGE1 | NASA_OUTDOOR_DISCHARGE_TEMP1 | Discharge temperature 1 | °C / 10 |
| 0x820C | VAR_OUT_SENSOR_DISCHARGE2 | NASA_OUTDOOR_DISCHARGE_TEMP2 | Discharge temperature 2 | °C / 10 |
| 0x820E | VAR_OUT_SENSOR_DISCHARGE3 | NASA_OUTDOOR_DISCHARGE_TEMP3 | Discharge temperature 3 | °C / 10 |
| 0x8218 | VAR_OUT_SENSOR_CONDOUT | NASA_OUTDOOR_COND_OUT1 | Main HX outlet temperature | °C / 10 |
| 0x821A | VAR_OUT_SENSOR_SUCTION | NASA_OUTDOOR_SUCTION1_TEMP | Suction temperature | °C / 10 |
| 0x821C | VAR_OUT_SENSOR_DOUBLETUBE | NASA_OUTDOOR_DOUBLE_TUBE | Double tube (liquid pipe) | °C / 10 |
| 0x821E | VAR_OUTCD_SENSOR_EVIIN | NASA_OUTDOOR_EVI_IN | EVI inlet temperature | °C / 10 |
| 0x8220 | VAR_OUT_SENSOR_EVIOUT | NASA_OUTDOOR_EVI_OUT | EVI outlet temperature | °C / 10 |
| 0x8223 | VAR_OUT_CONTROL_TARGET_DISCHARGE | NASA_OUTDOOR_TARGET_DISCHARGE | Target discharge temperature | °C / 10 |
| 0x825E | VAR_OUT_SENSOR_TEMP_WATER | NASA_OUTDOOR_WATER_TEMP | Water temperature | °C / 10 |
| 0x8254 | VAR_OUT_SENSOR_IPM1 | NASA_OUTDOOR_IPM_TEMP1 | IPM1 temperature | °C / 10; Range: -41 to 150 |
| 0x8255 | VAR_OUT_SENSOR_IPM2 | NASA_OUTDOOR_IPM_TEMP2 | IPM2 temperature | °C / 10 |

### Outdoor Unit Messages - Compressor Frequency (0x8236-0x8276)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | |
|-----|---|---|---|---|
| 0x8236 | VAR_OUT_CONTROL_ORDER_CFREQ_COMP1 | NASA_OUTDOOR_COMP1_ORDER_HZ | Compressor 1 instruction frequency | |
| 0x8237 | VAR_OUT_CONTROL_TARGET_CFREQ_COMP1 | NASA_OUTDOOR_COMP1_TARGET_HZ | Compressor 1 target frequency | |
| 0x8238 | VAR_OUT_CONTROL_CFREQ_COMP1 | NASA_OUTDOOR_COMP1_RUN_HZ | Compressor 1 current frequency | |
| 0x8274 | VAR_OUT_CONTROL_ORDER_CFREQ_COMP2 | NASA_OUTDOOR_COMP2_ORDER_HZ | Compressor 2 instruction frequency | |
| 0x8275 | VAR_OUT_CONTROL_TARGET_CFREQ_COMP2 | NASA_OUTDOOR_COMP2_TARGET_HZ | Compressor 2 target frequency | |
| 0x8276 | VAR_OUT_CONTROL_CFREQ_COMP2 | NASA_OUTDOOR_COMP2_RUN_HZ | Compressor 2 current frequency | |

### Outdoor Unit Messages - Pressures & EEV (0x8226-0x822E)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | |
|-----|---|---|---|---|
| 0x8226 | VAR_OUT_LOAD_FANSTEP1 | NASA_OUTDOOR_FAN_STEP1 | Outdoor fan step | Min 0, Max 10000 |
| 0x8229 | VAR_OUT_LOAD_OUTEEV1 | NASA_OUTDOOR_MAINEEV1 | Main EEV 1 opening | |
| 0x822A | VAR_OUT_LOAD_OUTEEV2 | NASA_OUTDOOR_MAINEEV2 | Main EEV 2 opening | |
| 0x822B | VAR_OUT_LOAD_OUTEEV3 | NASA_OUTDOOR_MAINEEV3 | Main EEV 3 opening | |
| 0x822C | VAR_OUT_LOAD_OUTEEV4 | NASA_OUTDOOR_MAINEEV4 | Main EEV 4 opening | |
| 0x822D | VAR_OUT_LOAD_OUTEEV5 | NASA_OUTDOOR_MAINEEV5 | Main EEV 5 opening | |
| 0x822E | VAR_OUT_LOAD_EVIEEV | NASA_OUTDOOR_EVIEEV | EVI EEV opening | |
| 0x82B8 | VAR_OUT_SENSOR_MIDPRESS | NASA_OUTDOOR_MID_PRESS | Medium pressure | |

### Smart Grid & Demand Response (0x40A4-0x411D)

Control system response to grid signals for demand response, load shifting, and renewable integration.

| Hex | NASA.ptc Label | Description | Type | Range | Default |
|-----|---|---|---|---|---|
| 0x40A4 | ENUM_IN_FSV_5041 | Power Peak Control Application | Bool | 0-1 | 0 |
| 0x40A5 | ENUM_IN_FSV_5042 | Power Peak Control Forced Off Parts | Enum | 0-3 | 0 |
| 0x40A6 | ENUM_IN_FSV_5043 | Power Peak Control Input Voltage Type | Enum | 0-1 | 1 |
| 0x40A7 | ENUM_IN_FSV_5051 | Frequency Ratio Control | Bool | 0-1 | 0 |
| **0x411B** | **ENUM_IN_FSV_5081** | **PV Control Application** | **Bool** | **0-1** | **0** |
| **0x411C** | **ENUM_IN_FSV_5091** | **Smart Grid Control Application** | **Bool** | **0-1** | **0** |
| **0x411D** | **ENUM_IN_FSV_5094** | **Smart Grid DHW Mode Priority** | **Enum** | **0-1** | **0** |
| **0x42DD** | **VAR_IN_FSV_5092** | **Smart Grid Heating Temp Shift** | **Float** | **2-5°C** | **2°C** |
| **0x42DE** | **VAR_IN_FSV_5093** | **Smart Grid DHW Temp Shift** | **Float** | **2-5°C** | **5°C** |

**Smart Grid Control Summary:**

- **FSV #5091 (0x411C)**: Master enable for Smart Grid Control. When set to 1, system receives external signals (via 2 terminals or Modbus) and adjusts operation accordingly.
- **FSV #5092 (0x42DD)**: During Mode 3/4 (load increase), heating setpoints increase by this amount to store thermal energy during off-peak/abundant renewable periods.
- **FSV #5093 (0x42DE)**: During Mode 3 (load increase), DHW setpoint increases by this amount to pre-heat hot water tank during cheap/abundant power periods.
- **FSV #5094 (0x411D)**: During Mode 4 (load decrease/demand response), controls whether DHW also reduces (aggressive, value=1) or continues (comfort, value=0).

**Operation Modes** (when FSV #5091=1):

| Mode | Terminal 1 | Terminal 2 | Behavior |
|------|---|---|---|
| **1** | Short (0V) | Open | Forced thermostat off - all components stop (emergency load shedding) |
| **2** | Open | Open | Normal operation - user setpoints apply |
| **3** | Open | Short (0V) | Load increase - heating/DHW temps raised (off-peak, renewable abundance) |
| **4** | Short (0V) | Short (0V) | Load decrease - aggressive demand response, behavior controlled by FSV #5094 |

**See Also:** [Smart Grid Control Guide](../user-guide/smart-grid-control.md) for detailed configuration and examples.

### Power Consumption Monitoring (0x8411-0x8416)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Notes |
|-----|---|---|---|---|
| 0x8411 | LVAR_OUT_CONTROL_WATTMETER_1UNIT | NASA_OUTDOOR_CONTROL_WATTMETER_1UNIT | 1 outdoor unit instantaneous power | Appears ~135 seconds |
| 0x8412 | NASA_OUTDOOR_CONTROL_WATTMETER_1UNIT_ACCUM | | 1 outdoor unit cumulative power | |
| 0x8413 | LVAR_OUT_CONTROL_WATTMETER_1W_1MIN_SUM | NASA_OUTDOOR_CONTROL_WATTMETER_ALL_UNIT | All modules instantaneous power | Appears ~30 seconds |
| 0x8414 | LVAR_OUT* | NASA_OUTDOOR_CONTROL_WATTMETER_ALL_UNIT_ACCUM | All modules cumulative power | Value in Wh, divide by 1000 for kWh |
| 0x8415 | LVAR_OUT* | NASA_OUTDOOR_CONTROL_WATTMETER_TOTAL_SUM | Total (indoor+outdoor) instantaneous | Never seen in EHS data |
| 0x8416 | LVAR_OUT* | NASA_OUTDOOR_CONTROL_WATTMETER_TOTAL_SUM_ACCUM | Total (indoor+outdoor) cumulative | Never seen in EHS data |

### Running Time & Diagnostics (0x8405-0x840F)

| Hex | NASA.ptc Label | NasaConst.java Label | Description | Unit |
|-----|---|---|---|---|
| 0x8405 | LVAR_OUT_LOAD_COMP1_RUNNING_TIME | NASA_OUTDOOR_COMP1_RUNNING_TIME | Compressor 1 running time | hours |
| 0x8406 | LVAR_OUT* | NASA_OUTDOOR_COMP2_RUNNING_TIME | Compressor 2 running time | hours |
| 0x840E | NASA_OUTDOOR_COMP3_RUNNING_TIME | | Compressor 3 running time | hours |
| 0x840B | LVAR_OUT_AUTO_INSPECT_RESULT0 | | Auto inspection result 0 | |
| 0x840C | LVAR_OUT_AUTO_INSPECT_RESULT1 | | Auto inspection result 1 | |
