"""Run NASA controller tests."""

import asyncio
import os
import logging
import argparse

from dotenv import load_dotenv
from pysamsungnasa import SamsungNasa
from pysamsungnasa.cli import interactive_cli

load_dotenv()


async def main():
    """Main test thread."""
    nasa = SamsungNasa(
        host=os.getenv("SAMSUNG_HP_HOST", "unknown"),
        port=int(os.getenv("SAMSUNG_HP_PORT", 0)),
        config={
            "device_pnp": True,
            "device_dump_only": False,
            "log_all_messages": True,
            "log_buffer_messages": True,
            "devices_to_log": ["200000"],
        },
    )
    try:
        await nasa.start()
        await nasa.client.nasa_read([0x4097], "200000")
        while True:
            await asyncio.sleep(0.1)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        await nasa.stop()


async def start_cli():
    """Start the interactive CLI."""
    nasa = SamsungNasa(
        host=os.getenv("SAMSUNG_HP_HOST", "unknown"),
        port=int(os.getenv("SAMSUNG_HP_PORT", 0)),
        config={
            "device_pnp": True,
            "device_dump_only": False,
            "log_all_messages": True,
            "log_buffer_messages": True,
            "devices_to_log": ["200000"],
        },
    )
    try:
        await nasa.start()
        await interactive_cli(nasa)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
    finally:
        await nasa.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="nasa.log",
    )
    asyncio.run(start_cli())
