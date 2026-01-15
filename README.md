# Country Parser Toolkit

Сбор данных о странах: получаем список стран из RestCountries, парсим инфобокс Википедии, чистим и считаем статистику. Можно использовать как CLI или как библиотеку.

## Быстрый старт
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m parse_algorithm --limit 10 -o output.json
```

CLI выводит JSON со списком стран и статистикой (топ по населению, средняя площадь по часовому поясу, страны с евро). `--timezone` позволяет выбрать целевой часовой пояс (по умолчанию UTC+3).

## API
- `fetch_country_list(api_url=...) -> list[str]` — список стран из RestCountries.
- `generate_country_urls(names) -> list[str]` — ссылки на Википедию.
- `fetch_country_data(url) -> CountryData | None` — парсинг страницы страны.
- `deduplicate_countries(list[CountryData])` — уникализация по имени.
- `compute_stats(countries, target_timezone)` — сводка статистики.
- `parse_infobox(html)` — разбор HTML инфобокса (используется в тестах/офлайн сценариях).

## Тесты
```bash
pytest
```

## Заметки
- Используется `requests` + `beautifulsoup4`.
- CLI сохраняет JSON в файл (если указан `-o`) или выводит в stdout.
- В тестах используется локальный HTML-фрагмент — сеть не требуется. Для реального запуска потребуется интернет.
