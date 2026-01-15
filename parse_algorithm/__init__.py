"""
Country data scraping and parsing helpers.

Key functions:
- fetch_country_data(url, session=None): scrape a Wikipedia page into CountryData.
- fetch_country_list(api_url): fetch names from restcountries.
- generate_country_urls(names): build Wikipedia URLs.
- deduplicate_countries(), compute_stats(): clean and analyse results.
"""

from .parser import (
    CountryData,
    compute_stats,
    deduplicate_countries,
    fetch_country_data,
    fetch_country_list,
    generate_country_urls,
    parse_infobox,
)

__all__ = [
    "CountryData",
    "compute_stats",
    "deduplicate_countries",
    "fetch_country_data",
    "fetch_country_list",
    "generate_country_urls",
    "parse_infobox",
]
