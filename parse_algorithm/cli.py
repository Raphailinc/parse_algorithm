from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

from .parser import (
    compute_stats,
    deduplicate_countries,
    fetch_country_data,
    fetch_country_list,
    generate_country_urls,
    save_to_json,
)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch and parse country data from Wikipedia.")
    parser.add_argument("-n", "--limit", type=int, default=20, help="How many countries to process.")
    parser.add_argument("-o", "--output", type=Path, help="Path to save JSON results.")
    parser.add_argument("--timezone", type=str, default="UTC+3", help="Timezone for avg area stat.")
    parser.add_argument("--api-url", type=str, default=None, help="Custom restcountries API URL.")
    args = parser.parse_args(argv)

    session = requests.Session()
    api_url = args.api_url or None
    try:
        names = fetch_country_list(api_url=api_url or None, session=session)
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to fetch country list: {exc}", file=sys.stderr)
        return 1

    if args.limit:
        names = names[: args.limit]

    urls = generate_country_urls(names)
    countries = []
    for url in urls:
        data = fetch_country_data(url, session=session)
        if data:
            countries.append(data)
            print(f"Parsed: {data.name}")
        else:
            print(f"Skipped (failed): {url}", file=sys.stderr)

    countries = deduplicate_countries(countries)
    stats = compute_stats(countries, target_timezone=args.timezone)

    payload = {
        "countries": [c.to_dict() for c in countries],
        "stats": stats,
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        save_to_json(payload, str(args.output))
        print(f"Saved to {args.output}")
    else:
        import json

        print(json.dumps(payload, ensure_ascii=False, indent=2))

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":  # pragma: no cover
    main()
