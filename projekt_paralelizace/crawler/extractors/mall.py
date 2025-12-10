"""Mall.cz extractor: extract product information from Mall.cz product pages."""
from bs4 import BeautifulSoup

def extract_mall(html: str, url: str):
    """Extract product info from Mall.cz HTML."""
    soup = BeautifulSoup(html, "html.parser")

    name_elem = soup.find("h1", class_="product-detail__name")
    name = name_elem.get_text(strip=True) if name_elem else "Unknown"

    price_elem = soup.find("span", class_="price__price") or soup.find("span", class_="price")
    price = price_elem.get_text(strip=True) if price_elem else "N/A"

    avail_elem = (soup.find("span", class_="availability__text") or soup.find("span", class_="availability-message"))
    availability = avail_elem.get_text(strip=True) if avail_elem else "Unknown"

    img_elem = soup.find("img", class_="gallery-image") or soup.find("img", class_="product-images__image")
    image_url = img_elem["src"] if img_elem and img_elem.get("src") else ""

    return {
        "url": url,
        "name": name,
        "price": price,
        "availability": availability,
        "image": image_url,
        "store": "mall"
    }
