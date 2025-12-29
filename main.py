"""
Flet application that dynamically builds UI from JSON configuration.
This application loads a JSON file specified in the .env file and creates
a graphical interface based on the JSON structure.
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Any, Callable

import flet as ft
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


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


class ElementBuilder:
    """Builds Flet controls from JSON element definitions."""

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

    def __init__(self, page: ft.Page, app_state: AppState):
        self.page = page
        self.app_state = app_state
        self.file_picker: ft.FilePicker | None = None

    def build_element(self, element: dict) -> ft.Control | None:
        """Build a Flet control from an element definition."""
        element_type = element.get("type", "")

        # Check if element is hidden by default or always hidden
        if element.get("hiddenByDefault", False) or element.get("hidden", False):
            return None

        builder_method = getattr(self, f"_build_{element_type.replace('-', '_')}", None)

        if builder_method:
            control = builder_method(element)
            if control:
                # Setup conditional visibility if needed
                hidden_by_field = element.get("hiddenByField", "")
                if hidden_by_field:
                    self._setup_conditional_visibility(control, hidden_by_field)
                return control
        else:
            logger.warning(f"Unknown element type: {element_type}")
            return None

        return None

    def _setup_conditional_visibility(self, control: ft.Control, hidden_by_field: str) -> None:
        """Setup conditional visibility based on field value."""
        # Parse hiddenByField format: "fieldName==value" means hidden when field equals value
        # The control should be VISIBLE when condition is met (hidden when NOT met)
        if "==" in hidden_by_field:
            parts = hidden_by_field.split("==")
            if len(parts) == 2:
                field_name = parts[0].strip()
                expected_value = parts[1].strip()

                def update_visibility():
                    current_value = self.app_state.get_value(field_name, "")
                    # Show when field value equals expected value
                    control.visible = str(current_value) == expected_value
                    try:
                        control.update()
                    except Exception:
                        pass  # Control might not be attached yet

                self.app_state.register_visibility_callback(update_visibility)
                # Initial visibility check
                update_visibility()

    def _build_text(self, element: dict) -> ft.Control:
        """Build a Text element."""
        value = element.get("value", "")
        color = self.COLOR_MAP.get(element.get("color", "Black"), ft.Colors.BLACK)
        font_size = self.FONT_SIZE_MAP.get(element.get("fontSize", "Medium"), 14)

        # Handle markdown
        if element.get("markdown", False):
            text_control = ft.Markdown(
                value,
                selectable=True,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            )
        else:
            text_control = ft.Text(
                value,
                color=color,
                size=font_size,
                text_align=ft.TextAlign.CENTER if element.get("alignCenter", False) else ft.TextAlign.LEFT,
            )

        # Wrap in container if border or shadow is needed
        if element.get("border", False) or element.get("borderShadow", False):
            container = ft.Container(
                content=text_control,
                padding=10,
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.1, color),
            )
            if element.get("borderShadow", False):
                container.shadow = ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                )
            return container

        return text_control

    def _build_image(self, element: dict) -> ft.Control | None:
        """Build an Image element."""
        value = element.get("value", "")
        if not value:
            return None

        image = ft.Image(
            src=value,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(8) if element.get("roundedCorners", False) else None,
        )

        # Wrap in container for click handling if useLink is enabled
        if element.get("useLink", False) or element.get("useLightbox", False):
            container = ft.Container(
                content=image,
                on_click=lambda e: self.page.launch_url(value) if element.get("useLink") else None,
            )
            return container

        return image

    def _build_input_text(self, element: dict) -> ft.Control:
        """Build a TextField element."""
        name = element.get("name", "")

        text_field = ft.TextField(
            label=element.get("label", ""),
            value=str(element.get("value", "")),
            hint_text=element.get("placeholder", ""),
            read_only=element.get("readOnly", False),
        )

        def on_change(e):
            self.app_state.set_value(name, e.control.value)

        text_field.on_change = on_change

        # Store initial value
        if name:
            self.app_state.set_value(name, element.get("value", ""))
            self.app_state.field_controls[name] = text_field

        return text_field

    def _build_input_textarea(self, element: dict) -> ft.Control:
        """Build a multi-line TextField element."""
        name = element.get("name", "")
        rows = element.get("rows", 3)

        text_field = ft.TextField(
            label=element.get("label", ""),
            value=str(element.get("value", "")),
            hint_text=element.get("placeholder", ""),
            multiline=True,
            min_lines=rows,
            max_lines=rows if not element.get("autoHeight", False) else None,
            read_only=element.get("readOnly", False),
        )

        def on_change(e):
            self.app_state.set_value(name, e.control.value)

        text_field.on_change = on_change

        # Store initial value
        if name:
            self.app_state.set_value(name, element.get("value", ""))
            self.app_state.field_controls[name] = text_field

        return text_field

    def _build_input_select(self, element: dict) -> ft.Control:
        """Build a Dropdown element."""
        name = element.get("name", "")
        value_arr = element.get("valueArr", [])

        # Build dropdown options from valueArr
        options = []
        title_field = element.get("itemFieldNameForTitle", "name")
        value_field = element.get("itemFieldNameForValue", "value")

        for item in value_arr:
            if isinstance(item, dict):
                options.append(ft.dropdown.Option(
                    key=str(item.get(value_field, "")),
                    text=str(item.get(title_field, "")),
                ))
            else:
                options.append(ft.dropdown.Option(key=str(item), text=str(item)))

        current_value = element.get("value", "")

        dropdown = ft.Dropdown(
            label=element.get("label", ""),
            value=str(current_value) if current_value else None,
            hint_text=element.get("placeholder", ""),
            options=options,
        )

        def on_change(e):
            self.app_state.set_value(name, e.control.value)

        dropdown.on_change = on_change

        # Store initial value
        if name:
            self.app_state.set_value(name, current_value)
            self.app_state.field_controls[name] = dropdown

        return dropdown

    def _build_input_file(self, element: dict) -> ft.Control:
        """Build a file picker button."""
        name = element.get("name", "")
        accept = element.get("accept", "")
        multiple = element.get("multiple", False)
        label = element.get("label", "")
        placeholder = element.get("placeholder", "Choose file...")

        # Create file picker if not exists
        if not self.file_picker:
            self.file_picker = ft.FilePicker()
            self.page.overlay.append(self.file_picker)

        # Create a text field to display selected file name
        file_text = ft.Text(placeholder, italic=True, color=ft.Colors.GREY)

        def pick_files(e):
            # Determine allowed extensions from accept
            allowed_extensions = None
            if accept:
                # Parse accept attribute (e.g., "image/*" or ".jpg,.png")
                if accept.startswith("image/"):
                    allowed_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "webp"]
                elif accept.startswith("video/"):
                    allowed_extensions = ["mp4", "avi", "mov", "webm"]
                elif "," in accept:
                    allowed_extensions = [ext.strip().lstrip(".") for ext in accept.split(",")]

            self.file_picker.pick_files(
                allow_multiple=multiple,
                allowed_extensions=allowed_extensions,
            )

        def on_result(e: ft.FilePickerResultEvent):
            if e.files:
                file_names = ", ".join([f.name for f in e.files])
                file_text.value = file_names
                file_text.update()
                self.app_state.set_value(name, [f.path for f in e.files])
            else:
                file_text.value = placeholder
                file_text.update()
                self.app_state.set_value(name, [])

        self.file_picker.on_result = on_result

        pick_button = ft.Button(
            content=ft.Row([
                ft.Icon(ft.Icons.UPLOAD_FILE),
                ft.Text(label if label else "Choose file"),
            ], tight=True, spacing=5),
            on_click=pick_files,
        )

        return ft.Column([
            pick_button,
            file_text,
        ], spacing=5)

    def _build_button(self, element: dict) -> ft.Control:
        """Build a Button element."""
        text = element.get("text", "")
        color = self.COLOR_MAP.get(element.get("color", "Blue"), ft.Colors.BLUE)
        icon_name = element.get("icon", "")

        # Map Bootstrap Icons to Flet Icons (basic mapping)
        icon_map = {
            "bi-check2": ft.Icons.CHECK,
            "bi-download": ft.Icons.DOWNLOAD,
            "bi-upload": ft.Icons.UPLOAD,
            "bi-info-circle": ft.Icons.INFO,
            "bi-question-circle": ft.Icons.HELP,
            "bi-arrow-right": ft.Icons.ARROW_FORWARD,
            "bi-arrow-left": ft.Icons.ARROW_BACK,
        }
        flet_icon = icon_map.get(icon_name) if icon_name else None

        def on_click(e):
            # For now, just log the button click
            # In a real implementation, this would trigger API calls
            logger.info(f"Button clicked: {element.get('name', 'unknown')}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Button action would be triggered here"),
                open=True,
            )
            self.page.update()

        button_content = ft.Row([
            ft.Icon(flet_icon, color=ft.Colors.WHITE) if flet_icon else ft.Container(),
            ft.Text(text, color=ft.Colors.WHITE),
        ], tight=True, spacing=5)

        button = ft.Button(
            content=button_content,
            bgcolor=color,
            on_click=on_click,
        )

        return button

    def _build_image_comparison(self, element: dict) -> ft.Control:
        """Build an image comparison element with two images side by side."""
        value_first = element.get("valueFirst", "")
        value_second = element.get("valueSecond", "")
        label = element.get("label", "")

        images_row = ft.Row(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Text("Before", size=12, color=ft.Colors.GREY),
                        ft.Image(
                            src=value_first,
                            fit=ft.ImageFit.CONTAIN,
                            width=200,
                            border_radius=8,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("After", size=12, color=ft.Colors.GREY),
                        ft.Image(
                            src=value_second,
                            fit=ft.ImageFit.CONTAIN,
                            width=200,
                            border_radius=8,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )

        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=12, italic=True) if label else ft.Container(),
                images_row,
            ]),
            padding=10,
        )

    def _build_progress(self, element: dict) -> ft.Control:
        """Build a progress bar element."""
        value = element.get("value")

        # If value is None or 0, show indeterminate progress
        if value is None or value == 0:
            progress_bar = ft.ProgressBar(width=400)
        else:
            # Value should be between 0 and 1
            progress_value = float(value) if isinstance(value, (int, float)) else 0
            progress_bar = ft.ProgressBar(value=progress_value, width=400)

        return ft.Container(
            content=progress_bar,
            padding=10,
        )

    def _build_input_hidden(self, element: dict) -> ft.Control | None:
        """Build a hidden input (stores value in state but not visible)."""
        name = element.get("name", "")
        value = element.get("value", "")

        if name:
            self.app_state.set_value(name, value)

        # Return None as hidden inputs shouldn't be displayed
        return None


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


def load_json_from_env() -> dict:
    """Load JSON configuration from file path specified in .env."""
    json_path = os.getenv("JSON_PATH")

    if not json_path:
        # Default to example file if JSON_PATH not set
        json_path = "examples/example_data.json"
        logger.info(f"JSON_PATH not set in .env, using default: {json_path}")

    # Resolve path relative to script location
    script_dir = Path(__file__).parent
    full_path = script_dir / json_path

    if not full_path.exists():
        raise FileNotFoundError(f"JSON file not found: {full_path}")

    logger.info(f"Loading JSON from: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(page: ft.Page):
    """Main function that initializes the Flet application."""
    # Configure page
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    try:
        # Load JSON configuration
        json_data = load_json_from_env()

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
