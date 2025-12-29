"""
Flet from JSON - Dynamic UI builder for Flet applications.

This package provides utilities to build Flet user interfaces
from JSON configuration files.
"""

from .builder import JsonUIBuilder
from .config import load_json_from_env
from .constants import COLOR_MAP, FONT_SIZE_MAP, ICON_MAP
from .elements import ElementBuilder
from .state import AppState

__all__ = [
    "JsonUIBuilder",
    "ElementBuilder",
    "AppState",
    "load_json_from_env",
    "COLOR_MAP",
    "FONT_SIZE_MAP",
    "ICON_MAP",
]

__version__ = "0.1.0"
