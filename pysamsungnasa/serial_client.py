"""SerialX client to handle communication with the controller."""

import asyncio
import inspect
import logging
import serialx
import os

from typing import Callable

_LOGGER = logging.getLogger(__name__)


class SerialClient:
    """SerialX client to handle communication with the controller."""

    def __init__(
        self,
        url: str,
        message_handler: Callable,
        connect_callback: Callable,
        disconnect_callback: Callable,
        baudrate: int = 9600,
    ) -> None:
        """Init a NASA Client."""
        self.url = url
        self.baudrate = baudrate
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.listner_task: asyncio.Task | None = None
        self.message_handler: Callable = message_handler
        self.connect_callback: Callable = connect_callback
        self.disconnect_callback: Callable = disconnect_callback
        self.timeout = 10
        self._is_connected = False
        _LOGGER.debug("SerialClient initialized with URL: %s and baudrate: %d", url, baudrate)

    @property
    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self._is_connected and self.writer is not None and not self.writer.is_closing()

    async def connect(self):
        """Establish a connection to the SerialX device."""
        if self._is_connected:
            return
        _LOGGER.debug("Attempting to connect to SerialX device at URL: %s with baudrate: %d", self.url, self.baudrate)
        try:
            self.reader, self.writer = await serialx.open_serial_connection(
                url=self.url,
                key=os.getenv("SAMSUNG_HP_DEVICE_KEY"),
                baudrate=self.baudrate,
                timeout=self.timeout,
                byte_size=8,
                parity=serialx.Parity.EVEN,
                stopbits=serialx.StopBits.ONE,
            )
            if self.listner_task is None or self.listner_task.done():
                self.listner_task = asyncio.create_task(self._listener_task())
            self._is_connected = True
            if self.connect_callback:
                if inspect.iscoroutinefunction(self.connect_callback):
                    await self.connect_callback()
                else:
                    self.connect_callback()
            _LOGGER.info("Successfully connected to SerialX device at URL: %s", self.url)
        except (OSError, asyncio.TimeoutError) as e:
            _LOGGER.error("Failed to connect to SerialX device at URL: %s. Error: %s", self.url, e)
            raise ConnectionError(f"Failed to connect to SerialX device at URL: {self.url}. Error: {e}")

    async def disconnect(self):
        """Disconnect the connection to the SerialX device."""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        if self.listner_task and not self.listner_task.done():
            self.listner_task.cancel()
        self._is_connected = False
        self.reader = None
        self.writer = None
        if self.disconnect_callback:
            if inspect.iscoroutinefunction(self.disconnect_callback):
                await self.disconnect_callback()
            else:
                self.disconnect_callback()
        _LOGGER.info("Connection to SerialX device at URL: %s has been closed.", self.url)

    async def _listener_task(self):
        """Listen for incoming messages from the SerialX device."""
        _LOGGER.debug("Starting listener task for SerialX device at URL: %s", self.url)
        try:
            while self.is_connected and self.reader:
                data = await self.reader.readuntil(0x34.to_bytes())  # Read until the end byte (0x34)
                if data:
                    _LOGGER.debug("Received message from SerialX device at URL: %s", self.url)
                    try:
                        if self.message_handler:
                            if inspect.iscoroutinefunction(self.message_handler):
                                await self.message_handler(data)
                            else:
                                self.message_handler(data)
                    except Exception as e:
                        _LOGGER.exception(
                            "Error in message handler for SerialX device at URL: %s. Error: %s", self.url, e
                        )
                else:
                    _LOGGER.warning("SerialX device at URL: %s has closed the connection.", self.url)
                    await self.disconnect()
        except asyncio.IncompleteReadError:
            _LOGGER.debug("SerialX device at URL: %s has closed the connection.", self.url)
            await self.disconnect()
        except (OSError, asyncio.CancelledError) as e:
            _LOGGER.exception("Listener task for SerialX device at URL: %s encountered an error: %s", self.url, e)
            await self.disconnect()
