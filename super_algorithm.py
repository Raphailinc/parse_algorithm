import requests
from bs4 import BeautifulSoup
import json
import re
import os

def fetch_country_data(url):
    try:
        response = requests.get(url)

        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            infobox = soup.find('table', {'class': 'infobox'})

            name = soup.find('h1', {'id': 'firstHeading'}).text.strip()
            capital = get_wikipedia_field(infobox, ["Capital", "Largest city"])
            area = get_wikipedia_field(infobox, ["Total area", "Area"], parse_area)
            population = get_wikipedia_field(infobox, ["Population", "2022 estimate"], parse_population)
            time_zone = get_wikipedia_field(infobox, "Time zone")
            currency = get_wikipedia_field(infobox, "Currency")
            code = get_wikipedia_field(infobox, ["ISO code", "ISO 3166 code"])

            country_data = {
                "name": name,
                "capital": capital,
                "area": area,
                "population": population,
                "time_zone": time_zone,
                "currency": currency,
                "code": code,
            }

            return country_data

        else:
            print(f"Failed to fetch data from {url}")
            return None
            
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

def get_wikipedia_field(infobox, field_names, parse_function=None):
    try:
        if isinstance(field_names, str):
            field_names = [field_names]

        for field_name in field_names:
            # Ищем элемент с текстом заголовка
            field_element = infobox.find('th', string=re.compile(fr'^\s*•?\s*{re.escape(field_name)}\s*$', flags=re.I))

            if field_element:
                # Ищем следующий элемент td (значение)
                field_value = extract_text_from_element(field_element.find_next('td'))

                if not field_value:
                    # Если значение пусто, попробуем использовать другой метод
                    field_value = extract_text_from_element(field_element.find_next('td'))

                    # Если и этот метод не сработал, попробуем найти ссылки и взять текст из первой
                    if not field_value:
                        links = field_element.find_next('td').find_all('a')
                        if links:
                            field_value = links[0].get_text(strip=True)

                if parse_function:
                    field_value = parse_function(field_value)

                if field_value:
                    return field_value

    except Exception as e:
        print(f"Error: {e}")
        return None

def extract_text_from_element(element):
    try:
        for sup in element.find_all('sup'):
            sup.extract()
        return element.get_text(strip=True)
    except Exception as e:
        print(f"Error extracting text from element: {e}")
        return ""

def parse_area(area_text):
    try:
        area_value = re.search(r'\d[\d,.]*', area_text).group()
        return float(area_value.replace(',', '')) if area_value else 0
    except Exception as e:
        return 0

def parse_population(population_text):
    try:
        population_value = re.search(r'\d[\d,.]*', population_text).group()
        return int(population_value.replace(',', '')) if population_value else 0
    except Exception as e:
        return 0

def get_country_list():
    url = "https://restcountries.com/v2/all"
    response = requests.get(url)

    if response.ok:
        countries = response.json()
        return countries
    else:
        print(f"Failed to fetch country list. Status code: {response.status_code}")
        return None

def generate_country_urls(countries):
    base_url = "https://en.wikipedia.org/wiki/"
    country_urls = [base_url + country["name"] for country in countries]
    return country_urls

# Процедура очистки данных
def clean_data(data):
    # Обработка отсутствующих значений
    for key, value in data.items():
        if value is None or value == "":
            data[key] = "N/A"  # Заменяем отсутствующие значения на "N/A"

    # Преобразование типов данных
    data["area"] = float(data["area"]) if data["area"] != "N/A" else None
    data["population"] = int(data["population"]) if data["population"] != "N/A" else None

    return data

# Процедура удаления дубликатов
def remove_duplicates(data_list):
    unique_data = []
    seen_names = set()

    for data in data_list:
        name = data["name"].lower()  # Приводим к нижнему регистру для исключения дубликатов
        if name not in seen_names:
            seen_names.add(name)
            unique_data.append(data)

    return unique_data

# Процедура выполнения простых запросов
def simple_queries(data_list):
    # Получить список всех стран
    all_countries = [data["name"] for data in data_list]
    print("Список всех стран:", all_countries)

    # Получить информацию о населении страны с наибольшим населением
    countries_with_population = [data for data in data_list if data.get("population") is not None]
    if countries_with_population:
        max_population_country = max(countries_with_population, key=lambda x: x.get("population", 0))
        print("Страна с наибольшим населением:", max_population_country["name"], "Население:", max_population_country["population"])
    else:
        print("Нет данных о населении для сравнения.")

    # Получить список стран с их столицами (исключая страны без информации о столице)
    countries_with_capitals = {data["name"]: data["capital"] for data in data_list if data.get("capital") != "N/A"}
    print("Список стран с их столицами:", countries_with_capitals)

# Процедура выполнения расширенных запросов
def advanced_queries(data_list):
    # Получить среднюю площадь стран в заданном часовом поясе
    target_timezone = "UTC+3"  # Задаём целевой часовой пояс
    countries_in_timezone = [data["name"] for data in data_list if data.get("time_zone") == target_timezone]
    average_area = sum(data.get("area", 0) for data in data_list) / len(data_list)
    print(f"Средняя площадь стран в часовом поясе {target_timezone}: {average_area:.2f} кв. км")

    # Получить список стран, где валютой является евро
    euro_countries = [data["name"] for data in data_list if "Euro" in data.get("currency", "")]
    print("Список стран с валютой в евро:", euro_countries)

def save_to_json(data, output_directory, filename):
    filepath = os.path.join(output_directory, filename)
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

def main():
    countries = get_country_list()

    if countries is not None:
        output_directory = "output_data"  # Specify the output directory
        os.makedirs(output_directory, exist_ok=True)

        country_urls = generate_country_urls(countries[:20])
        country_data_list = []

        for url in country_urls:
            data = fetch_country_data(url)

            if data is not None:
                cleaned_data = clean_data(data)
                country_data_list.append(cleaned_data)
                print(json.dumps(cleaned_data, ensure_ascii=False, indent=2))
            else:
                print(f"Failed to fetch data for {url}")

        # Сохраняем очищенные данные в файл JSON
        save_to_json(country_data_list, output_directory, "cleaned_data.json")

        # Выполняем запросы и сохраняем результаты в JSON-файлах
        simple_queries(country_data_list)
        advanced_queries(country_data_list)

if __name__ == "__main__":
    main()