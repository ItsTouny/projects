"""Configuration loader module.

Loads configuration from a JSON file directly into a Python dictionary.
"""
import json
import os
from typing import Dict, Any

def load_config(path: str = "config/config.json") -> Dict[str, Any]:
    """
    Load configuration from a JSON file.

    Returns a dictionary with the config values. It also sets default values
    for paths (output/logs) if they are missing in the JSON.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if "output_dir" not in config:
        config["output_dir"] = "output"

    if "logs_dir" not in config:
        config["logs_dir"] = "logs"

    if "num_processes" not in config:
        config["num_processes"] = 4

    return config