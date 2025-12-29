# Flet from JSON

A Python Flet application that dynamically builds graphical user interfaces from JSON configuration files.

## Requirements

- Python 3.9 or higher
- Flet 0.27.0 or higher

## Installation

1. Clone the repository:
```bash
git clone https://github.com/andchir/flet_from_json.git
cd flet_from_json
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on the example:
```bash
cp .env.example .env
```

4. Edit `.env` to specify your JSON configuration file path:
```
JSON_PATH=examples/example_data.json
```

## Running the Application

```bash
python main.py
```

This will start the Flet application and open a window displaying the UI built from the JSON configuration.

## JSON Format

The application supports the following element types from the JSON configuration:

### Display Elements
- **text** - Text display with optional markdown, colors, borders, and shadows
- **image** - Image display from URL with rounded corners and link support
- **image-comparison** - Side-by-side image comparison (before/after)
- **progress** - Progress bar with determinate or indeterminate modes

### Input Elements
- **input-text** - Single-line text input
- **input-textarea** - Multi-line text input
- **input-select** - Dropdown selection
- **input-file** - File picker with extension filtering
- **input-hidden** - Hidden field for storing values

### Interactive Elements
- **button** - Clickable button with icon and color support

### Features
- **Tabs** - Multi-tab navigation based on JSON `tabs` array
- **Conditional Visibility** - Show/hide elements based on field values using `hiddenByField`
- **Blocks** - Grouped elements with ordering support

## Example JSON Structure

See `examples/example_data.json` for a complete example of the JSON format.

## JSON Format Documentation

For detailed documentation on the JSON format, see:
https://raw.githubusercontent.com/andchir/api2app-frontend/refs/heads/main/docs/JSON_FORMAT.md

## Flet Documentation

For more information about Flet framework:
- https://docs.flet.dev/api-reference/
- https://docs.flet.dev/cookbook/
