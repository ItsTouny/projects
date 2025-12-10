# Product Price Crawler — Extended Project

**Author:** Tony Menšík

This project is a product price crawler that extracts product information (name, price, availability, image) from multiple e-shops concurrently. It is modular, has per-site extractors, supports multiprocessing, retry/backoff, CSV output , logging, and unit tests.

## Quick start

1. Create virtualenv and install requirements:
```bash
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

2. Edit `config/config.json` with the stores and URLs you want to crawl.

3. Run:
```bash
python main.py
```

4. Run tests:
```bash
pytest -q
```

The output files are written to `output/` and logs to `logs/`.
