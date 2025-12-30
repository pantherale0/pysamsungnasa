"""All possible messages for the Samsung NASA protocol."""

import importlib
import inspect
import pkgutil

from ..messaging import BaseMessage


def load_message_classes():
    """Dynamically load all classes defined under protocol.factory.messages."""
    classes = {}
    package = __name__

    # Iterate through all modules in the package
    for _, module_name, _ in pkgutil.iter_modules([__path__[0]]):
        full_module_name = f"{package}.{module_name}"
        module = importlib.import_module(full_module_name)

        # Inspect the module for classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Ensure the class is defined in the module (not imported)
            if obj.__module__ == full_module_name:
                if issubclass(obj, BaseMessage) and hasattr(obj, "MESSAGE_ID"):
                    classes[obj.MESSAGE_ID] = obj

    return classes
