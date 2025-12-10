"""Configuration loader module.

Provides a dataclass `CrawlerConfig` and helper to load configuration from a dict.
All docstrings are in English for documentation and clarity.
"""
from dataclasses import dataclass, field
from typing import List

@dataclass
class CrawlerConfig:
    """Holds crawler configuration parameters."""
    base_domains: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    num_processes: int = 4
    user_agent: str = "ProductCrawler/1.0"
    timeout: int = 5
    retry_count: int = 2
    backoff_factor: float = 1.0
    save_html: bool = False
    export_format: str = "csv"
    output_dir: str = "output"
    logs_dir: str = "logs"
    resume: bool = True

def load_config_from_dict(raw: dict) -> CrawlerConfig:
    """Create CrawlerConfig from a raw dict (e.g. loaded JSON)."""
    return CrawlerConfig(
        base_domains = raw.get("base_domains", []),
        paths = raw.get("paths", []),
        num_processes = raw.get("num_processes", 4),
        user_agent = raw.get("user_agent", "ProductCrawler/1.0"),
        timeout = raw.get("timeout", 5),
        retry_count = raw.get("retry_count", 2),
        backoff_factor = raw.get("backoff_factor", 1.0),
        save_html = raw.get("save_html", False),
        export_format = raw.get("export_format", "csv"),
        output_dir = raw.get("output_dir", "output"),
        logs_dir = raw.get("logs_dir", "logs"),
        resume = raw.get("resume", True)
    )
