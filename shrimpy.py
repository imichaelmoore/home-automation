import os
import time
import base64
import hmac
import hashlib
import requests
from influxdb import InfluxDBClient
from collections import defaultdict


def get_shrimpy_balance(key: str, secret: str) -> dict:
    """Request balance information from Shrimpy API.

    Args:
        key (str): Shrimpy API key.
        secret (str): Shrimpy API secret.

    Returns:
        dict: Balance information from Shrimpy API.
    """
    endpoint = "/v1/accounts"
    nonce = str(int(time.time() * 10000))
    sign_url = (endpoint + "GET" + nonce).encode("utf-8")
    signing = hmac.new(base64.b64decode(secret), sign_url, hashlib.sha256)
    signing_b64 = base64.b64encode(signing.digest()).decode("utf-8")
    headers = {
        "content-type": "application/json",
        "SHRIMPY-API-KEY": key,
        "SHRIMPY-API-NONCE": nonce,
        "SHRIMPY-API-SIGNATURE": signing_b64,
    }
    response = requests.get("https://api.shrimpy.io" + endpoint, headers=headers)
    return response.json()


def post_to_influx(client: InfluxDBClient, data: dict) -> None:
    """Post data to InfluxDB.

    Args:
        client (InfluxDBClient): InfluxDB client instance.
        data (dict): Data to post to InfluxDB.
    """
    json_body = [{"measurement": "crypto_balance", "fields": data}]
    client.write_points(json_body)


def main():
    influx_client = InfluxDBClient(
        host=os.getenv("INFLUX_HOSTNAME"),
        port=8086,
        username=os.getenv("INFLUX_USERNAME"),
        password=os.getenv("INFLUX_PASSWORD"),
        database=os.getenv("INFLUX_DATABASE"),
    )

    shrimpy_key = os.getenv("SHRIMPY_API_KEY")
    shrimpy_secret = os.getenv("SHRIMPY_API_SECRET")

    while True:
        balance_data = get_shrimpy_balance(shrimpy_key, shrimpy_secret)
        to_post = defaultdict(float)

        total_balance = 0.0
        for account in balance_data:
            account_balance = account.get("balance", [])
            usd_balance = sum(float(asset["usdValue"]) for asset in account_balance)
            total_balance += usd_balance
            for asset in account_balance:
                to_post[
                    f"{account['exchange']}_balance_{asset['symbol']}_usd"
                ] += float(asset["usdValue"])

        to_post["total_usd"] = total_balance
        post_to_influx(influx_client, to_post)
        time.sleep(10)


if __name__ == "__main__":
    main()
