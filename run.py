"""Run NASA controller tests."""

import asyncio
import os
import logging

from dotenv import load_dotenv
from pysamsungnasa import SamsungNasa

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
            "log_buffer_messages": False,
            "devices_to_log": ["200000"],
        },
    )
    try:
        await nasa.start()
        await nasa.client.nasa_read([0x4097])
        while True:
            await asyncio.sleep(5)
            # for k, v in nasa.devices.items():
            #     logging.info("Device %s:", k)
            #     logging.info("  Type: %s", v.device_type.name)
            #     logging.info("  Address: %s", v.address)
            #     logging.info("  Attributes: %s", v.attributes)
            #     logging.info("  Last packet time: %s", v.last_packet_time)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        await nasa.stop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        # filename="nasa.log",
    )
    asyncio.run(main())
