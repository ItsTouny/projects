import csv
import multiprocessing
import time, os, logging
from typing import Dict
from .downloader import Downloader
from .parser import parse_product
from .writer import ensure_dir

class Orchestrator:
    """Main orchestration class for running the crawler."""

    def __init__(self, raw_config: Dict):
        self.raw_config = raw_config
        self.config = raw_config
        self.num_processes = self.config.get('num_processes', 4)
        self.timeout = self.config.get('timeout', 5)
        self.output_dir = self.config.get('output_dir', 'output')
        self.logs_dir = self.config.get('logs_dir', 'logs')
        ensure_dir(self.output_dir)
        ensure_dir(self.logs_dir)

        self.csv_path = os.path.join(self.output_dir, "results.csv")
        self.csv_header = ["url","name","price","availability","image","store","error"]
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.csv_header)

        log_path = os.path.join(self.logs_dir, 'crawler.log')
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s',
                            handlers=[logging.FileHandler(log_path, encoding='utf-8'),
                                      logging.StreamHandler()])
        self.logger = logging.getLogger('projekt_paralelizace')

        manager = multiprocessing.Manager()
        self.lock = manager.Lock()

    def _crawl_one(self, job: Dict):
        """Worker: download HTML and run appropriate extractor; zapisuje přímo do CSV."""
        store_type = job['type']
        url = job['url']
        d = Downloader(timeout=self.timeout)
        html, err = d.fetch(url)
        print(type(html))
        row = {
            'url': url,
            'name': None,
            'price': None,
            'availability': None,
            'image': None,
            'store': store_type,
            'error': err
        }

        if html:
            try:
                product = parse_product(store_type, html, url)
                row.update(product)
                row['error'] = None
            except Exception as e:
                row['error'] = str(e)

        with self.lock:
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
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
        jobs = []
        for store in self.config.get('stores', []):
            for url in store.get('urls', []):
                jobs.append({'type': store.get('type'), 'url': url})

        start = time.time()
        self.logger.info('Starting crawl: %d jobs', len(jobs))
        with multiprocessing.Pool(processes=self.num_processes) as pool:
            pool.map(self._crawl_one, jobs)

        elapsed = time.time() - start
        self.logger.info('Finished crawl: %d products in %.2fs', len(jobs), elapsed)
