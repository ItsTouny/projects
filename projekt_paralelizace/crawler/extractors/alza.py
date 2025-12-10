"""Alza extractor: extract basic product information from Alza product pages."""
from bs4 import BeautifulSoup

def extract_alza(_html: str, url: str):
    """Extract product info from Alza HTML."""
    soup = BeautifulSoup(_html, "html.parser")
    name = soup.find("h1")
    name = name.get_text(strip=True) if name else "Unknown"

    price_elem = soup.find("span", {"class": "price-box__primary-price__value"}) or soup.find("span", {"class": "price"})
    price = price_elem.get_text(strip=True) if price_elem else "N/A"
    price = price.replace("\xa0", " ")


    availability = "unknown"
    for span in soup.find_all("span"):
        text = span.get_text(strip=True)
        if "Skladem" in text:
            availability = text.replace("\xa0", " ").replace("&gt;", ">")
            break

    image_url = "unknown"
    for img in soup.find_all("img"):
        title = img.get("title", "")
        if name.lower() in title.lower():
            image_url = img.get("src", "")
            break

    return {
        "url": url,
        "name": name,
        "price": price,
        "availability": availability,
        "image": image_url,
        "store": "alza"
    }