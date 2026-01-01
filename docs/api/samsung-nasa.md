# API Reference

Core API classes and methods for pysamsungnasa.

## SamsungNasa

Main entry point for the NASA protocol.

```python
from pysamsungnasa import SamsungNasa

nasa = SamsungNasa(
    host: str,
    port: int,
    config: dict,
    new_device_event_handler: Callable | None = None,
    disconnect_event_handler: Callable | None = None,
)
```

### Properties

#### `config: NasaConfig`
The active configuration object.

#### `client: NasaClient`
Low-level TCP client.

#### `devices: dict[str, NasaDevice]`
Dictionary of all devices by address.

#### `parser: NasaPacketParser`
Message parser instance.

### Methods

#### `async start()`
Connect to the NASA network and start listening.

```python
await nasa.start()
```

#### `async stop()`
Disconnect from the NASA network.

```python
await nasa.stop()
```

#### `async send_message(destination, request_type, messages)`
Send a raw message to a device.

```python
from pysamsungnasa.protocol.factory import SendMessage
from pysamsungnasa.protocol.enum import DataType

await nasa.send_message(
    destination="200020",
    request_type=DataType.REQUEST,
    messages=[SendMessage(0x4000, b'\x01')]
)
```

## NasaDevice

Base class for all devices.

### Properties

#### `address: str`
Device network address (e.g., "100000").

#### `device_type: AddressClass`
Type of device (Enum).

#### `attributes: dict[int, BaseMessage]`
All received message attributes.

#### `last_packet_time: datetime | None`
Timestamp of last update.

#### `config: NasaConfig`
Configuration object.

#### `fsv_config: dict`
FSV (Feature/Setting/Value) configuration.

### Methods

#### `add_device_callback(callback: Callable)`
Register a callback for device updates.

```python
def on_update(device):
    print(f"Device {device.address} updated")

device.add_device_callback(on_update)
```

#### `remove_device_callback(callback: Callable)`
Unregister a callback.

#### `add_packet_callback(message_number: int, callback: Callable)`
Register a callback for a specific message type.

```python
def on_temp(device, **kwargs):
    print(f"Temperature: {kwargs['packet'].VALUE}")

device.add_packet_callback(0x4203, on_temp)
```

#### `remove_packet_callback(message_number: int, callback: Callable)`
Unregister a message callback.

#### `async get_configuration()`
Request device FSV configuration.

```python
await device.get_configuration()
```

#### `handle_packet(**kwargs)`
Internal method called when device receives a packet.

## OutdoorNasaDevice

Subclass for outdoor units (typically address 100000).

### Additional Properties

#### `outdoor_temperature: float | None`
Current outdoor air temperature (°C).

#### `power_consumption: float | None`
Current power consumption (W).

#### `power_current: float | None`
Current draw (A).

#### `power_produced: float | None`
Power produced (W).

#### `power_generated_last_minute: float | None`
Energy generated in last minute (Wh).

#### `cumulative_energy: float | None`
Total cumulative energy (kWh).

#### `heatpump_voltage: float | None`
Operating voltage (V).

#### `compressor_frequency: float | None`
Compressor speed (Hz).

#### `fan_speed: float | None`
Fan speed (RPM).

#### `cop_rating: float | None`
Coefficient of Performance (efficiency rating).

#### `water_outlet_temperature: float | None`
Water outlet temperature (°C).

## IndoorNasaDevice

Subclass for indoor units (typically addresses 200020+).

### Additional Properties

#### `climate_controller: ClimateController | None`
Climate control interface.

#### `dhw_controller: DhwController | None`
Domestic hot water control interface.

## ClimateController

Controls indoor heating/cooling.

```python
@dataclass
class ClimateController:
    address: str
    power: Optional[bool]
    current_mode: Optional[str]
    real_operation_mode: Optional[str]
    f_current_temperature: Optional[float]
    f_target_temperature: Optional[float]
    current_humidity: Optional[int]
    current_fan_mode: Optional[str]
    current_fan_speed: Optional[int]
    water_outlet_current_temperature: Optional[float]
    water_law_target_temperature: Optional[float]
    zone_1_status: Optional[bool]
    zone_2_status: Optional[bool]
```

### Methods

#### `async turn_on()`
Enable climate control.

#### `async turn_off()`
Disable climate control.

#### `async set_operation_mode(mode: str)`
Set operation mode (cool, heat, dry, fan, auto).

#### `async set_target_temperature(temperature: float)`
Set target temperature.

#### `async set_fan_speed(speed: int)`
Set fan speed (1-4).

#### `async set_air_swing(mode: str)`
Set air swing direction.

## DhwController

Controls domestic hot water heating.

```python
@dataclass
class DhwController:
    address: str
    power: Optional[bool]
    operation_mode: Optional[str]
    target_temperature: Optional[float]
    current_temperature: Optional[float]
    reference_temp_source: Optional[str]
    outdoor_operation_status: Optional[str]
    outdoor_operation_mode: Optional[str]
    dhw_enable_status: Optional[bool]
```

### Methods

#### `async turn_on()`
Enable DHW.

#### `async turn_off()`
Disable DHW.

#### `async set_target_temperature(temperature: float)`
Set target temperature.

#### `async set_operation_mode(mode: str)`
Set DHW operation mode.

## NasaConfig

Configuration dataclass.

```python
@dataclass
class NasaConfig:
    client_address: int = 1
    device_dump_only: bool = False
    device_pnp: bool = False
    device_addresses: list[str] = field(default_factory=list)
    max_buffer_size: int = 262144
    log_all_messages: bool = False
    devices_to_log: list[str] = field(default_factory=list)
    log_buffer_messages: bool = False
    enable_read_retries: bool = True
    read_retry_max_attempts: int = 3
    read_retry_interval: float = 1.0
    read_retry_backoff_factor: float = 1.1
    enable_write_retries: bool = True
    write_retry_max_attempts: int = 3
    write_retry_interval: float = 1.0
    write_retry_backoff_factor: float = 1.1
```

## NasaClient

Low-level TCP client (rarely used directly).

### Properties

#### `is_connected: bool`
Connection status.

### Methods

#### `async connect()`
Establish TCP connection.

#### `async disconnect()`
Close TCP connection.

## Enumerations

### AddressClass

Device type enumeration:

```python
from pysamsungnasa.protocol.enum import AddressClass

AddressClass.OUTDOOR          # 0x10
AddressClass.HTU              # 0x11
AddressClass.INDOOR           # 0x20
AddressClass.ERV              # 0x30
AddressClass.DIFFUSER         # 0x35
AddressClass.MCU              # 0x38
AddressClass.RMC              # 0x40
AddressClass.WIRED_REMOTE     # 0x50
AddressClass.PIM              # 0x58
```

### DataType

Message type enumeration:

```python
from pysamsungnasa.protocol.enum import DataType

DataType.READ          # 0x01
DataType.WRITE         # 0x02
DataType.REQUEST       # 0x03
DataType.NOTIFICATION  # 0x04
DataType.RESPONSE      # 0x05
DataType.ACK           # 0x06
DataType.NACK          # 0x07
```

### InOperationMode

Indoor operation modes:

```python
from pysamsungnasa.protocol.enum import InOperationMode

InOperationMode.AUTO
InOperationMode.COOL
InOperationMode.DRY
InOperationMode.FAN
InOperationMode.HEAT
```

## Exceptions

### ConnectionError
Raised when connection to NASA device fails.

### TimeoutError
Raised when waiting for a response times out.

## Type Hints

All methods use proper type hints for IDE support:

```python
# These are properly typed
nasa: SamsungNasa
device: NasaDevice
cc: ClimateController
config: NasaConfig
```

## Next Steps

- Check specific modules:
  - [Samsung NASA](samsung-nasa.md)
  - [NASA Client](nasa-client.md)
  - [NASA Device](nasa-device.md)
  - [Controllers](controllers.md)
  - [Configuration](configuration.md)
- Read [Basic Usage](../user-guide/basic-usage.md)
- Explore [Examples](../examples.md)
