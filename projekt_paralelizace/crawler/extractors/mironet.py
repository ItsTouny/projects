import json
import re
from bs4 import BeautifulSoup

def extract_mironet(_html: str, url: str):
    """Extract product info from Mironet HTML using JSON-LD with HTML fallback."""
    soup = BeautifulSoup(_html, "html.parser")

    # 1. Inicializace proměnných (defaultní hodnoty)
    name = "Unknown"
    price = "N/A"
    availability = "Neznámá"
    image_url = ""

    # 2. Extrakce Názvu (HTML H1 je spolehlivé)
    h1_elem = soup.find("h1")
    if h1_elem:
        name = h1_elem.get_text(strip=True)

    # ---------------------------------------------------------
    # 3. PRIMÁRNÍ METODA: JSON-LD (Strukturovaná data)
    # ---------------------------------------------------------
    json_scripts = soup.find_all("script", type="application/ld+json")
    json_success = False

    for script in json_scripts:
        try:
            data = json.loads(script.get_text())

            # Hledáme objekt typu Product
            if isinstance(data, list):
                product_data = next((item for item in data if item.get("@type") == "Product"), None)
            else:
                product_data = data if data.get("@type") == "Product" else None

            if product_data:
                # -- Obrázek z JSONu (bývá nejkvalitnější) --
                if "image" in product_data:
                    img_data = product_data["image"]
                    if isinstance(img_data, list):
                        image_url = img_data[0]
                    elif isinstance(img_data, str):
                        image_url = img_data

                # -- Nabídky (Cena a Dostupnost) --
                if "offers" in product_data:
                    offers = product_data["offers"]
                    # Pokud je více nabídek, vezmeme první
                    if isinstance(offers, list):
                        offers = offers[0]

                    # Cena
                    if "price" in offers:
                        price = str(offers["price"]) + ",-" # Převedeme na string

                    # Dostupnost (URL schema.org)
                    avail_url = offers.get("availability", "")
                    if "InStock" in avail_url:
                        availability = "Skladem"
                    elif "OutOfStock" in avail_url or "Discontinued" in avail_url:
                        availability = "Nedostupné"
                    elif "PreOrder" in avail_url:
                        availability = "Předobjednávka"

                    json_success = True
                    break # Máme data, končíme cyklus
        except:
            continue


    return {
        "url": url,
        "name": name,
        "price": price,
        "availability": availability,
        "image": image_url,
        "store": "mironet"
    }