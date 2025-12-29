"""
Test script to verify Flet 0.80+ compatibility.
Run this to check if all the Flet APIs used in the codebase are compatible.
"""

import sys


def test_flet_version():
    """Test that we're using Flet 0.80+"""
    import flet as ft
    version = ft.__version__
    major, minor = version.split('.')[:2]
    assert int(major) >= 0 and int(minor) >= 80, f"Expected Flet >= 0.80, got {version}"
    print(f"✓ Flet version: {version}")


def test_filepicker_api():
    """Test FilePicker new API"""
    import flet as ft

    # FilePicker should exist
    assert hasattr(ft, 'FilePicker'), "FilePicker not found"

    # FilePicker should NOT have on_result (deprecated in 0.80+)
    import inspect
    sig = inspect.signature(ft.FilePicker.__init__)
    params = list(sig.parameters.keys())
    assert 'on_result' not in params, "on_result should not be in FilePicker params"

    # pick_files should be async
    fp = ft.FilePicker()
    assert hasattr(fp, 'pick_files'), "pick_files method not found"

    # FilePickerResultEvent should NOT exist
    assert not hasattr(ft, 'FilePickerResultEvent'), "FilePickerResultEvent should not exist in 0.80+"

    print("✓ FilePicker API is compatible with 0.80+")


def test_button_api():
    """Test Button API"""
    import flet as ft

    # Button should work with content=
    btn = ft.Button(content=ft.Text("test"))
    assert btn is not None

    print("✓ Button API is compatible")


def test_page_services():
    """Test that Page has services attribute"""
    import flet as ft

    assert hasattr(ft.Page, 'services'), "Page.services attribute not found"

    print("✓ Page.services exists")


def test_colors_api():
    """Test Colors API"""
    import flet as ft

    assert hasattr(ft.Colors, 'BLACK'), "Colors.BLACK not found"
    assert hasattr(ft.Colors, 'with_opacity'), "Colors.with_opacity not found"
    assert hasattr(ft.Colors, 'BLUE'), "Colors.BLUE not found"
    assert hasattr(ft.Colors, 'GREY'), "Colors.GREY not found"

    print("✓ Colors API is compatible")


def test_icons_api():
    """Test Icons API"""
    import flet as ft

    assert hasattr(ft.Icons, 'UPLOAD_FILE'), "Icons.UPLOAD_FILE not found"

    print("✓ Icons API is compatible")


def test_controls_api():
    """Test various control APIs used in the codebase"""
    import flet as ft

    # Test Text
    text = ft.Text("test", color=ft.Colors.BLACK, size=14)
    assert text is not None

    # Test Image
    image = ft.Image(src="test.png", fit=ft.BoxFit.CONTAIN)
    assert image is not None

    # Test TextField
    tf = ft.TextField(label="test", value="", hint_text="hint")
    assert tf is not None

    # Test Dropdown
    dropdown = ft.Dropdown(
        label="test",
        options=[ft.dropdown.Option(key="1", text="Option 1")],
    )
    assert dropdown is not None

    # Test Row/Column
    row = ft.Row([ft.Text("test")], tight=True, spacing=5)
    assert row is not None

    column = ft.Column([ft.Text("test")], spacing=10)
    assert column is not None

    # Test Container
    container = ft.Container(content=ft.Text("test"), padding=10)
    assert container is not None

    # Test Tabs with TabBar and TabBarView (Flet 0.80+ pattern)
    tabs = ft.Tabs(
        selected_index=0,
        length=2,
        expand=True,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(tabs=[ft.Tab(label="Tab 1"), ft.Tab(label="Tab 2")]),
                ft.TabBarView(
                    expand=True,
                    controls=[ft.Text("Content 1"), ft.Text("Content 2")],
                ),
            ],
        ),
    )
    assert tabs is not None

    # Test SnackBar
    snack = ft.SnackBar(content=ft.Text("test"), open=True)
    assert snack is not None

    # Test Markdown
    md = ft.Markdown("# Test", selectable=True)
    assert md is not None

    # Test ProgressBar
    pb = ft.ProgressBar(width=400)
    assert pb is not None

    print("✓ All controls API are compatible")


def test_import_elements():
    """Test importing the elements module"""
    try:
        from flet_from_json.elements import ElementBuilder
        print("✓ ElementBuilder imports successfully")
    except Exception as e:
        print(f"✗ Failed to import ElementBuilder: {e}")
        sys.exit(1)


def test_import_builder():
    """Test importing the builder module"""
    try:
        from flet_from_json.builder import JsonUIBuilder
        print("✓ JsonUIBuilder imports successfully")
    except Exception as e:
        print(f"✗ Failed to import JsonUIBuilder: {e}")
        sys.exit(1)


def main():
    """Run all compatibility tests"""
    print("=" * 60)
    print("Flet 0.80+ Compatibility Tests")
    print("=" * 60)

    tests = [
        test_flet_version,
        test_filepicker_api,
        test_button_api,
        test_page_services,
        test_colors_api,
        test_icons_api,
        test_controls_api,
        test_import_elements,
        test_import_builder,
    ]

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            sys.exit(1)

    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
