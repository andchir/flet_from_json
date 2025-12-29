"""
Experiment script to test different ways to access ImageFit in Flet.
This helps determine the correct API for different Flet versions.
"""
import flet as ft

try:
    print(f"Flet version: {ft.__version__}")
except:
    print("Flet version: unknown")
print()

# Test different ways to access ImageFit
print("Testing ft.ImageFit:")
try:
    print(f"  ft.ImageFit = {ft.ImageFit}")
    print(f"  ft.ImageFit.CONTAIN = {ft.ImageFit.CONTAIN}")
except AttributeError as e:
    print(f"  Error: {e}")

print()
print("Testing ft.Image.fit with string value:")
try:
    # Some versions accept string values
    img = ft.Image(src="test.png", fit="contain")
    print(f"  String 'contain' works")
except Exception as e:
    print(f"  Error: {e}")

print()
print("Looking for ImageFit in flet module:")
image_fit_attrs = [attr for attr in dir(ft) if 'fit' in attr.lower() or 'image' in attr.lower()]
print(f"  Related attributes: {image_fit_attrs}")

print()
print("Looking for enums in flet module:")
enum_attrs = [attr for attr in dir(ft) if not attr.startswith('_') and attr[0].isupper()]
print(f"  Public classes/enums: {[a for a in enum_attrs[:50]]}")  # Show first 50

print()
print("Checking ft.Image class signature:")
try:
    import inspect
    sig = inspect.signature(ft.Image.__init__)
    print(f"  Image.__init__ params: {list(sig.parameters.keys())}")
except Exception as e:
    print(f"  Error: {e}")

print()
print("Looking for 'fit' related types:")
for attr in dir(ft):
    if 'fit' in attr.lower():
        obj = getattr(ft, attr)
        print(f"  ft.{attr} = {obj}")
