"""Alza extractor: extract basic product information from Alza product pages."""
import json
import re

from bs4 import BeautifulSoup

def extract_mironet(_html: str, url: str):
    """Extract product info from Alza HTML."""
    soup = BeautifulSoup(_html, "html.parser")
    name = soup.find("h1")
    name = name.get_text(strip=True) if name else "Unknown"

    price_elem = soup.find("span", {"class": "product_dph"}) or soup.find("span", {"class": "price"})
    price = price_elem.get_text(strip=True) if price_elem else "N/A"
    price = price.replace("\xa0", " ")

    # 1. METODA: JSON-LD (Strukturovaná data pro Google)
    # Toto je nejčistší způsob. E-shopy to tam mít MUSÍ.
    json_scripts = soup.find_all("script", type="application/ld+json")

    found_data = False

    for script in json_scripts:
        try:
            data = json.loads(script.get_text())

            # Někdy je to seznam, někdy slovník
            if isinstance(data, list):
                # Hledáme objekt, který je typu "Product"
                product_data = next((item for item in data if item.get("@type") == "Product"), None)
            else:
                product_data = data if data.get("@type") == "Product" else None

            if product_data and "offers" in product_data:
                offers = product_data["offers"]

                # Cena
                price = offers.get("price")
                currency = offers.get("priceCurrency")

                # Dostupnost (bývá jako URL "http://schema.org/InStock")
                availability_url = offers.get("availability", "")

                status = "Neznámý"
                if "InStock" in availability_url:
                    status = "✅ Skladem"
                elif "OutOfStock" in availability_url:
                    status = "❌ Vyprodáno"
                elif "PreOrder" in availability_url:
                    status = "🕒 Předobjednávka"

                print(f"--- DATA Z JSON-LD ---")
                print(f"Cena: {price} {currency}")
                print(f"Status: {status} ({availability_url})")
                found_data = True
                break

        except Exception as e:
            continue
    """for child in availability_elem.children:
        availability = child.get_text(strip=True) if child else "N/A"""

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
        "store": "mironet"
    }