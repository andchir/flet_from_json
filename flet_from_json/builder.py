"""
JSON UI Builder for constructing Flet interfaces from JSON configuration.
"""

import flet as ft

from .elements import ElementBuilder
from .state import AppState


class JsonUIBuilder:
    """Main class that builds the complete UI from JSON configuration."""

    def __init__(self, page: ft.Page, json_data: dict):
        self.page = page
        self.json_data = json_data
        self.app_state = AppState()
        self.element_builder = ElementBuilder(page, self.app_state)

    def build(self) -> None:
        """Build the complete UI."""
        # Set page title from JSON
        app_name = self.json_data.get("name", "Flet App")
        self.page.title = app_name

        # Get tabs configuration
        tabs_config = self.json_data.get("tabs", [])
        blocks = self.json_data.get("blocks", [])

        if tabs_config:
            # Build tabbed interface
            self._build_tabbed_interface(tabs_config, blocks)
        else:
            # Build single-page interface
            self._build_single_page(blocks)

    def _build_tabbed_interface(self, tabs_config: list, blocks: list) -> None:
        """Build a tabbed interface."""
        # Group blocks by tabIndex
        blocks_by_tab: dict[int, list] = {}
        for block in blocks:
            tab_index = block.get("tabIndex", 0)
            if tab_index not in blocks_by_tab:
                blocks_by_tab[tab_index] = []
            blocks_by_tab[tab_index].append(block)

        # Create tabs
        flet_tabs = []
        for i, tab_name in enumerate(tabs_config):
            tab_blocks = blocks_by_tab.get(i, [])
            tab_content = self._build_blocks_content(tab_blocks)

            flet_tabs.append(ft.Tab(
                label=tab_name,
                content=ft.Container(
                    content=tab_content,
                    padding=20,
                ),
            ))

        tabs_control = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=flet_tabs,
            expand=True,
        )

        self.page.add(tabs_control)

    def _build_single_page(self, blocks: list) -> None:
        """Build a single-page interface without tabs."""
        content = self._build_blocks_content(blocks)
        self.page.add(content)

    def _build_blocks_content(self, blocks: list) -> ft.Control:
        """Build content for a list of blocks."""
        # Sort blocks by orderIndex
        sorted_blocks = sorted(blocks, key=lambda b: b.get("options", {}).get("orderIndex", 0))

        columns = []
        for block in sorted_blocks:
            block_content = self._build_block(block)
            if block_content:
                columns.append(block_content)

        return ft.Column(
            columns,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20,
        )

    def _build_block(self, block: dict) -> ft.Control | None:
        """Build a single block with its elements."""
        options = block.get("options", {})

        # Check if block is enabled
        if not options.get("enabled", True):
            # Block is disabled, but still show its elements (just as static display)
            pass

        elements = block.get("elements", [])

        # Sort elements by orderIndex
        sorted_elements = sorted(elements, key=lambda e: e.get("orderIndex", 0))

        built_elements = []
        for element in sorted_elements:
            control = self.element_builder.build_element(element)
            if control:
                built_elements.append(control)

        if not built_elements:
            return None

        # Wrap in a container with optional styling
        return ft.Container(
            content=ft.Column(built_elements, spacing=10),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.BLACK),
        )
