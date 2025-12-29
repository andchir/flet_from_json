"""
Element builders for creating Flet controls from JSON definitions.
"""

import logging

import flet as ft

from .constants import COLOR_MAP, FONT_SIZE_MAP, ICON_MAP
from .state import AppState

logger = logging.getLogger(__name__)


class ElementBuilder:
    """Builds Flet controls from JSON element definitions."""

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
        color = COLOR_MAP.get(element.get("color", "Black"), ft.Colors.BLACK)
        font_size = FONT_SIZE_MAP.get(element.get("fontSize", "Medium"), 14)

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
            fit=ft.BoxFit.CONTAIN,
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
            self.page.services.append(self.file_picker)

        # Create a text field to display selected file name
        file_text = ft.Text(placeholder, italic=True, color=ft.Colors.GREY)

        async def pick_files(e):
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

            # In Flet 0.80+, pick_files is async and returns the result directly
            files = await self.file_picker.pick_files(
                allow_multiple=multiple,
                allowed_extensions=allowed_extensions,
            )

            if files:
                file_names = ", ".join([f.name for f in files])
                file_text.value = file_names
                self.app_state.set_value(name, [f.path for f in files])
            else:
                file_text.value = placeholder
                self.app_state.set_value(name, [])

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
        color = COLOR_MAP.get(element.get("color", "Blue"), ft.Colors.BLUE)
        icon_name = element.get("icon", "")

        flet_icon = ICON_MAP.get(icon_name) if icon_name else None

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
                            fit=ft.BoxFit.CONTAIN,
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
                            fit=ft.BoxFit.CONTAIN,
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
