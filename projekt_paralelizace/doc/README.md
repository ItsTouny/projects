# Product Price Crawler

**Author:** Tony Menšík

A high-performance, concurrent product price crawler designed to extract real-time product information (name, price, availability, stock status, and images) from major Czech e-commerce sites. The system is built with modularity and robustness in mind, featuring site-specific extractors, anti-bot bypass mechanisms, and multiprocessing support.

## 🚀 Features

* **Multi-Site Support:** Specialized extractors for **Alza.cz**, **Datart.cz**, and **Mironet.cz**.
* **Anti-Bot Evasion:** Uses TLS fingerprinting (Chrome simulation) and session warm-up to bypass basic protections.
* **Reliable Parsing:** Prioritizes **JSON-LD** structured data extraction for stability against HTML layout changes.
* **High Performance:** Utilizes `multiprocessing` to crawl multiple URLs concurrently.
* **Robust Architecture:** Includes automatic retries, timeouts, and comprehensive error logging.
* **Clean Output:** Aggregates all data into a standardized CSV format.
* **Test Suite:** Includes unit tests for validation of parsing logic.

## 🛠️ Installation

1.  **Clone the repository and enter the directory:**
    ```bash
    git clone https://github.com/ItsTouny/projects.git
    cd projekt_paralelizace
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    py -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    py -m pip install -r lib/requirements.txt
    ```

4. **Run crawler:**
    ```bash
    python main.py
    ```

## ⚙️ Configuration

The crawler is driven by a configuration file located at `config/config.json`. You can define the URLs to crawl and system parameters here.

**Example `config.json`:**
```json
{
  "num_processes": 4,
  "timeout": 15,
  "output_dir": "output",
  "logs_dir": "logs",
  "stores": [
    {
      "type": "alza",
      "urls": [
        "[https://www.alza.cz/iphone-15-pro-128gb-cerny-titan-d7899797.htm](https://www.alza.cz/iphone-15-pro-128gb-cerny-titan-d7899797.htm)"
      ]
    },
    {
      "type": "mironet",
      "urls": [
        "[https://www.mironet.cz/apple-iphone-15-128gb-cerna-61-oled-super-retina-xdr-2556x1179-a16-bionic-6gb-ram-128gb+dp597255/](https://www.mironet.cz/apple-iphone-15-128gb-cerna-61-oled-super-retina-xdr-2556x1179-a16-bionic-6gb-ram-128gb+dp597255/)"
      ]
    }
  ]
}