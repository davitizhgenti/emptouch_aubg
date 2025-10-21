# core/widgets.py
from dataclasses import dataclass
from typing import Callable, List


# This list will hold all registered widget configurations.
WIDGET_REGISTRY: List['Widget'] = []

@dataclass
class Widget:
    """A dataclass to hold the configuration for a dashboard widget."""
    name: str
    permission_codename: str
    template_name: str
    fetch_data_func: Callable

def register(widget: Widget):
    """A function to add a widget to the central registry."""
    if not isinstance(widget, Widget):
        raise TypeError("Only Widget instances can be registered.")
    WIDGET_REGISTRY.append(widget)