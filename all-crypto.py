"""Module to fetch current prices for Kraken currency pairs and write them to InfluxDB."""

from typing import Dict, List
from pycoingecko import CoinGeckoAPI
from influxdb import InfluxDBClient
import os
import time


def get_influxdb_client() -> InfluxDBClient:
    """Create and return an InfluxDB client using environment variables."""
    return InfluxDBClient(
        host=os.getenv("INFLUX_HOSTNAME"),
        port=8086,
        username=os.getenv("INFLUX_USERNAME"),
        password=os.getenv("INFLUX_PASSWORD"),
        database=os.getenv("INFLUX_DATABASE"),
    )


def get_kraken_crypto_symbols() -> List[str]:
    """Returns a list of crypto symbols available on Kraken."""
    return [
        x.lower()
        for x in [
            "AAVE",
            "ALGO",
            "ANT",
            "REP",
            "REPV2",
            "BAT",
            "BAL",
            "XBT",
            "BCH",
            "ADA",
            "LINK",
            "COMP",
            "ATOM",
            "CRV",
            "DAI",
            "DASH",
            "MANA",
            "XDG",
            "EOS",
            "ETH",
            "ETC",
            "FIL",
            "FLOW",
            "GNO",
            "ICX",
            "KAVA",
            "KEEP",
            "KSM",
            "KNC",
            "LSK",
            "LTC",
            "MLN",
            "XMR",
            "NANO",
            "OMG",
            "OXT",
            "PAXG",
            "DOT",
            "QTUM",
            "XRP",
            "SC",
            "XLM",
            "STORJ",
            "SNX",
            "TBTC",
            "USDT",
            "XTZ",
            "GRT",
            "TRX",
            "UNI",
            "USDC",
            "WAVES",
            "YFI",
            "ZEC",
        ]
    ]


def get_kraken_gecko_mapping(
    currencies: List[Dict[str, str]], kraken_crypto: List[str]
) -> Dict[str, str]:
    """Maps Kraken symbols to CoinGecko API symbols.

    Args:
        currencies: A list of currency dicts from CoinGecko API.
        kraken_crypto: A list of crypto symbols available on Kraken.

    Returns:
        A dictionary mapping Kraken symbols to CoinGecko symbols.
    """
    symbols = {c["symbol"]: c["name"] for c in currencies}
    kraken_to_gecko_mapping = {"xdg": "doge", "xbt": "btc"}
    mapping = {k.lower(): v.lower() for k, v in symbols.items() if k in kraken_crypto}

    for k, v in kraken_to_gecko_mapping.items():
        mapping[k] = symbols[v]

    return mapping


def fetch_and_write_crypto_data(
    client: InfluxDBClient, cg: CoinGeckoAPI, mapping: Dict[str, str]
):
    """Fetches crypto data and writes it to InfluxDB.

    Args:
        client: An InfluxDB client instance.
        cg: A CoinGeckoAPI client instance.
        mapping: A mapping of Kraken to CoinGecko symbols.
    """
    reverse_mapping = {v: k for k, v in mapping.items()}

    while True:
        prices = cg.get_price(
            ids=list(mapping.values()),
            vs_currencies="usd",
            include_market_cap="true",
            include_24hr_vol="true",
        )
        data = {f"{reverse_mapping[k]}.usd": v["usd"] for k, v in prices.items()}
        data.update(
            {
                f"{reverse_mapping[k]}.usd_24h_vol": v["usd_24h_vol"]
                for k, v in prices.items()
            }
        )
        data.update(
            {
                f"{reverse_mapping[k]}.usd_market_cap": v["usd_market_cap"]
                for k, v in prices.items()
            }
        )

        json_body = [{"measurement": "allcrypto", "fields": data}]
        client.write_points(json_body)
        time.sleep(10)  # Sleep to prevent rate limiting, adjust as needed.


def main():
    """Main function to execute the script logic."""
    client = get_influxdb_client()
    cg = CoinGeckoAPI()
    currencies = cg.get_coins_list()
    kraken_crypto = get_kraken_crypto_symbols()
    mapping = get_kraken_gecko_mapping(currencies, kraken_crypto)
    fetch_and_write_crypto_data(client, cg, mapping)


if __name__ == "__main__":
    main()
