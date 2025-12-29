"""
Test script to verify the ImageFit -> BoxFit fix works.
This script imports the elements module and verifies it can be imported without error.
"""
import sys
sys.path.insert(0, '/tmp/gh-issue-solver-1767008630206')

print("Testing import of flet_from_json modules...")

# Test 1: Import flet
import flet as ft
print(f"✓ Flet version: {ft.__version__}")

# Test 2: Verify BoxFit exists
print(f"✓ ft.BoxFit.CONTAIN = {ft.BoxFit.CONTAIN}")

# Test 3: Import the elements module - this should not fail anymore
try:
    from flet_from_json.elements import ElementBuilder
    print("✓ ElementBuilder imported successfully")
except AttributeError as e:
    print(f"✗ Import failed with AttributeError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Import failed with unexpected error: {e}")
    sys.exit(1)

# Test 4: Import the builder module
try:
    from flet_from_json.builder import JsonUIBuilder
    print("✓ JsonUIBuilder imported successfully")
except AttributeError as e:
    print(f"✗ Import failed with AttributeError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Import failed with unexpected error: {e}")
    sys.exit(1)

# Test 5: Import the whole package
try:
    from flet_from_json import JsonUIBuilder, load_json_from_env
    print("✓ flet_from_json package imported successfully")
except AttributeError as e:
    print(f"✗ Import failed with AttributeError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Import failed with unexpected error: {e}")
    sys.exit(1)

print()
print("=" * 50)
print("All tests passed! The ImageFit -> BoxFit fix is working.")
print("=" * 50)
