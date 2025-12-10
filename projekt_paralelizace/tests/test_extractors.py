"""Unit tests for extractors: alza, mall, datart.

These tests use small HTML snippets to validate the parsing logic.
"""
from crawler.extractors.alza import extract_alza
from crawler.extractors.mall import extract_mall
from crawler.extractors.datart import extract_datart

def test_alza_basic():
    html = "<html><head><title>Prod</title></head><body><h1>Name A</h1><span class='price-box__primary-price__value'>123 Kč</span></body></html>"
    res = extract_alza(html, 'https://alza.test/p')
    assert res['name'] == 'Name A'
    assert '123' in res['price']

def test_mall_basic():
    html = "<html><body><h1 class='product-detail__name'>MName</h1><span class='price__price'>1 234 Kč</span></body></html>"
    res = extract_mall(html, 'https://mall.test/p')
    assert res['name'] == 'MName'
    assert '1 234' in res['price']

def test_datart_basic():
    html = "<html><head><meta property='og:image' content='https://img'></head><body><h1 class='product-title'>DName</h1><span class='price'>2 000 Kč</span><span class='availability__text'>Skladem</span></body></html>"
    res = extract_datart(html, 'https://datart.test/p')
    assert res['name'] == 'DName'
    assert '2 000' in res['price']
    assert res['availability'] == 'Skladem'
