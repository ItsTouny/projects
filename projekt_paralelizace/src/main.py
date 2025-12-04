"""
Author: Tony Menšík
Project: Parallel Web Crawler
Description: Parallel crawler using multiprocessing.
             Downloads title and meta description for URLs from config,
             writes to CSV, includes detailed prints and checks.
"""

import json
import os
import multiprocessing
import requests
from bs4 import BeautifulSoup
import csv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config", "config.json")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "results.csv")

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

urls = []
for domain in config["base_domains"]:
    for path in config["paths"]:
        urls.append(domain + path)

lock = multiprocessing.Lock()


def crawl_one(url):
    try:
        print(f"Crawling: {url}")
        response = requests.get(url, timeout=(3, 3))
        soup = BeautifulSoup(response.text, "html.parser")

        title = "No title"
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        description = "No description"
        desc_tag = soup.find("meta", {"name": "description"})
        if desc_tag and desc_tag.get("content") and desc_tag["content"].strip() != "":
            description = desc_tag["content"].strip()

        with lock:
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([url, title, description])


    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return (url, "ERROR", str(e))


if __name__ == "__main__":
    num_processes = config["num_processes"]

    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(crawl_one, urls)

    print("Crawling finished. Pool terminated successfully. Program exited.")
