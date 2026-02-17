# Examples

Real-world code examples for pysamsungnasa.

## Basic Connection

Connect and read device data:

```python
import asyncio
from pysamsungnasa import SamsungNasa

async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={"client_address": 1}
    )

    await nasa.start()

    # Wait for devices
    await asyncio.sleep(2)

    # Display discovered devices
    print(f"Found {len(nasa.devices)} devices:")
    for address, device in nasa.devices.items():
        print(f"  {address}: {device.device_type}")

    await nasa.stop()

asyncio.run(main())
```

## Temperature Monitoring

Monitor temperatures from all devices:

```python
import asyncio
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.outdoor import OutdoorAirTemperature
from pysamsungnasa.protocol.factory.messages.indoor import (
    InCurrentTemperature,
    InTargetTemperature,
    InOperationModeMessage
)

async def main():
    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["100000", "200020"]
        }
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for devices

    print("Temperature Monitoring")
    print("-" * 40)

    for address, device in nasa.devices.items():
        print(f"\nDevice ({address}):")
        
        # Try reading outdoor temperature
        try:
            outdoor_temp = await device.get_attribute(OutdoorAirTemperature)
            print(f"  Outdoor Temperature: {outdoor_temp.VALUE}°C")
        except (TimeoutError, KeyError):
            pass
        
        # Try reading indoor temperature
        try:
            current_temp = await device.get_attribute(InCurrentTemperature)
            target_temp = await device.get_attribute(InTargetTemperature)
            mode = await device.get_attribute(InOperationModeMessage)
            print(f"  Current: {current_temp.VALUE}°C")
            print(f"  Target: {target_temp.VALUE}°C")
            print(f"  Mode: {mode.VALUE}")
        except (TimeoutError, KeyError):
            pass

    await nasa.stop()

asyncio.run(main())
```

## Smart Thermostat

Maintain automatic temperature control:

```python
import asyncio
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.indoor import (
    InCurrentTemperature,
    InOperationModeMessage
)
from pysamsungnasa.protocol.enum import InOperationMode

async def smart_thermostat(target_temp=22, hysteresis=0.5):
    """
    Simple smart thermostat that maintains temperature.

    Args:
        target_temp: Target temperature in °C
        hysteresis: Temperature deadband
    """

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["200020"]
        }
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for device

    indoor = nasa.devices["200020"]

    async def control_temperature(device):
        try:
            # Get current temperature
            temp_msg = await device.get_attribute(InCurrentTemperature)
            current = temp_msg.VALUE
            
            # Get current mode
            mode_msg = await device.get_attribute(InOperationModeMessage)
            current_mode = mode_msg.VALUE

            # Heating needed
            if current < target_temp - hysteresis:
                if current_mode != InOperationMode.HEAT:
                    await device.write_attribute(
                        InOperationModeMessage,
                        InOperationMode.HEAT
                    )
                print(f"Heating: {current:.1f}°C → {target_temp}°C")

            # Cooling needed
            elif current > target_temp + hysteresis:
                if current_mode != InOperationMode.COOL:
                    await device.write_attribute(
                        InOperationModeMessage,
                        InOperationMode.COOL
                    )
                print(f"Cooling: {current:.1f}°C → {target_temp}°C")

            # In range
            else:
                print(f"OK: {current:.1f}°C (target {target_temp}°C)")
        
        except TimeoutError:
            print("Timeout reading temperature")

    # Register callback
    indoor.add_device_callback(control_temperature)

    # Run for 1 hour
    print(f"Smart thermostat active (target: {target_temp}°C)")
    await asyncio.sleep(3600)

    await nasa.stop()

asyncio.run(smart_thermostat())
```

## Energy Monitoring

Track power consumption:

```python
import asyncio
from datetime import datetime
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.outdoor import (
    OutdoorPowerConsumption,
    OutdoorCumulativeEnergy,
    OutdoorCopRating
)

async def energy_monitoring():
    """Monitor and log power consumption."""

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["100000"]
        }
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for device

    outdoor = nasa.devices["100000"]

    async def log_power(device):
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            power_msg = await device.get_attribute(OutdoorPowerConsumption)
            power = power_msg.VALUE
            
            cumulative_msg = await device.get_attribute(OutdoorCumulativeEnergy)
            cumulative = cumulative_msg.VALUE
            
            cop_msg = await device.get_attribute(OutdoorCopRating)
            cop = cop_msg.VALUE

            print(f"{timestamp} | "
                  f"Power: {power:6.0f}W | "
                  f"Energy: {cumulative:7.1f}kWh | "
                  f"COP: {cop:.1f}")
        except TimeoutError:
            print("Timeout reading energy data")

    outdoor.add_device_callback(log_power)

    print("Energy Monitoring")
    print("-" * 60)
    print(f"{'Time':<10} | {'Power':>10} | {'Cumulative':>12} | {'COP':>8}")
    print("-" * 60)

    # Log for 1 hour
    await asyncio.sleep(3600)

    await nasa.stop()

asyncio.run(energy_monitoring())
```

## Multi-Zone Climate Control

Control multiple zones independently:

```python
import asyncio
from pysamsungnasa import SamsungNasa
from pysamsungnasa.protocol.factory.messages.indoor import (
    InOperationPowerMessage,
    InOperationModeMessage,
    InTargetTemperature,
    InFanSpeedMessage,
    InCurrentTemperature
)
from pysamsungnasa.protocol.enum import InOperationMode

async def multi_zone_control():
    """Control climate in multiple zones."""

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["200020", "200021", "200022"]
        }
    )

    await nasa.start()
    await asyncio.sleep(2)  # Wait for devices

    zones = {
        "200020": {"name": "Living Room", "target": 22},
        "200021": {"name": "Bedroom", "target": 19},
        "200022": {"name": "Kitchen", "target": 21}
    }

    # Apply settings to each zone
    for address, zone_config in zones.items():
        device = nasa.devices.get(address)
        if not device:
            continue

        print(f"Setting {zone_config['name']} to {zone_config['target']}°C")

        # Set multiple attributes at once
        await device.write_attributes({
            InOperationPowerMessage: 1,  # Turn on
            InOperationModeMessage: InOperationMode.AUTO,  # Auto mode
            InTargetTemperature: zone_config['target'],  # Temperature
            InFanSpeedMessage: 2,  # Fan speed
        })

    # Monitor all zones
    async def monitor():
        print("\n=== Zone Status ===")
        for address, zone_config in zones.items():
            device = nasa.devices.get(address)
            if not device:
                continue

            try:
                current = await device.get_attribute(InCurrentTemperature)
                target = await device.get_attribute(InTargetTemperature)
                mode = await device.get_attribute(InOperationModeMessage)
                print(f"{zone_config['name']}: "
                      f"{current.VALUE}°C "
                      f"(target {target.VALUE}°C) "
                      f"mode={mode.VALUE}")
            except TimeoutError:
                print(f"{zone_config['name']}: Timeout")

    # Monitor for 30 minutes
    for i in range(30):
        await monitor()
        await asyncio.sleep(60)

    await nasa.stop()

asyncio.run(multi_zone_control())
```

## DHW Control with Schedule

Heat water on a schedule:

```python
import asyncio
from datetime import datetime, time
from pysamsungnasa import SamsungNasa

async def scheduled_dhw():
    """Turn DHW on/off on a schedule."""

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["200020"]
        }
    )

    # Schedule: Morning 6-8, Evening 18-20
    schedule = [
        (6, 8),    # 6-8 AM
        (18, 20),  # 6-8 PM
    ]

    await nasa.start()

    device = nasa.devices["200020"]
    dhw = device.dhw_controller

    async def check_schedule():
        now = datetime.now()
        current_hour = now.hour

        should_be_on = any(start <= current_hour < end for start, end in schedule)
        is_on = dhw.power

        if should_be_on and not is_on:
            print(f"{now.strftime('%H:%M:%S')} - Turning DHW ON")
            await dhw.turn_on()
            await dhw.set_target_temperature(45)

        elif not should_be_on and is_on:
            print(f"{now.strftime('%H:%M:%S')} - Turning DHW OFF")
            await dhw.turn_off()

        status = "ON" if dhw.power else "OFF"
        temp = dhw.current_temperature or 0
        target = dhw.target_temperature or 0
        print(f"  Status: {status}, Current: {temp}°C, Target: {target}°C")

    # Check schedule every minute
    try:
        while True:
            await check_schedule()
            await asyncio.sleep(60)
    finally:
        await nasa.stop()

# Run the scheduler
asyncio.run(scheduled_dhw())
```

## Integration with Home Automation

Simple integration pattern:

```python
import asyncio
from pysamsungnasa import SamsungNasa

class SmartHomeIntegration:
    """Example home automation integration."""

    def __init__(self, host, port):
        self.nasa = SamsungNasa(
            host=host,
            port=port,
            config={
                "client_address": 1,
                "device_addresses": ["200000", "200020"]
            }
        )
        self.device_callbacks = {}

    async def start(self):
        """Start the integration."""
        await self.nasa.start()

        # Register callbacks
        for address, device in self.nasa.devices.items():
            device.add_device_callback(self._on_device_update)

    async def stop(self):
        """Stop the integration."""
        await self.nasa.stop()

    def _on_device_update(self, device):
        """Handle device updates."""
        callback = self.device_callbacks.get(device.address)
        if callback:
            callback(device)

    def on_device_update(self, address):
        """Decorator for device update handlers."""
        def decorator(func):
            self.device_callbacks[address] = func
            return func
        return decorator

    async def set_temperature(self, address, temp):
        """Set temperature for a zone."""
        device = self.nasa.devices.get(address)
        if device and device.climate_controller:
            await device.climate_controller.set_target_temperature(temp)

# Usage
async def main():
    home = SmartHomeIntegration("192.168.1.100", 8000)

    @home.on_device_update("100000")
    def on_outdoor_update(device):
        print(f"Outdoor: {device.outdoor_temperature}°C, "
              f"Power: {device.power_consumption}W")

    @home.on_device_update("200020")
    def on_indoor_update(device):
        if device.climate_controller:
            cc = device.climate_controller
            print(f"Indoor: {cc.f_current_temperature}°C, "
                  f"Mode: {cc.current_mode}")

    await home.start()

    # Control temperature
    await home.set_temperature("200020", 22)

    # Run for 30 seconds
    await asyncio.sleep(30)

    await home.stop()

asyncio.run(main())
```

## Continuous Monitoring with Logging

Log all device data continuously:

```python
import asyncio
import logging
from pysamsungnasa import SamsungNasa

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hvac.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("HVAC")

async def continuous_monitoring():
    """Continuous monitoring with full logging."""

    nasa = SamsungNasa(
        host="192.168.1.100",
        port=8000,
        config={
            "client_address": 1,
            "device_addresses": ["200000", "200020"]
        }
    )

    def log_device_update(device):
        """Log device update."""
        logger.info(f"Device {device.address} updated")

        if hasattr(device, 'outdoor_temperature'):
            logger.info(f"  Outdoor temp: {device.outdoor_temperature}°C")
            logger.info(f"  Power: {device.power_consumption}W")

        if hasattr(device, 'climate_controller') and device.climate_controller:
            cc = device.climate_controller
            logger.info(f"  Indoor temp: {cc.f_current_temperature}°C")
            logger.info(f"  Mode: {cc.current_mode}")

    await nasa.start()

    # Register callbacks
    for device in nasa.devices.values():
        device.add_device_callback(log_device_update)

    logger.info("Monitoring started")

    # Run indefinitely
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped")
    finally:
        await nasa.stop()

asyncio.run(continuous_monitoring())
```

## Error Handling and Resilience

Robust error handling:

```python
import asyncio
import logging
from pysamsungnasa import SamsungNasa

logger = logging.getLogger("NASA")

async def resilient_connection():
    """Connection with error handling and reconnection."""

    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            nasa = SamsungNasa(
                host="192.168.1.100",
                port=8000,
                config={"client_address": 1}
            )

            await nasa.start()
            logger.info("Connected successfully")

            # Operate normally
            await asyncio.sleep(3600)

            await nasa.stop()
            break

        except ConnectionError as e:
            logger.error(f"Connection error: {e}")

            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay}s... "
                           f"({attempt + 1}/{max_retries})")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries exceeded")

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            await asyncio.sleep(retry_delay)

asyncio.run(resilient_connection())
```

## More Examples

For more complete examples, check the test files in the project repository.

## Next Steps

- Read [Basic Usage](user-guide/basic-usage.md)
- Check [Configuration](user-guide/configuration.md)
- Explore [API Reference](api/samsung-nasa.md)
