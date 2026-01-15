from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup


API_URL = "https://restcountries.com/v2/all"
WIKI_BASE = "https://en.wikipedia.org/wiki/"


@dataclass
class CountryData:
    name: str
    capital: Optional[str]
    area: Optional[float]
    population: Optional[int]
    time_zone: Optional[str]
    currency: Optional[str]
    code: Optional[str]

    def to_dict(self) -> dict:
        return asdict(self)


def _clean_text(element) -> str:
    if element is None:
        return ""
    for sup in element.find_all("sup"):
        sup.decompose()
    return element.get_text(strip=True)


def _find_field(infobox, labels: Iterable[str]):
    for label in labels:
        th = infobox.find("th", string=re.compile(rf"^\s*•?\s*{re.escape(label)}\s*$", flags=re.I))
        if th:
            td = th.find_next("td")
            if td:
                text = _clean_text(td)
                if not text:
                    links = td.find_all("a")
                    if links:
                        text = links[0].get_text(strip=True)
                if text:
                    return text
    return ""


def _parse_number(text: str) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"\d[\d,.]*", text)
    if not match:
        return None
    raw = match.group().replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return None


def parse_infobox(html: str, name_hint: Optional[str] = None) -> CountryData:
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        raise ValueError("Infobox table not found")

    name = name_hint or _clean_text(soup.find("h1", {"id": "firstHeading"}))
    capital = _find_field(infobox, ["Capital", "Largest city"]) or None
    area = _parse_number(_find_field(infobox, ["Total area", "Area"]))
    population = _parse_number(_find_field(infobox, ["Population", "2022 estimate", "2023 estimate"]))
    population = int(population) if population is not None else None
    time_zone = _find_field(infobox, ["Time zone", "Timezones", "Time zone(s)"]) or None
    currency = _find_field(infobox, ["Currency", "Currencies"]) or None
    code = _find_field(infobox, ["ISO code", "ISO 3166 code", "ISO 3166-1 alpha-3"]) or None

    return CountryData(
        name=name,
        capital=capital,
        area=area,
        population=population,
        time_zone=time_zone,
        currency=currency,
        code=code,
    )


def fetch_country_data(url: str, session: Optional[requests.Session] = None) -> Optional[CountryData]:
    sess = session or requests.Session()
    try:
        resp = sess.get(url, timeout=15)
        resp.raise_for_status()
        return parse_infobox(resp.text)
    except Exception:
        return None


def fetch_country_list(api_url: str = API_URL, session: Optional[requests.Session] = None) -> List[str]:
    sess = session or requests.Session()
    resp = sess.get(api_url, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return [item["name"] for item in data if "name" in item]


def generate_country_urls(names: Iterable[str]) -> List[str]:
    return [WIKI_BASE + name.replace(" ", "_") for name in names]


def deduplicate_countries(countries: Iterable[CountryData]) -> List[CountryData]:
    unique = {}
    for c in countries:
        key = c.name.lower()
        if key not in unique:
            unique[key] = c
    return list(unique.values())


def compute_stats(countries: Iterable[CountryData], target_timezone: Optional[str] = None) -> dict:
    items = list(countries)
    populations = [c for c in items if c.population]
    top_population = max(populations, key=lambda x: x.population) if populations else None

    caps = {c.name: c.capital for c in items if c.capital}
    avg_area = None
    if target_timezone:
        filtered = [c.area for c in items if c.time_zone == target_timezone and c.area]
        if filtered:
            avg_area = sum(filtered) / len(filtered)

    euro_countries = [c.name for c in items if c.currency and "euro" in c.currency.lower()]

    return {
        "countries": [c.name for c in items],
        "capitals": caps,
        "top_population": top_population.to_dict() if top_population else None,
        "average_area_in_timezone": avg_area,
        "euro_countries": euro_countries,
    }


def save_to_json(data, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
