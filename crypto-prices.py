import os
import time
from typing import List, Dict
from influxdb import InfluxDBClient
from poloniex import Poloniex


def get_ticker_data(polo: Poloniex, currency_pair: str) -> float:
    """
    Retrieve the last price of a given currency pair from Poloniex.

    Args:
    polo (Poloniex): The Poloniex API object.
    currency_pair (str): The currency pair (e.g., "USDT_BTC").

    Returns:
    float: The last price of the currency pair.
    """
    ticker = polo.returnTicker()[currency_pair]
    return round(float(ticker["last"]), 3)


def create_influxdb_client() -> InfluxDBClient:
    """
    Create an InfluxDB client.

    Returns:
    InfluxDBClient: The InfluxDB client object.
    """
    return InfluxDBClient(
        os.getenv("INFLUX_HOSTNAME"),
        8086,
        os.getenv("INFLUX_USERNAME"),
        os.getenv("INFLUX_PASSWORD"),
        os.getenv("INFLUX_DATABASE"),
    )


def main():
    polo = Poloniex()
    client = create_influxdb_client()

    while True:
        json_body: List[Dict] = [
            {
                "measurement": "cryptocurrency",
                "fields": {
                    "USDT_BTC": get_ticker_data(polo, "USDT_BTC"),
                    "USDT_ETH": get_ticker_data(polo, "USDT_ETH"),
                    "USDT_XMR": get_ticker_data(polo, "USDT_XMR"),
                },
            }
        ]

        print(json_body)
        client.write_points(json_body)
        time.sleep(5)


if __name__ == "__main__":
    main()
