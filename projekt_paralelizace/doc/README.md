# Parallel Web Crawler

**Author:** Tony Menšík  
**Project:** Parallel Web Crawler  
**Description:**  
This Python project crawls multiple web pages in parallel using multiprocessing. It extracts the **title** and **meta description** of each page and saves the results to a CSV file.

---

## Configuration

The crawler uses a JSON config file located in `config/config.json`.

Example:

```json
{
  "base_domains": [
    "https://example.com",
    "https://www.python.org",
    "https://www.wikipedia.org"
  ],
  "paths": [
    "/",
    "/about",
    "/contact"
  ],
  "num_processes": 3
}
```

## Parameters:

| Parameter     | Description                    |
|---------------|--------------------------------|
| base_domains  | List of domain URLs to crawl   |
| paths         | Paths to append to each domain |
| num_processes | Number of processes to start   |

## Setup Instructions:

1. Install Python 3 (>=3.8 recommended)
2. Install dependencies:

```bash
py -m pip install -r lib/requirements.txt
```

## Run program:

```bash
cd bin
.\run_crawler.bat
```