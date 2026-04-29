"""Client-side helper managers for NASA client runtime."""

from __future__ import annotations

import asyncio
import logging
from asyncio import iscoroutinefunction
from typing import Any


class TaskManager:
    """Manage lifecycle for background tasks."""

    def __init__(self) -> None:
        self.tasks: dict[str, asyncio.Task | None] = {}

    def set(self, name: str, task: asyncio.Task) -> None:
        self.tasks[name] = task

    def get(self, name: str) -> asyncio.Task | None:
        return self.tasks.get(name)

    async def cancel(self, name: str) -> bool:
        task = self.tasks.get(name)
        if not task:
            return False
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
        self.tasks[name] = None
        return True


class RetryManager:
    """Track retry state for reads and writes."""

    def __init__(self) -> None:
        self.pending_reads: dict[str, dict] = {}
        self.queued_reads: dict[str, list[list[int]]] = {}
        self.pending_writes: dict[str, dict] = {}

    def clear_pending_write(self, destination: str, message_numbers: list[int], logger=None) -> list[str]:
        cleared_keys: list[str] = []
        keys_to_delete: list[str] = []
        for write_key, write_info in self.pending_writes.items():
            if write_info["destination"] != destination:
                continue
            if message_numbers:
                packet_message_ids = write_info.get("message_ids", [])
                if all(msg_id in message_numbers for msg_id in packet_message_ids):
                    keys_to_delete.append(write_key)
                    cleared_keys.append(write_key)
            else:
                keys_to_delete.append(write_key)
                cleared_keys.append(write_key)

        for key in keys_to_delete:
            del self.pending_writes[key]
            if logger:
                logger.debug("Cleared pending write request for key %s", key)
        return cleared_keys

    def clear_pending_read(self, destination: str, message_numbers: list[int], logger=None) -> bool:
        read_key = f"{destination}_{tuple(sorted(message_numbers))}"
        if read_key not in self.pending_reads:
            return False
        del self.pending_reads[read_key]
        if logger:
            logger.debug("Cleared pending read request for messages %s from %s", message_numbers, destination)
        return True


class EventDispatcher:
    """Dispatch sync/async event handlers with centralized error handling."""

    def __init__(self, logger: logging.Logger) -> None:
        self.handlers: dict[str, object | None] = {}
        self._logger = logger

    def set_handler(self, event: str, handler: Any) -> None:
        self.handlers[event] = handler

    async def dispatch(self, event: str, *args, **kwargs) -> None:
        handler = self.handlers.get(event)
        if not handler:
            return
        try:
            if iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            elif callable(handler):
                handler(*args, **kwargs)
        except Exception as ex:
            self._logger.error("Error in event handler '%s': %s", event, ex)
