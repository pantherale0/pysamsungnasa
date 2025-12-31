# pysamsungnasa

[![Tests](https://github.com/pantherale0/pysamsungnasa/actions/workflows/test.yml/badge.svg)](https://github.com/pantherale0/pysamsungnasa/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/pantherale0/pysamsungnasa/branch/main/graph/badge.svg)](https://codecov.io/gh/pantherale0/pysamsungnasa)

A Python library to communicate with Samsung heat pumps, in theory both cool only and cool+heat units are supported, although only tested on an EHS unit (cool+heat)

## Features

- Connect and disconnect from Samsung HVAC/EHS units via a TCP socket over the F1/F2 connectors (NasaClient).
- Discover new devices on the NASA network and manage known devices (SamsungNasa).
- Send commands to devices and handle responses (SamsungNasa, NasaClient).
- Parse incoming data packets from devices (NasaPacketParser, various message classes).
- Represent devices with attributes and control their functions (NasaDevice, DhwController, ClimateController).
- Control DHW (Domestic Hot Water) settings like power, operation mode, and target temperature (DhwController).
- Control climate settings like power, mode, target temperature, fan speed, and more (ClimateController).
- Provide a mechanism for callbacks to be notified of device and packet updates (NasaDevice).
- Support reading device configurations (NasaDevice).
- Handle message construction and parsing based on message types (protocol.factory).
- Define specific message formats for indoor and outdoor units (protocol.factory.messages).

## Future plans

These might not end up happening, but I would like to have a go at creating these one day.

- Simulate a remote controller for a "dummy" zone 2
- Send custom Z1/Z2 temperature readings to the master controller
- Implement TPI/load awareness/preditive model algorithms for an advanced complete custom controller

## Installation

```bash
pip install pysamsungnasa
```

## Usage

TODO

## Configuration

TODO

## Contributing

TODO

## Thanks

This project utilizes or incorporates ideas, code and work from the following sources,
and I would like to express my sincere gratitude to their creators and contributors:

- [ESPHome Samsung HVAC Bus](https://github.com/omerfaruk-aran/esphome_samsung_hvac_bus/)
- [Samsung NASA MQTT Bridge](https://github.com/70p4z/samsung-nasa-mqtt/)
- [Samsung ASHP NASA link MQTT bridge / Home Assistant](https://community.openenergymonitor.org/t/contribution-samsung-ashp-nasa-link-mqtt-bridge-home-assistant)
- [OpenEnergyMonitoring Forum](https://community.openenergymonitor.org/search?q=samsung) for all the shared wisdom on multiple threads.
- @betaphi for the [EHS Wiki](https://wiki.myehs.eu/wiki/Main_Page), which provided valuable insights into different messages. The protocol is mostly documented [here](NOTES.md) as the NASA Protocol page is no longer on the wiki. More messages are defined within the parser classes from the latest version of S-Net.

None of this would have been possible without the above.
