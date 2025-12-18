import csv
import multiprocessing
import time
import os
import logging
from typing import Dict

from .downloader import Downloader
from .parser import parse_product
from .writer import ensure_dir


class Orchestrator:
    """
    Main orchestration class for running the crawler.

    It manages the configuration, logging, worker process pool, and synchronizes
    writing results to the output CSV file.
    """

    def __init__(self, raw_config: Dict):
        """
        Initializes the Orchestrator with the given configuration.

        Args:
            raw_config (Dict): The configuration dictionary containing settings
                               for stores, timeouts, and output directories.
        """
        self.raw_config = raw_config
        self.config = raw_config

        self.num_processes = self.config.get("num_processes", 4)
        self.timeout = self.config.get("timeout", 5)
        self.output_dir = self.config.get("output_dir", "output")
        self.logs_dir = self.config.get("logs_dir", "logs")

        ensure_dir(self.output_dir)
        ensure_dir(self.logs_dir)

        self.csv_path = os.path.join(self.output_dir, "results.csv")
        self.csv_header = [
            "url",
            "name",
            "price",
            "availability",
            "image",
            "store",
            "error"
        ]

        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

            with open(self.csv_path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(self.csv_header)

        log_path = os.path.join(self.logs_dir, "crawler.log")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            handlers=[
                logging.FileHandler(log_path, encoding="utf-8"),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger("projekt_paralelizace")

        manager = multiprocessing.Manager()
        self.lock = manager.Lock()

    def _crawl_one(self, job: Dict):
        """
        Worker method used by the multiprocessing pool.

        It downloads the HTML for a single job, parses the product data,
        and safely writes the result (or error) to the shared CSV file
        using a lock.

        Args:
            job (Dict): A dictionary containing the 'url' and store 'type'.
        """
        store_type = job.get("type")
        url = job.get("url")

        downloader = Downloader(timeout=self.timeout)
        html, error = downloader.fetch(url)

        row = {
            "url": url,
            "name": None,
            "price": None,
            "availability": None,
            "image": None,
            "store": store_type,
            "error": error
        }

        if html is not None:
            try:
                product = parse_product(store_type, html, url)
                row.update(product)
                row["error"] = None
            except Exception as exc:
                row["error"] = str(exc)

        with self.lock:
            with open(self.csv_path, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    row["url"],
                    row["name"],
                    row["price"],
                    row["availability"],
                    row["image"],
                    row["store"],
                    row["error"]
                ])

    def run(self):
        """
        Prepares the jobs from configuration and executes the crawling process
        using a parallel process pool.
        """
        jobs = []

        stores = self.config.get("stores", [])
        for store in stores:
            store_type = store.get("type")
            urls = store.get("urls", [])

            for url in urls:
                jobs.append({
                    "type": store_type,
                    "url": url
                })

        start_time = time.time()

        self.logger.info("Starting crawl: %d jobs", len(jobs))

        with multiprocessing.Pool(processes=self.num_processes) as pool:
            pool.map(self._crawl_one, jobs)

        elapsed = time.time() - start_time

        self.logger.info(
            "Finished crawl: %d products in %.2fs",
            len(jobs),
            elapsed
        )
