import requests
import time
import json
from influxdb import InfluxDBClient
from pprint import pprint
from poloniex import Poloniex

polo = Poloniex()

client = InfluxDBClient(os.getenv("INFLUX_HOSTNAME"), 8086, os.getenv("INFLUX_USERNAME"), os.getenv("INFLUX_PASSWORD"), os.getenv("INFLUX_DATABASE"))

while True:
    ticker = polo.returnTicker()["USDT_BTC"]
    eticker = polo.returnTicker()["USDT_ETH"]
    xticker = polo.returnTicker()["USDT_XMR"]
    json_body = [
                    {
                    "measurement": "cryptocurrency",
                    "fields": {
                        "USDT_BTC": round(float(ticker["last"]), 3),
                        "USDT_ETH": round(float(eticker["last"]), 3),
                        "USDT_XMR": round(float(xticker["last"]), 3),
                        }
                    }
                ]

    pprint(json_body)
    client.write_points(json_body)
    time.sleep(5)