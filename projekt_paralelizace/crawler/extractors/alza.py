import json
from bs4 import BeautifulSoup


def extract_alza(_html: str, url: str) -> dict:
    """
    Extracts product information (name, price, availability, image) from Alza.cz HTML.

    This function prioritizes extracting structured data (JSON-LD) for reliability.
    It handles specific Alza image object structures found in JSON-LD.

    Args:
        _html (str): The raw HTML content of the product page.
        url (str): The URL of the product page.

    Returns:
        dict: A dictionary containing the extracted product details:
            - url (str): The original product URL.
            - name (str): The product name.
            - price (str): The product price or 'N/A'.
            - availability (str): Stock status (e.g., 'Skladem', 'Nedostupné').
            - image (str): URL of the product image.
            - store (str): Fixed string 'alza'.
    """
    soup = BeautifulSoup(_html, "html.parser")

    name = "Unknown"
    price = "N/A"
    availability = "Neznámá"
    image_url = ""

    h1_elem = soup.find("h1")
    if h1_elem:
        name = h1_elem.get_text(strip=True)

    json_scripts = soup.find_all("script", type="application/ld+json")

    for script in json_scripts:
        try:
            data = json.loads(script.get_text())

            if isinstance(data, list):
                product_data = next((item for item in data if item.get("@type") == "Product"), None)
            else:
                product_data = data if data.get("@type") == "Product" else None

            if product_data:
                if "image" in product_data:
                    img_data = product_data["image"]

                    if isinstance(img_data, list) and len(img_data) > 0:
                        first_item = img_data[0]
                        if isinstance(first_item, dict):
                            image_url = first_item.get("url", "")
                        else:
                            image_url = str(first_item)
                    elif isinstance(img_data, dict):
                        image_url = img_data.get("url", "")
                    elif isinstance(img_data, str):
                        image_url = img_data

                if "offers" in product_data:
                    offers = product_data["offers"]
                    if isinstance(offers, list):
                        offers = offers[0]

                    if "price" in offers:
                        price = str(offers["price"])+",-"

                    avail_url = offers.get("availability", "")
                    if "InStock" in avail_url:
                        availability = "Skladem"
                    elif "OutOfStock" in avail_url or "Discontinued" in avail_url:
                        availability = "Nedostupné"
                    elif "PreOrder" in avail_url:
                        availability = "Předobjednávka"

                    break
        except:
            continue

    return {
        "url": url,
        "name": name,
        "price": price,
        "availability": availability,
        "image": image_url,
        "store": "alza"
    }