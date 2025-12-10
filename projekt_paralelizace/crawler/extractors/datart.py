"""Datart extractor: datart.cz product pages extractor.

This extractor uses common Datart CSS selectors but keeps fallbacks for robustness.
Selectors may change over time; adjust the extractor if the site HTML changes.
"""
from bs4 import BeautifulSoup

def extract_datart(html: str, url: str):
    """Extract product info from Datart product HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Name: usually in <h1> with class containing 'product-title' or itemprop='name'
    name_elem = soup.find("h1", class_=lambda c: c and 'product' in c and 'title' in c) or soup.find("h1") or soup.find(attrs={"itemprop": "name"})
    name = name_elem.get_text(strip=True) if name_elem else "Unknown"

    # Price: look for common price classes or data-price attributes
    price_elem = soup.find(lambda tag: tag.name in ['span','div'] and tag.get('class') and any('price' in c for c in tag.get('class')))                  or soup.find(attrs={'data-price': True})
    price = price_elem.get_text(strip=True) if price_elem else "N/A"

    # Availability: try common availability labels
    avail_elem = soup.find(lambda tag: tag.get('class') and any('availability' in c or 'stock' in c for c in tag.get('class')))                  or soup.find(text=lambda t: t and ('Skladem' in t or 'Na objednávku' in t or 'Vyprodáno' in t))
    availability = avail_elem.get_text(strip=True) if hasattr(avail_elem, 'get_text') else (avail_elem.strip() if avail_elem else 'Unknown')

    # Image: try meta og:image or common img selectors
    img_meta = soup.find('meta', property='og:image') or soup.find('meta', attrs={'name':'og:image'})
    if img_meta and img_meta.get('content'):
        image_url = img_meta['content']
    else:
        img_elem = soup.find('img', class_=lambda c: c and ('product' in c or 'image' in c)) or soup.find('img')
        image_url = img_elem['src'] if img_elem and img_elem.get('src') else ""

    return {
        "url": url,
        "name": name,
        "price": price,
        "availability": availability,
        "image": image_url,
        "store": "datart"
    }
