#!/usr/bin/env python3
"""Entry point for the Product Price Crawler.

Reads configuration and starts the orchestrator which manages the download,
parsing and writing of product data.
"""

import json
from crawler.orchestrator import Orchestrator
import os

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    orchestrator = Orchestrator(config)
    orchestrator.run()
