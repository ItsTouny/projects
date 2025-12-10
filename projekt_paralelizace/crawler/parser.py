"""Parser that selects the correct extractor per store type."""
from .extractors.alza import extract_alza
from .extractors.mall import extract_mall
from .extractors.datart import extract_datart

EXTRACTOR_MAP = {
    "alza": extract_alza,
    "mall": extract_mall,
    "datart": extract_datart
}

def parse_product(store_type: str, html: str, url: str):
    """Run the extractor for the given store_type on the provided HTML."""
    extractor = EXTRACTOR_MAP.get(store_type)
    if extractor is None:
        raise ValueError(f"Unknown store type: {store_type}")
    return extractor(html,url)
