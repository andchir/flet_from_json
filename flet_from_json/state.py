"""
Application state management for the Flet JSON UI builder.
"""

import logging
from typing import Any, Callable

import flet as ft

logger = logging.getLogger(__name__)


class AppState:
    """Holds application state including field values for conditional visibility."""

    def __init__(self):
        self.field_values: dict[str, Any] = {}
        self.field_controls: dict[str, ft.Control] = {}
        self.visibility_callbacks: list[Callable[[], None]] = []

    def set_value(self, name: str, value: Any) -> None:
        """Set a field value and trigger visibility updates."""
        self.field_values[name] = value
        self._update_visibility()

    def get_value(self, name: str, default: Any = None) -> Any:
        """Get a field value."""
        return self.field_values.get(name, default)

    def register_visibility_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be called when field values change."""
        self.visibility_callbacks.append(callback)

    def _update_visibility(self) -> None:
        """Call all registered visibility callbacks."""
        for callback in self.visibility_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error updating visibility: {e}")
