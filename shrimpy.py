""" Gets current balance for all accounts managed by Shrimpy, writes to Influx. """

import requests, json, time, datetime, base64, hmac, hashlib
from time import sleep
from influxdb import InfluxDBClient
from pprint import pprint
import uuid
import random
from collections import defaultdict
from pprint import pprint
import os

client = InfluxDBClient(os.getenv("INFLUX_HOSTNAME"), 8086, os.getenv("INFLUX_USERNAME"), os.getenv("INFLUX_PASSWORD"), os.getenv("INFLUX_DATABASE"))


key = os.getenv('SHRIMPY_API_KEY')
secret = os.getenv('SHRIMPY_API_SECRET')

def request(endpoint="/v1/accounts"):
    #     endpoint = f'/v1/accounts/{exid}/balance'
    nonce = str(int(time.time() * 10000))
    signurl = (endpoint + 'GET'+nonce).encode('utf-8')
    signing = hmac.new(base64.b64decode(secret), signurl , hashlib.sha256)
    signing_b64 = base64.b64encode(signing.digest()).decode('utf-8')
    header = {'content-type': 'application/json',
            'SHRIMPY-API-KEY': key,
            'SHRIMPY-API-NONCE' : nonce,
            'SHRIMPY-API-SIGNATURE': signing_b64 }
    r = requests.get('https://api.shrimpy.io' + endpoint, headers = header)
    return r.json()

def go():
    to_post = defaultdict(lambda: 0.0)

    accounts = request('/v1/accounts')

    total_balance = 0.0
    for a in accounts:
        d = request(f'/v1/accounts/{a["id"]}/balance')
        usdBalance = 0.0
        for x in d["balances"]:
            to_post[f"kraken_{x['symbol']}_usdValue"] += float(x['usdValue'])
            usdBalance += x['usdValue']
        total_balance += usdBalance
    print(total_balance)
    to_post['usd'] = total_balance

    json_body = [{"measurement": "crypto_balance", "fields": to_post}]
    client.write_points(json_body)
    pprint(json_body)

if __name__ == "__main__":
    while True:
        go()
        sleep(10)