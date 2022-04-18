""" Gets current prices for all relevant Kraken currency pairs, writes to Influx """

from pycoingecko import CoinGeckoAPI
from influxdb import InfluxDBClient
from pprint import pprint
import time
import os

client = InfluxDBClient(os.getenv("INFLUX_HOSTNAME"), 8086, os.getenv("INFLUX_USERNAME"), os.getenv("INFLUX_PASSWORD"), os.getenv("INFLUX_DATABASE"))


cg = CoinGeckoAPI()
currencies = cg.get_coins_list()
kraken_crypto = [x.lower() for x in ['AAVE','ALGO','ANT','REP','REPV2','BAT','BAL','XBT','BCH','ADA','LINK','COMP','ATOM','CRV','DAI','DASH','MANA','XDG','EOS','ETH','ETC','FIL','FLOW','GNO','ICX','KAVA','KEEP','KSM','KNC','LSK','LTC','MLN','XMR','NANO','OMG','OXT','PAXG','DOT','QTUM','XRP','SC','XLM','STORJ','SNX','TBTC','USDT','XTZ','GRT','TRX','UNI','USDC','WAVES','YFI','ZEC']]
symbols = {c['symbol']: c['name'] for c in currencies}
kraken_to_gecko_mapping = {'xdg':'doge', 'xbt':'btc'}
kk = {k.lower():v.lower() for (k,v) in symbols.items() if k in kraken_crypto}

for x in kraken_to_gecko_mapping:
  kk[x] = symbols[kraken_to_gecko_mapping[x]]

rev = {v.lower():k.lower() for (k,v) in kk.items()}

while True:
  prices = cg.get_price(ids=[x for x in kk.values()], vs_currencies='usd', include_market_cap='true', include_24hr_vol='true')

  r = {}
  for x in prices:
    y = rev[x]
    r[f"{y}.usd"] = float(prices[x]['usd'])
    r[f"{y}.usd_24h_vol"] = float(prices[x]['usd_24h_vol'])
    r[f"{y}.usd_market_cap"] = float(prices[x]['usd_market_cap'])


  json_body = [
                  {
                      "measurement": "allcrypto",
                      "fields": r
                  }
              ]
  client.write_points(json_body)
  pprint(json_body)