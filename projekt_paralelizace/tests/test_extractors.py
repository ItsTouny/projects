"""Unit tests for extractors: alza, datart, mironet.

These tests validate STRICTLY the JSON-LD parsing logic.
Since HTML fallbacks were removed, missing JSON must result in default values (N/A).
"""

from crawler.extractors.alza import extract_alza
from crawler.extractors.mironet import extract_mironet
from crawler.extractors.datart import extract_datart

# ============================================================================
#                                   ALZA TESTS
# ============================================================================

def test_alza_json_ld_standard():
    html = """
    <html>
        <body>
            <h1>iPhone 15</h1>
            <script type="application/ld+json">
            {
                "@context": "http://schema.org/",
                "@type": "Product",
                "name": "iPhone 15",
                "image": "https://img.alza.cz/foto.jpg",
                "offers": {
                    "@type": "Offer",
                    "price": "29990",
                    "availability": "http://schema.org/InStock"
                }
            }
            </script>
        </body>
    </html>
    """
    res = extract_alza(html, 'https://alza.test/p')
    assert res['name'] == 'iPhone 15'  # From H1
    assert res['price'] == '29990,-'
    assert res['availability'] == 'Skladem'
    assert res['image'] == 'https://img.alza.cz/foto.jpg'

def test_alza_image_object_structure():
    html = """
    <html>
        <body>
            <h1>Samsung TV</h1>
            <script type="application/ld+json">
            {
                "@type": "Product",
                "image": [
                    {
                        "@type": "ImageObject",
                        "url": "https://image.alza.cz/products/SAMO0269c5.jpg",
                        "name": "Hlavní obrázek"
                    }
                ]
            }
            </script>
        </body>
    </html>
    """
    res = extract_alza(html, 'url')
    assert res['image'] == 'https://image.alza.cz/products/SAMO0269c5.jpg'

def test_alza_missing_json():
    html = """
    <html>
        <body>
            <h1>Just Name</h1>
            <span class="price-box__primary-price__value">100 Kč</span>
            <span>Skladem</span>
        </body>
    </html>
    """
    res = extract_alza(html, 'url')
    assert res['name'] == 'Just Name'
    assert res['price'] == 'N/A'          # HTML is ignored
    assert res['availability'] == 'Neznámá'
    assert res['image'] == ''

# ============================================================================
#                                  DATART TESTS
# ============================================================================

def test_datart_json_list_format():
    html = """
    <html>
        <body>
            <h1>Datart Washer</h1>
            <script type="application/ld+json">
            [
                { "@type": "BreadcrumbList" },
                {
                    "@type": "Product",
                    "image": "https://img.datart.cz/washer.jpg",
                    "offers": {
                        "price": 12000,
                        "availability": "http://schema.org/OutOfStock"
                    }
                }
            ]
            </script>
        </body>
    </html>
    """
    res = extract_datart(html, 'url')
    assert res['price'] == '12000,-'
    assert res['availability'] == 'Nedostupné'
    assert res['image'] == 'https://img.datart.cz/washer.jpg'

def test_datart_missing_json():
    html = """
    <html>
        <body>
            <h1>Datart HTML Only</h1>
            <div class="price-box__price">500 Kč</div>
        </div>
    </html>
    """
    res = extract_datart(html, 'url')
    assert res['name'] == 'Datart HTML Only'
    assert res['price'] == 'N/A'
    assert res['availability'] == 'Neznámá'

# ============================================================================
#                                 MIRONET TESTS
# ============================================================================

def test_mironet_json_price_formatting():
    html = """
    <html>
        <body>
            <h1>Mironet GPU</h1>
            <script type="application/ld+json">
            {
                "@type": "Product",
                "offers": {
                    "price": "45000",
                    "availability": "http://schema.org/PreOrder"
                }
            }
            </script>
        </body>
    </html>
    """
    res = extract_mironet(html, 'url')
    assert res['price'] == '45000,-'
    assert res['availability'] == 'Předobjednávka'

def test_mironet_missing_json():
    html = """
    <html>
        <body>
            <h1>Mironet No JSON</h1>
            <span class="product_dph">100 Kč</span>
        </body>
    </html>
    """
    res = extract_mironet(html, 'url')
    assert res['name'] == 'Mironet No JSON'
    assert res['price'] == 'N/A'
    assert res['availability'] == 'Neznámá'