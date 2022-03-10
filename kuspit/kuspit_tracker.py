import base64
import pandas as pd

from bs4 import BeautifulSoup
from googleapiclient.discovery import build

from quickstart import get_credentials


TICKER_KEY = "Emisora"
OPERATION_TYPE = "Tipo de Operación"
UNIT_PRICE = "Precio Unitario"
TITLE_ASSIGNED = "Títulos Asignados"


creds = get_credentials()
gmail = build('gmail', 'v1', credentials=creds)


def get_all_messages(query=None, max_results=100):
    messages = []
    response = gmail.users().messages().list(
        userId='me', q=query, maxResults=max_results).execute()
    messages = response["messages"]

    while response.get("nextPageToken"):
        response = gmail.users().messages().list(
            userId='me', q="kuspit", maxResults=500, pageToken=response["nextPageToken"]).execute()
        messages.extend(response["messages"])

    return messages


def parse_order_details(decoded_data):
    soup = BeautifulSoup(decoded_data, "lxml")
    table = soup.find("table", {
                      "width": "515"})
    if not table:
        return {}

    table_data = table.find_all("td")

    def clean_string(string):
        # join is to clean multiple spaces
        return " ".join(string.replace("\r\n", "").split())

    details = {clean_string(table_data[i].text): clean_string(table_data[i+1].text)
               for i in range(len(table_data) - 1)}
    return details


def get_order_details_in_messages(message_list):
    order_details = []
    messages = []
    message_ids = [message.get("id") for message in message_list]

    messages = [gmail.users().messages().get(userId='me', id=message_id, format="full").execute()
                for message_id in message_ids]

    for message in messages:
        if not message.get("payload").get("parts")[0].get("parts"):
            continue
        data = message.get("payload").get(
            "parts")[0].get("parts")[0].get("body").get("data")
        data = data.replace("-", "+").replace("_", "/")
        decoded_data = base64.b64decode(data)

        # Now, the data obtained is in lxml. So, we will parse
        # it with BeautifulSoup library
        order_detail = parse_order_details(decoded_data)

        order_details.append(order_detail)

    return order_details


def get_tickers_count_from_orders(orders):
    tickers_count = {}

    for order_details in orders:
        if order_details.get(TICKER_KEY):
            tickers_count[order_details.get(TICKER_KEY)] = tickers_count.get(
                order_details.get(TICKER_KEY), 0) + 1

    return tickers_count


def group_ticker_operations_in_orders(ticker, orders):
    ticker_orders = list(filter(lambda x: x.get(TICKER_KEY) == ticker, orders))
    result = {
        TICKER_KEY: ticker,
    }

    def parse_price(price_str):
        return float(price_str.replace('$ ', "").replace(',', ""))

    for operation in ticker_orders:
        result[operation.get(OPERATION_TYPE)] = result.get(
            operation.get(OPERATION_TYPE), 0) + parse_price(operation.get("Importe"))


def operations_in_orders_by_ticker(orders):
    tickers = get_tickers_count_from_orders(orders).keys()
    operations_per_ticker = {}

    for ticker in tickers:
        operations_per_ticker[ticker] = list(
            filter(lambda x: x.get(TICKER_KEY) == ticker, orders))

    return operations_per_ticker


def format_operations_in_orders_by_ticker(operations_in_orders):
    for ticker in operations_in_orders:
        print(f"{ticker}\n{'-'*50}")
        for operation in operations_in_orders[ticker]:
            print(
                f'{operation.get(OPERATION_TYPE)} -- {operation.get("Fecha de Asignación")} -- {operation.get(UNIT_PRICE)} -- {operation.get(TITLE_ASSIGNED)}')

        print("-"*50)


orders = get_order_details_in_messages(
    get_all_messages("kuspit orden de compra de acciones "))

print(get_tickers_count_from_orders(orders))
group_ticker_operations_in_orders("FUNO", orders)

# format_operations_in_orders_by_ticker(operations_in_orders_by_ticker(orders))
df = pd.DataFrame(orders)
df.to_csv("orders_in_mail_compra.csv")

orders = get_order_details_in_messages(
    get_all_messages("kuspit orden de venta de acciones "))

print(get_tickers_count_from_orders(orders))
group_ticker_operations_in_orders("FUNO", orders)

# format_operations_in_orders_by_ticker(operations_in_orders_by_ticker(orders))
df = pd.DataFrame(orders)
df.to_csv("orders_in_mail_venta.csv")
