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
    .\venv\Scripts\activate
    cd ..
    py -m venv ../venv
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
  "stores": [
    {
      "name": "alza",
      "type": "alza",
      "urls": [
        "https://www.alza.cz/iphone-17-pro-256gb-stribrna-d13078788.htm",
        "https://www.alza.cz/samsung-galaxy-s25-12gb-256gb-blueblack-d12981191.htm"
      ]
    },
    {
      "name": "mironet",
      "type": "mironet",
      "urls": [
        "https://www.mironet.cz/apple-iphone-17-pro-512gb-stribrna-63-12gb-512gb-ios26+dp773763/"
      ]
    },
    {
      "name": "datart",
      "type": "datart",
      "urls": [
        "https://www.datart.cz/mobilni-telefon-apple-iphone-17-pro-256gb-stribrny-mg8g4sx-a"
      ]
    }
  ],
  "num_processes": 6,
  "timeout": 5,
  "retry_count": 2
}
```