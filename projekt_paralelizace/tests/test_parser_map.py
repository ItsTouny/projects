from crawler.parser import EXTRACTOR_MAP
def test_map_contains_all():
    assert 'alza' in EXTRACTOR_MAP
    assert 'mall' in EXTRACTOR_MAP
    assert 'datart' in EXTRACTOR_MAP
