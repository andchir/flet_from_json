"""
Constants and mappings used throughout the application.
"""

import flet as ft

# Color mapping from JSON to Flet colors
COLOR_MAP = {
    "Blue": ft.Colors.BLUE,
    "Green": ft.Colors.GREEN,
    "Red": ft.Colors.RED,
    "Yellow": ft.Colors.YELLOW,
    "Gray": ft.Colors.GREY,
    "Grey": ft.Colors.GREY,
    "Black": ft.Colors.BLACK,
    "White": ft.Colors.WHITE,
    "Orange": ft.Colors.ORANGE,
    "Purple": ft.Colors.PURPLE,
}

# Font size mapping
FONT_SIZE_MAP = {
    "Small": 12,
    "Medium": 14,
    "Large": 18,
    "XLarge": 24,
}

# Bootstrap Icons to Flet Icons mapping
ICON_MAP = {
    "bi-check2": ft.Icons.CHECK,
    "bi-download": ft.Icons.DOWNLOAD,
    "bi-upload": ft.Icons.UPLOAD,
    "bi-info-circle": ft.Icons.INFO,
    "bi-question-circle": ft.Icons.HELP,
    "bi-arrow-right": ft.Icons.ARROW_FORWARD,
    "bi-arrow-left": ft.Icons.ARROW_BACK,
}
