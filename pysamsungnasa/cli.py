"""Interactive CLI for Samsung NASA."""

import asyncio
import logging

import aioconsole

from .nasa import SamsungNasa
from .device import NasaDevice
from .protocol.enum import AddressClass

_LOGGER = logging.getLogger(__name__)


async def follow_logs():
    """Follow logs."""

    def log_handler(record: logging.LogRecord):
        print(f"{record.levelname}: {record.getMessage()}")

    logger = logging.getLogger("pysamsungnasa")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.emit = log_handler
    logger.addHandler(handler)

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        logger.removeHandler(handler)


def print_device_header(device: NasaDevice):
    """Print device header."""
    print(f"Device {device.address}:")
    print(f"  Last seen: {device.last_packet_time}")
    print(f"  Address: {device.address}")
    print(f"  Device Type: {device.device_type}")
    print(f"  Config: {device.config}")
    print(f"  Total attributes: {len(device.attributes)}")
    print(f"  FSV Config: {device.fsv_config}")
    if device.device_type == AddressClass.INDOOR:
        print(f"  DHW Controller: {'Yes' if device.dhw_controller else 'No'}")
        print(f"  Climate Controller: {'Yes' if device.climate_controller else 'No'}")
        print(
            f"  Climate Controller mode: {device.climate_controller.current_mode if device.climate_controller else 'N/A'}"
        )
        print(
            f"  Climate Controller target temp: {device.climate_controller.target_temperature if device.climate_controller else 'N/A'}"
        )


async def print_logs():
    """Print last 20 lines of logs."""

    try:
        # Read nasa.log to get last 20 lines
        with open("nasa.log", "r") as f:
            lines = f.readlines()[-20:]
        for line in lines:
            print(line.strip())
    except Exception as e:
        print(f"Error reading nasa.log: {e}")


async def interactive_cli(nasa: SamsungNasa):
    """Interactive CLI."""
    print("Samsung NASA Interactive CLI. Type 'help' for a list of commands.")
    while True:
        try:
            command_str = await aioconsole.ainput("> ")
            if not command_str:
                continue

            parts = command_str.strip().split()
            command = parts[0].lower()

            if command == "quit":
                break
            elif command == "help":
                print("Commands:")
                print("  read <device_address> <message_id_hex>")
                print("  write <device_address> <message_id_hex> <value_hex>")
                print("  device <device_address> <message_id_hex>")
                print("  climate <device_address> <dhw/heat>")
                print("  config set <key> <value>")
                print("  config read <key>")
                print("  logger follow")
                print("  quit")
                continue
            elif command in ("read", "write") and len(parts) >= 3:
                device_id = parts[1]
                try:
                    message_id = int(parts[2], 16)
                except ValueError:
                    print(f"Invalid message_id: {parts[2]}")
                    continue

                if command == "read":
                    if len(parts) != 3:
                        print("Usage: read <device_id> <message_id_hex>")
                        continue
                    print(f"Reading from {device_id}, message {hex(message_id)}")
                    response = await nasa.client.nasa_read([message_id], device_id)
                    print(f"Response: {response}")

                elif command == "write":
                    if len(parts) != 4:
                        print("Usage: write <device_id> <message_id_hex> <value_hex>")
                        continue
                    value = parts[3]
                    print(f"Writing to {device_id}, message {hex(message_id)}, value {value}")
                    # Assuming nasa_write needs a specific data_type, using default for now
                    from .protocol.enum import DataType

                    response = await nasa.client.nasa_write(message_id, value, device_id, DataType.WRITE)
                    print(f"Response: {response}")
            elif command == "device":
                if len(parts) == 1:
                    # Print all devices
                    for device in nasa.devices.values():
                        print_device_header(device)
                elif len(parts) == 2:
                    device_id = parts[1]
                    if device_id in nasa.devices:
                        device = nasa.devices[device_id]
                        print_device_header(device)
                        for k, v in device.attributes.items():
                            print(f"  {k}: {v.as_dict}")
                    else:
                        print(f"Device {device_id} not found")
                elif len(parts) == 3:
                    device_id = parts[1]
                    # Convert str to decimal (0x4097 -> 16503)
                    message_id = int(parts[2], 16)
                    if device_id in nasa.devices:
                        device = nasa.devices[device_id]
                        print_device_header(device)
                        if message_id in device.attributes:
                            print(f"  {message_id}: {device.attributes[message_id].as_dict}")
                        else:
                            print(f"  {message_id} not found")
                    else:
                        print(f"Device {device_id} not found")
                else:
                    print("Usage: device [<device_address> [<message_id_hex>]]")
                    print("  Without arguments, lists all devices.")
                    print("  With device_address, lists all attributes of the device.")
                    print("  With device_address and message_id, prints the value of the attribute.")
            elif command == "config":
                if len(parts) == 2 and parts[1] == "set":
                    if len(parts) == 4:
                        key = parts[2]
                        value = parts[3]
                        nasa.config.__setattr__(key, value)
                        print(f"Config set: {key} = {value}")
                    else:
                        print("Usage: config set <key> <value>")
                elif len(parts) == 2 and parts[1] == "read":
                    if len(parts) == 3:
                        key = parts[2]
                        print(f"Config read: {key} = {getattr(nasa.config, key)}")
                    else:
                        print("Usage: config read <key>")
                else:
                    print("Usage: config set <key> <value> or config read <key>")
            elif command == "logger" and len(parts) == 2 and parts[1] == "follow":
                await follow_logs()
            elif command == "logger" and len(parts) == 2 and parts[1] == "print":
                await print_logs()
            elif command == "quit":
                break
            elif command == "climate":
                # Show and control climate information (DHW/Heating)
                if len(parts) < 3 or len(parts) > 4:
                    print("Usage: climate <device_address> <dhw/heat> [<on/off>]")
                    continue
                device_id = parts[1]
                climate_type = parts[2]
                command = parts[3] if len(parts) > 3 else None
                if device_id not in nasa.devices:
                    print(f"Device {device_id} not found")
                    continue
                device = nasa.devices[device_id]
                if climate_type == "dhw":
                    if not device.dhw_controller:
                        print(f"Device {device_id} has no DHW controller")
                        continue
                    print("DHW Climate Control:")
                    print(f"  Current Temp: {device.dhw_controller.current_temperature}")
                    print(f"  Target Temp: {device.dhw_controller.target_temperature}")
                    print(f"  Mode: {device.dhw_controller.operation_mode}")
                    print(f"  Fan Speed: {device.dhw_controller.power}")
                    if command is not None:
                        if command == "on":
                            await device.dhw_controller.turn_on()
                            print("DHW turned on")
                        elif command == "off":
                            await device.dhw_controller.turn_off()
                            print("DHW turned off")
                        else:
                            print(f"Unknown command for DHW: {command}")
                elif climate_type == "heat":
                    if not device.climate_controller:
                        print(f"Device {device_id} has no Heating controller")
                        continue
                    print("Heating Climate Control:")
                    print(f"  Current Temp: {device.climate_controller.current_temperature}")
                    print(f"  Target Temp: {device.climate_controller.target_temperature}")
                    print(f"  Mode: {device.climate_controller.current_mode}")
                    print(f"  Fan Speed: {device.climate_controller.power}")
                    if command is not None:
                        if command == "on":
                            await device.climate_controller.turn_on()
                            print("Heating turned on")
                        elif command == "off":
                            await device.climate_controller.turn_off()
                            print("Heating turned off")
                        else:
                            print(f"Unknown command for Heating: {command}")
                else:
                    print(f"Unknown climate type: {climate_type}")
            else:
                print(f"Unknown command: {command_str}")

        except (KeyboardInterrupt, asyncio.CancelledError):
            break
        except Exception as e:
            _LOGGER.error("Error in CLI: %s", e)
