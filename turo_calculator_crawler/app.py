from concurrent.futures import ProcessPoolExecutor
from instance.config import app_config
import requests

from bs4 import BeautifulSoup
from instance.config import app_config
from db.TuroDB import TuroDB


app_config = app_config.get('development')()


CANARY_URL = "https://turo.com/us/en/carculator?country=US&deliveryOffered=true&make={make}&marketAreaId=104&model=Camry%20Hybrid&trim=XLE&year=2018"
BASE_URL = "https://turo.com/us/en/carculator?country=US&deliveryOffered={deliveryOffered}&make={make}&marketAreaId={marketAreaId}&model={model}&trim={trim}&year={year}"


def get_selector_values(soup: BeautifulSoup, selector_id):
    selector = soup.find("select", {"id": selector_id})
    options = selector.find_all("option") if selector else []
    return {option.get("value"): option.text for option in options if option} if options else []


def get_stats(soup: BeautifulSoup):
    stats = soup.find_all("div", {"class": "chart gaugeChart"})
    daily_price = soup.find(
        "div", {"class": "carculatorResults-stats"})
    daily_price = daily_price.find("span").text if daily_price else None

    if not stats:
        return {}

    return {
        "days_booked_per_moth": stats[0].text,
        "earnings_per_month": stats[1].text,
        "earnings_per_day": stats[2].text,
        "daily_price": daily_price,
    }


def get_html(url):
    headers = {
        "apikey": app_config.ZENSCRAPE_KEY
    }

    params = (
        ("url", url),
        ("location", "na"),
        ("render", "true"),
        ("scroll_to_bottom", True),
    )

    response = requests.get(
        'https://app.zenscrape.com/api/v1/get', headers=headers, params=params)

    return response.text


def save_to_db(doc):
    with TuroDB() as db:
        cars = db.get_cars()
        cars.insert_one(doc)


def first_request(maker):
    html = get_html(CANARY_URL.format(**{"make": maker}))

    soup = BeautifulSoup(html, "html.parser")

    selector_ids = ["year", "make", "model", "marketAreaId", "trim"]

    values = {selector_id: get_selector_values(
        soup, selector_id) for selector_id in selector_ids}

    return values


def gen_years():
    return [str(year) for year in range(2014, 2019)]


def work(url, vals):
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    stats = get_stats(soup)
    stats.update(vals)
    save_to_db(stats)


def main():

    # values = first_request("Toyota")
    makers = ["Toyota"]
    locations = ["104", "95"]
    years = gen_years()
    deliveryOffereds = ["true"]

    vals = []

    for make in makers:
        values = first_request(make)
        models = values.get("model")
        trims = values.get("trim")
        for location in locations:
            for year in years:
                for trim in trims:
                    for deliveryOffered in deliveryOffereds:
                        for model in models:
                            val = {"year": year, "make": make, "marketAreaId": location,
                                   "model": model.replace(" ", "%20"), "deliveryOffered": deliveryOffered, "trim": trim}
                            url = BASE_URL.format(**val)
                            vals.append((url, val))
    print(len(vals))

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                work, url, val) for url, val in vals
        ]

        i = 0
        for future in futures:
            if future.result():
                i += 1
                continue
            if i % 100 == 0:
                print(i)
    # vals = {"year": year, "make": "Toyota", "marketAreaId": values.get("marketAreaId"),
    #         "model": model.replace(" ", "%20"), "deliveryOffered": "true", "trim": "true"}
    # url = BASE_URL.format(**vals)
    # html = get_html(url)
    # soup = BeautifulSoup(html, "html.parser")
    # stats = get_stats(soup)
    # stats.update(vals)
    # cars.append(stats)


if __name__ == '__main__':
    main()
