"""Functionality to execute when run as a script."""

# Uses cli.py to provide an interactive CLI for testing.
# Environment variables can be used to set the host and port of the Samsung NASA device:

import asyncio
import os
import logging
from dotenv import load_dotenv

from .nasa import SamsungNasa
from .cli import interactive_cli

load_dotenv()


async def main():
    """Main function to start the interactive CLI."""
    if os.getenv("SAMSUNG_HP_HOST") is None or os.getenv("SAMSUNG_HP_PORT") is None:
        print("Please set the SAMSUNG_HP_HOST and SAMSUNG_HP_PORT environment variables.", file=sys.stderr)
        sys.exit(1)

    nasa = SamsungNasa(
        host=os.getenv("SAMSUNG_HP_HOST"),
        port=int(os.getenv("SAMSUNG_HP_PORT")),
        config={
            "device_pnp": os.getenv("SAMSUNG_HP_DEVICE_PNP", "True").lower() in ("true", "1", "yes"),
            "device_dump_only": os.getenv("SAMSUNG_HP_DEVICE_DUMP_ONLY", "False").lower() in ("true", "1", "yes"),
            "log_all_messages": os.getenv("SAMSUNG_HP_LOG_ALL_MESSAGES", "False").lower() in ("true", "1", "yes"),
            "log_buffer_messages": os.getenv("SAMSUNG_HP_LOG_BUFFER_MESSAGES", "False").lower() in ("true", "1", "yes"),
            "messages_to_log": (
                [int(x, 0) for x in os.getenv("SAMSUNG_HP_MESSAGES_TO_LOG", "").split(",") if x.strip()]
                if os.getenv("SAMSUNG_HP_MESSAGES_TO_LOG")
                else []
            ),
            "devices_to_log": (
                [x.strip() for x in os.getenv("SAMSUNG_HP_DEVICES_TO_LOG", "").split(",") if x.strip()]
                if os.getenv("SAMSUNG_HP_DEVICES_TO_LOG")
                else []
            ),
        },
    )
    await nasa.start()
    try:
        await interactive_cli(nasa)
    finally:
        await nasa.stop()


if __name__ == "__main__":
    # Log to nasa.log in CWD at level defined by LOG_LEVEL env var (default DEBUG)
    log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.DEBUG),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="nasa.log",
        filemode="a",
    )
    # Add a logger for error messages to console
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    # Suppress noisy aiotelnet.client debug logs
    logging.getLogger("aiotelnet.client").setLevel(logging.INFO)

    # Execute main
    asyncio.run(main())
