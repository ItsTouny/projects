"""Writer utilities for CSV/JSON/SQLite outputs."""
import csv, os, json
from typing import List, Dict

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def write_csv(path: str, rows: List[Dict]):
    """Append dict rows to CSV file; write header if file doesn't exist."""
    ensure_dir(os.path.dirname(path) or ".")
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        if not rows:
            return
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)

def write_json(path: str, rows: List[Dict]):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
