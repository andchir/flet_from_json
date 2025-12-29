"""
Flet application that dynamically builds UI from JSON configuration.

This is the entry point for the application. The main logic is organized
in the flet_from_json package.
"""

import json
import logging
from pathlib import Path

import flet as ft

from flet_from_json import JsonUIBuilder, load_json_from_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(page: ft.Page):
    """Main function that initializes the Flet application."""
    # Configure page
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    try:
        # Load JSON configuration
        # Use script directory as base path for resolving JSON file
        base_path = Path(__file__).parent
        json_data = load_json_from_env(base_path)

        # Build UI from JSON
        builder = JsonUIBuilder(page, json_data)
        builder.build()

    except FileNotFoundError as e:
        page.add(ft.Text(
            f"Error: {e}",
            color=ft.Colors.RED,
            size=16,
        ))
    except json.JSONDecodeError as e:
        page.add(ft.Text(
            f"Error parsing JSON: {e}",
            color=ft.Colors.RED,
            size=16,
        ))
    except Exception as e:
        logger.exception("Unexpected error")
        page.add(ft.Text(
            f"Unexpected error: {e}",
            color=ft.Colors.RED,
            size=16,
        ))


if __name__ == "__main__":
    ft.run(main)
