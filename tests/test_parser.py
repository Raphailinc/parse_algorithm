import json
from pathlib import Path

import pytest

from parse_algorithm.parser import (
    CountryData,
    compute_stats,
    deduplicate_countries,
    parse_infobox,
)


@pytest.fixture
def sample_html():
    path = Path(__file__).parent / "fixtures" / "sample_country.html"
    return path.read_text(encoding="utf-8")


def test_parse_infobox_extracts_fields(sample_html):
    data = parse_infobox(sample_html, name_hint="Sampleland")
    assert data.name == "Sampleland"
    assert data.capital == "Sample City"
    assert data.area == 123456.0
    assert data.population == 9876543
    assert data.time_zone == "UTC+3"
    assert data.currency == "Euro (€)"
    assert data.code == "SPL"


def test_deduplicate_countries():
    countries = [
        CountryData("A", None, None, None, None, None, None),
        CountryData("a", None, None, None, None, None, None),
        CountryData("B", None, None, None, None, None, None),
    ]
    unique = deduplicate_countries(countries)
    assert len(unique) == 2


def test_compute_stats():
    items = [
        CountryData("One", "Cap1", 100.0, 50, "UTC+3", "Euro", None),
        CountryData("Two", "Cap2", 300.0, 150, "UTC+3", "Dollar", None),
        CountryData("Three", "Cap3", 200.0, 250, "UTC+1", "Euro", None),
    ]
    stats = compute_stats(items, target_timezone="UTC+3")
    assert stats["top_population"]["name"] == "Three"
    assert pytest.approx(stats["average_area_in_timezone"], rel=1e-6) == 200.0
    assert "One" in stats["euro_countries"] and "Three" in stats["euro_countries"]
    assert stats["capitals"]["One"] == "Cap1"
