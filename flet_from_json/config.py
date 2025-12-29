"""
Configuration loading utilities for the Flet JSON UI application.
"""

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def load_json_from_env(base_path: Path | None = None) -> dict:
    """Load JSON configuration from file path specified in .env.

    Args:
        base_path: Base path for resolving relative JSON paths.
                   If None, uses the current working directory.

    Returns:
        Parsed JSON configuration as a dictionary.

    Raises:
        FileNotFoundError: If the JSON file doesn't exist.
        json.JSONDecodeError: If the JSON is invalid.
    """
    json_path = os.getenv("JSON_PATH")

    if not json_path:
        # Default to example file if JSON_PATH not set
        json_path = "examples/example_data.json"
        logger.info(f"JSON_PATH not set in .env, using default: {json_path}")

    # Resolve path relative to base_path or current directory
    if base_path is None:
        base_path = Path.cwd()

    full_path = base_path / json_path

    if not full_path.exists():
        raise FileNotFoundError(f"JSON file not found: {full_path}")

    logger.info(f"Loading JSON from: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)
