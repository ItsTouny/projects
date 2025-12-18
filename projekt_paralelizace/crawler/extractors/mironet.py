import json
from bs4 import BeautifulSoup


def extract_mironet(_html: str, url: str) -> dict:
    soup = BeautifulSoup(_html, "html.parser")

    name = "Unknown"
    price = "N/A"
    availability = "Neznámá"
    image_url = ""

    h1_elem = soup.find("h1")
    if h1_elem is not None:
        name = h1_elem.get_text(strip=True)

    json_scripts = soup.find_all("script", type="application/ld+json")

    for script in json_scripts:
        try:
            script_text = script.get_text()
            data = json.loads(script_text)

            product_data = None

            if isinstance(data, list):
                for item in data:
                    if not isinstance(item, dict):
                        continue

                    item_type = item.get("@type")
                    if item_type == "Product":
                        product_data = item
                        break

            elif isinstance(data, dict):
                if data.get("@type") == "Product":
                    product_data = data

            if product_data is not None:

                image_field = product_data.get("image")

                if isinstance(image_field, list) and len(image_field) > 0:
                    image_url = image_field[0]
                elif isinstance(image_field, str):
                    image_url = image_field

                offers = product_data.get("offers")

                if isinstance(offers, list) and len(offers) > 0:
                    offers = offers[0]

                if isinstance(offers, dict):

                    if "price" in offers:
                        price = str(offers["price"]) + ",-"

                    availability_url = offers.get("availability", "")

                    if "InStock" in availability_url:
                        availability = "Skladem"
                    elif "OutOfStock" in availability_url:
                        availability = "Nedostupné"
                    elif "Discontinued" in availability_url:
                        availability = "Nedostupné"
                    elif "PreOrder" in availability_url:
                        availability = "Předobjednávka"

                break

        except Exception:
            continue

    return {
        "url": url,
        "name": name,
        "price": price,
        "availability": availability,
        "image": image_url,
        "store": "mironet"
    }
