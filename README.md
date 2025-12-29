# Flet from JSON

A Python Flet application that dynamically builds graphical user interfaces from JSON configuration files.

## Requirements

- Python 3.9 or higher
- Flet 0.80.0 or higher

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

## Project Structure

```
flet_from_json/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment configuration example
├── README.md                  # This file
├── flet_from_json/            # Main package
│   ├── __init__.py            # Package exports
│   ├── state.py               # Application state management (AppState)
│   ├── constants.py           # Color, font size, and icon mappings
│   ├── elements.py            # Element builders (ElementBuilder)
│   ├── builder.py             # JSON UI builder (JsonUIBuilder)
│   └── config.py              # Configuration loading utilities
└── examples/
    └── example_data.json      # Example JSON configuration
```

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
