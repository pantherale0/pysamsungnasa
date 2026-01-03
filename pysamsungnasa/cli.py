"""Interactive CLI for Samsung NASA."""

import asyncio
import logging

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.shortcuts import CompleteStyle

from .nasa import SamsungNasa
from .device import NasaDevice, IndoorNasaDevice, OutdoorNasaDevice
from .protocol.enum import DataType

_LOGGER = logging.getLogger(__name__)


class CLICompleter(Completer):
    """Custom completer for the CLI."""

    def __init__(self, nasa: SamsungNasa):
        """Initialize completer with NASA instance."""
        self.nasa = nasa
        self.commands = [
            "read",
            "read-range",
            "write",
            "device",
            "dump",
            "climate",
            "config",
            "logger",
            "quit",
            "help",
        ]
        self.config_subcommands = ["set", "read", "append", "dump"]
        self.logger_subcommands = ["follow", "print"]
        self.climate_modes = ["dhw", "heat"]
        self.climate_commands = ["on", "off"]

    def get_completions(self, document, complete_event):
        """Generate completions based on input."""
        text = document.text_before_cursor
        parts = text.split()

        # If no text, suggest all commands
        if not parts:
            for cmd in self.commands:
                yield Completion(cmd)
            return

        # Single word being typed - complete commands
        if len(parts) == 1:
            word = parts[0].lower()
            for cmd in self.commands:
                if cmd.startswith(word):
                    yield Completion(cmd, start_position=-len(word))
            return

        # If text ends with space, suggest next argument based on command
        if text.endswith(" "):
            command = parts[0].lower()

            if command == "config":
                # Suggest config subcommands
                for sub in self.config_subcommands:
                    yield Completion(sub)

            elif command == "logger":
                # Suggest logger subcommands
                for sub in self.logger_subcommands:
                    yield Completion(sub)

            elif command == "climate" and len(parts) == 2:
                # After "climate ", suggest device addresses
                for addr in self.nasa.devices.keys():
                    yield Completion(addr)

            elif command == "climate" and len(parts) == 3:
                # After "climate <device> ", suggest climate modes (dhw/heat)
                for m in self.climate_modes:
                    yield Completion(m)

            elif command == "climate" and len(parts) == 4:
                # After "climate <device> <mode> ", suggest on/off
                for c in self.climate_commands:
                    yield Completion(c)

            elif command in ("device", "dump", "read", "write", "read-range"):
                # Suggest device addresses
                for addr in self.nasa.devices.keys():
                    yield Completion(addr)
        else:
            # Partial word being typed
            word = parts[-1].lower()
            command = parts[0].lower()

            if command == "config" and len(parts) == 2:
                # Suggest config subcommands
                for sub in self.config_subcommands:
                    if sub.startswith(word):
                        yield Completion(sub, start_position=-len(word))

            elif command == "logger" and len(parts) == 2:
                # Suggest logger subcommands
                for sub in self.logger_subcommands:
                    if sub.startswith(word):
                        yield Completion(sub, start_position=-len(word))

            elif command == "climate" and len(parts) == 2:
                # Suggest device addresses
                for addr in self.nasa.devices.keys():
                    if addr.lower().startswith(word):
                        yield Completion(addr, start_position=-len(word))

            elif command == "climate" and len(parts) == 3:
                # Suggest climate modes (dhw/heat)
                for m in self.climate_modes:
                    if m.startswith(word):
                        yield Completion(m, start_position=-len(word))

            elif command == "climate" and len(parts) == 4:
                # Suggest on/off
                for c in self.climate_commands:
                    if c.startswith(word):
                        yield Completion(c, start_position=-len(word))

            elif command in ("device", "dump", "read", "write", "read-range") and len(parts) == 2:
                # Suggest device addresses
                for addr in self.nasa.devices.keys():
                    if addr.lower().startswith(word):
                        yield Completion(addr, start_position=-len(word))


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
    if isinstance(device, IndoorNasaDevice):
        print(f"  DHW Controller: {'Yes' if device.dhw_controller else 'No'}")
        print(f"  DHW power: {device.dhw_controller.power if device.dhw_controller else 'N/A'}")
        print(f"  DHW target temp: {device.dhw_controller.target_temperature if device.dhw_controller else 'N/A'}")
        print(f"  DHW operation mode: {device.dhw_controller.operation_mode if device.dhw_controller else 'N/A'}")
        has_cc = device.climate_controller
        print(f"  Climate Controller: {'Yes' if has_cc else 'No'}")
        cc_power = has_cc.power if has_cc else "N/A"
        print(f"  Climate power: {cc_power}")
        cc_mode = has_cc.current_mode if has_cc else "N/A"
        print(f"  Climate Controller mode: {cc_mode}")
        cc_target_temp = has_cc.f_target_temperature if has_cc else "N/A"
        print(f"  Climate Controller target temp: {cc_target_temp}")
        cc_current_temp = has_cc.f_current_temperature if has_cc else "N/A"
        print(f"  Climate Controller current temp: {cc_current_temp}")
    if isinstance(device, OutdoorNasaDevice):
        print(f"  Outdoor air temp: {device.outdoor_temperature}")
        print(f"  Heatpump voltage: {device.heatpump_voltage}")
        print(f"  Power consumption: {device.power_consumption}")
        print(f"  Power generated (last minute): {device.power_generated_last_minute}")
        print(f"  Power produced: {device.power_produced}")
        print(f"  Power current: {device.power_current}")
        print(f"  Cumulative energy: {device.cumulative_energy}")
        print(f"  Compressor frequency: {device.compressor_frequency}")
        print(f"  Fan speed: {device.fan_speed}")
        print(f"  COP rating: {device.cop_rating}")


async def print_logs():
    """Print last 20 lines of logs."""

    try:
        # Read nasa.log to get last 20 lines
        with open("nasa.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-20:]
        for line in lines:
            print(line.strip())
    except Exception as e:
        print(f"Error reading nasa.log: {e}")


async def interactive_cli(nasa: SamsungNasa):
    """Interactive CLI."""
    print("Samsung NASA Interactive CLI. Type 'help' for a list of commands.")
    completer = CLICompleter(nasa)
    session = PromptSession(
        completer=completer,
        complete_style=CompleteStyle.MULTI_COLUMN,
        complete_while_typing=False,
    )
    while True:
        try:
            with patch_stdout():
                command_str = await session.prompt_async("> ")
            if not command_str:
                continue

            parts = command_str.strip().split()
            command = parts[0].lower()

            if command == "quit":
                break
            elif command == "help":
                print("Commands:")
                print("  read <device_address> <message_id_hex>")
                print("  read-range <device_address> <start_message_id_hex> <count>")
                print("  write <device_address> <message_id_hex> <value_hex>")
                print("  device <device_address> <message_id_hex>")
                print("  dump <device_address>")
                print("  climate <device_address> <dhw/heat>")
                print("  config set <key> <value>")
                print("  config append <key> <value>")
                print("  config read <key>")
                print("  config dump")
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
                    response = await nasa.client.nasa_write(message_id, value, device_id, DataType.WRITE)
                    print(f"Response: {response}")
            elif command == "read-range" and len(parts) == 4:
                device_id = parts[1]
                try:
                    start_message_id = int(parts[2], 16)
                    count = int(parts[3])
                except ValueError:
                    print(f"Invalid message_id or count: {parts[2]}, {parts[3]}")
                    continue
                message_ids = [start_message_id + i for i in range(count)]
                print(f"Reading from {device_id}, messages {[hex(mid) for mid in message_ids]}")
                for message_id in message_ids:
                    response = await nasa.client.nasa_read([message_id], device_id)
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
                if len(parts) >= 3 and parts[1] == "set":
                    if len(parts) == 4:
                        key = parts[2]
                        value = parts[3]
                        setattr(nasa.config, key, value)
                        print(f"Config set: {key} = {value}")
                    else:
                        print("Usage: config set <key> <value>")
                elif len(parts) >= 3 and parts[1] == "read":
                    if len(parts) == 3:
                        key = parts[2]
                        print(f"Config read: {key} = {getattr(nasa.config, key)}")
                    else:
                        print("Usage: config read <key>")
                elif len(parts) >= 3 and parts[1] == "append":
                    if len(parts) == 4:
                        key = parts[2]
                        value = parts[3]
                        if value.startswith("0x"):
                            value = int(value, 16)
                        elif value.startswith("i"):
                            value = int(value[1:])
                        elif value.startswith("f"):
                            value = float(value[1:])
                        current_value = getattr(nasa.config, key)
                        if isinstance(current_value, list):
                            current_value.append(value)
                            setattr(nasa.config, key, current_value)
                            print(f"Config append: {key} += {value}")
                        else:
                            print(f"Config key {key} is not a list")
                    else:
                        print("Usage: config append <key> <value>")
                elif len(parts) == 2 and parts[1] == "dump":
                    for key, value in nasa.config.__dict__.items():
                        print(f"{key}: {value}")
                else:
                    print(
                        "Usage: config set <key> <value> or config read <key> or config append <key> <value> or config dump"
                    )
            elif command == "logger" and len(parts) == 2 and parts[1] == "follow":
                await follow_logs()
            elif command == "logger" and len(parts) == 2 and parts[1] == "print":
                await print_logs()
            elif command == "dump" and len(parts) == 2:
                device_id = parts[1]
                if device_id in nasa.devices:
                    device = nasa.devices[device_id]
                    # Sort attributes by message ID
                    sorted_attrs = dict(sorted(device.attributes.items()))
                    for k, v in sorted_attrs.items():
                        # Print k as hex
                        print(f"  {hex(k)}: {v.as_dict}")
                else:
                    print(f"Device {device_id} not found")
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
                if not isinstance(device, IndoorNasaDevice):
                    print("Climate control only available for indoor devices")
                    continue
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
                    print(f"  Current Temp: {device.climate_controller.f_current_temperature}")
                    print(f"  Target Temp: {device.climate_controller.f_target_temperature}")
                    print(f"  Mode: {device.climate_controller.current_mode}")
                    print(f"  Power: {device.climate_controller.power}")
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
