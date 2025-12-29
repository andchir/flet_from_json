"""
Experiment script to test BoxFit usage in Flet.
"""
import flet as ft

print(f"Flet version: {ft.__version__}")
print()

# Test BoxFit
print("Testing ft.BoxFit:")
print(f"  ft.BoxFit = {ft.BoxFit}")
print(f"  ft.BoxFit.CONTAIN = {ft.BoxFit.CONTAIN}")
print(f"  ft.BoxFit.COVER = {ft.BoxFit.COVER}")
print(f"  ft.BoxFit.FILL = {ft.BoxFit.FILL}")
print()

# Test creating an image with BoxFit
print("Testing ft.Image with BoxFit:")
img = ft.Image(
    src="test.png",
    fit=ft.BoxFit.CONTAIN,
)
print(f"  Image created successfully with fit={img.fit}")

# All BoxFit values
print()
print("All BoxFit values:")
for value in ft.BoxFit:
    print(f"  {value.name} = {value.value}")
