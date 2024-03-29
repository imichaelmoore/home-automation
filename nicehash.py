""" Gets current NiceHash mining statistics, writes to InfluxDB.  Not yet mypy-compliant. """

import pprint
from influxdb import InfluxDBClient
from datetime import datetime
from time import mktime, sleep
import uuid
import hmac
import requests
import json
from hashlib import sha256
import os

client = InfluxDBClient(
    os.getenv("INFLUX_HOSTNAME"),
    8086,
    os.getenv("INFLUX_USERNAME"),
    os.getenv("INFLUX_PASSWORD"),
    os.getenv("INFLUX_DATABASE"),
)


class public_api:
    def __init__(self, host, verbose=False):
        self.host = host
        self.verbose = verbose

    def request(self, method, path, query, body):
        url = self.host + path
        if query:
            url += "?" + query

        if self.verbose:
            print(method, url)

        s = requests.Session()
        if body:
            body_json = json.dumps(body)
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(
                str(response.status_code)
                + ": "
                + response.reason
                + ": "
                + str(response.content)
            )
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_current_global_stats(self):
        return self.request(
            "GET", "/main/api/v2/public/stats/global/current/", "", None
        )

    def get_global_stats_24(self):
        return self.request("GET", "/main/api/v2/public/stats/global/24h/", "", None)

    def get_active_orders(self):
        return self.request("GET", "/main/api/v2/public/orders/active/", "", None)

    def get_active_orders2(self):
        return self.request("GET", "/main/api/v2/public/orders/active2/", "", None)

    def buy_info(self):
        return self.request("GET", "/main/api/v2/public/buy/info/", "", None)

    def get_algorithms(self):
        return self.request("GET", "/main/api/v2/mining/algorithms/", "", None)

    def get_markets(self):
        return self.request("GET", "/main/api/v2/mining/markets/", "", None)

    def get_currencies(self):
        return self.request("GET", "/main/api/v2/public/currencies/", "", None)

    def get_multialgo_info(self):
        return self.request(
            "GET", "/main/api/v2/public/simplemultialgo/info/", "", None
        )

    def get_exchange_markets_info(self):
        return self.request("GET", "/exchange/api/v2/info/status", "", None)

    def get_exchange_trades(self, market):
        return self.request("GET", "/exchange/api/v2/trades", "market=" + market, None)

    def get_candlesticks(self, market, from_s, to_s, resolution):
        return self.request(
            "GET",
            "/exchange/api/v2/candlesticks",
            "market={}&from={}&to={}&resolution={}".format(
                market, from_s, to_s, resolution
            ),
            None,
        )

    def get_exchange_orderbook(self, market, limit):
        return self.request(
            "GET",
            "/exchange/api/v2/orderbook",
            "market={}&limit={}".format(market, limit),
            None,
        )


class private_api:
    def __init__(self, host, organisation_id, key, secret, verbose=False):
        self.key = key
        self.secret = secret
        self.organisation_id = organisation_id
        self.host = host
        self.verbose = verbose

    def request(self, method, path, query, body):
        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = bytearray(self.key, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(str(xtime), "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(xnonce, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(self.organisation_id, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(method, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(path, "utf-8")
        message += bytearray("\x00", "utf-8")
        message += bytearray(query, "utf-8")

        if body:
            body_json = json.dumps(body)
            message += bytearray("\x00", "utf-8")
            message += bytearray(body_json, "utf-8")

        digest = hmac.new(bytearray(self.secret, "utf-8"), message, sha256).hexdigest()
        xauth = self.key + ":" + digest

        headers = {
            "X-Time": str(xtime),
            "X-Nonce": xnonce,
            "X-Auth": xauth,
            "Content-Type": "application/json",
            "X-Organization-Id": self.organisation_id,
            "X-Request-Id": str(uuid.uuid4()),
        }

        s = requests.Session()
        s.headers = headers

        url = self.host + path
        if query:
            url += "?" + query

        if self.verbose:
            print(method, url)

        if body:
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(
                str(response.status_code)
                + ": "
                + response.reason
                + ": "
                + str(response.content)
            )
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

    def algo_settings_from_response(self, algorithm, algo_response):
        algo_setting = None
        for item in algo_response["miningAlgorithms"]:
            if item["algorithm"] == algorithm:
                algo_setting = item

        if algo_setting is None:
            raise Exception(
                "Settings for algorithm not found in algo_response parameter"
            )

        return algo_setting

    def get_accounts(self):
        return self.request("GET", "/main/api/v2/accounting/accounts2/", "", None)

    def get_accounts_for_currency(self, currency):
        return self.request(
            "GET", "/main/api/v2/accounting/account2/" + currency, "", None
        )

    def get_withdrawal_addresses(self, currency, size, page):
        params = "currency={}&size={}&page={}".format(currency, size, page)

        return self.request(
            "GET", "/main/api/v2/accounting/withdrawalAddresses/", params, None
        )

    def get_withdrawal_types(self):
        return self.request(
            "GET", "/main/api/v2/accounting/withdrawalAddresses/types/", "", None
        )

    def withdraw_request(self, address_id, amount, currency):
        withdraw_data = {
            "withdrawalAddressId": address_id,
            "amount": amount,
            "currency": currency,
        }
        return self.request(
            "POST", "/main/api/v2/accounting/withdrawal/", "", withdraw_data
        )

    def get_my_active_orders(self, algorithm, market, limit):
        ts = self.get_epoch_ms_from_now()
        params = "algorithm={}&market={}&ts={}&limit={}&op=LT".format(
            algorithm, market, ts, limit
        )

        return self.request("GET", "/main/api/v2/hashpower/myOrders", params, None)

    def create_pool(self, name, algorithm, pool_host, pool_port, username, password):
        pool_data = {
            "name": name,
            "algorithm": algorithm,
            "stratumHostname": pool_host,
            "stratumPort": pool_port,
            "username": username,
            "password": password,
        }
        return self.request("POST", "/main/api/v2/pool/", "", pool_data)

    def delete_pool(self, pool_id):
        return self.request("DELETE", "/main/api/v2/pool/" + pool_id, "", None)

    def get_my_pools(self, page, size):
        return self.request("GET", "/main/api/v2/pools/", "", None)

    def get_hashpower_orderbook(self, algorithm):
        return self.request(
            "GET", "/main/api/v2/hashpower/orderBook/", "algorithm=" + algorithm, None
        )

    def create_hashpower_order(
        self, market, type, algorithm, price, limit, amount, pool_id, algo_response
    ):
        algo_setting = self.algo_settings_from_response(algorithm, algo_response)

        order_data = {
            "market": market,
            "algorithm": algorithm,
            "amount": amount,
            "price": price,
            "limit": limit,
            "poolId": pool_id,
            "type": type,
            "marketFactor": algo_setting["marketFactor"],
            "displayMarketFactor": algo_setting["displayMarketFactor"],
        }
        return self.request("POST", "/main/api/v2/hashpower/order/", "", order_data)

    def cancel_hashpower_order(self, order_id):
        return self.request(
            "DELETE", "/main/api/v2/hashpower/order/" + order_id, "", None
        )

    def refill_hashpower_order(self, order_id, amount):
        refill_data = {"amount": amount}
        return self.request(
            "POST",
            "/main/api/v2/hashpower/order/" + order_id + "/refill/",
            "",
            refill_data,
        )

    def set_price_hashpower_order(self, order_id, price, algorithm, algo_response):
        algo_setting = self.algo_settings_from_response(algorithm, algo_response)

        price_data = {
            "price": price,
            "marketFactor": algo_setting["marketFactor"],
            "displayMarketFactor": algo_setting["displayMarketFactor"],
        }
        return self.request(
            "POST",
            "/main/api/v2/hashpower/order/" + order_id + "/updatePriceAndLimit/",
            "",
            price_data,
        )

    def set_limit_hashpower_order(self, order_id, limit, algorithm, algo_response):
        algo_setting = self.algo_settings_from_response(algorithm, algo_response)
        limit_data = {
            "limit": limit,
            "marketFactor": algo_setting["marketFactor"],
            "displayMarketFactor": algo_setting["displayMarketFactor"],
        }
        return self.request(
            "POST",
            "/main/api/v2/hashpower/order/" + order_id + "/updatePriceAndLimit/",
            "",
            limit_data,
        )

    def set_price_and_limit_hashpower_order(
        self, order_id, price, limit, algorithm, algo_response
    ):
        algo_setting = self.algo_settings_from_response(algorithm, algo_response)

        price_data = {
            "price": price,
            "limit": limit,
            "marketFactor": algo_setting["marketFactor"],
            "displayMarketFactor": algo_setting["displayMarketFactor"],
        }
        return self.request(
            "POST",
            "/main/api/v2/hashpower/order/" + order_id + "/updatePriceAndLimit/",
            "",
            price_data,
        )

    def get_my_exchange_orders(self, market):
        return self.request(
            "GET", "/exchange/api/v2/myOrders", "market=" + market, None
        )

    def get_my_exchange_trades(self, market):
        return self.request(
            "GET", "/exchange/api/v2/myTrades", "market=" + market, None
        )

    def create_exchange_limit_order(self, market, side, quantity, price):
        query = "market={}&side={}&type=limit&quantity={}&price={}".format(
            market, side, quantity, price
        )
        return self.request("POST", "/exchange/api/v2/order", query, None)

    def create_exchange_buy_market_order(self, market, quantity):
        query = "market={}&side=buy&type=market&secQuantity={}".format(market, quantity)
        return self.request("POST", "/exchange/api/v2/order", query, None)

    def create_exchange_sell_market_order(self, market, quantity):
        query = "market={}&side=sell&type=market&quantity={}".format(market, quantity)
        return self.request("POST", "/exchange/api/v2/order", query, None)

    def cancel_exchange_order(self, market, order_id):
        query = "market={}&orderId={}".format(market, order_id)
        return self.request("DELETE", "/exchange/api/v2/order", query, None)


if __name__ == "__main__":
    apikey = os.getenv("NICEHASH_APIKEY")
    apisecret = os.getenv("NICEHASH_APISECRET")
    org = os.getenv("NICEHASH_ORG")

    private_api = private_api("https://api2.nicehash.com", org, apikey, apisecret)

    while True:
        btc = private_api.get_accounts()["currencies"][0]
        available = btc["available"]
        balance = btc["totalBalance"]

        usdrate = requests.get(
            "https://api2.nicehash.com/exchange/api/v2/info/prices"
        ).json()["BTCUSDC"]

        raw = requests.get(
            "https://api2.nicehash.com/main/api/v2/mining/external/3M6uRT9JF7VeSKQqtwzSUJZfgVWGW4xvw2/rigs2"
        ).json()
        rigs = raw["miningRigs"]
        btc_tp_per_24_hour = raw["totalProfitability"]
        usd_tp_per_24_hour = btc_tp_per_24_hour * usdrate
        per_month_profitability = usd_tp_per_24_hour * 30

        json_body = [
            {
                "measurement": "nicehash",
                "fields": {
                    "active_devices": raw["totalDevices"],
                    "per_month_profitability": per_month_profitability,
                    "nicehash_wallet_balance": balance,
                    "nicehash_wallet_balance_usd": float(balance) * float(usdrate),
                },
            }
        ]

        client.write_points(json_body)
        pprint.pprint(json_body)
        sleep(10)
