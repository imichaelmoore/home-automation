""" Gets weather forecast from weather.com, writes to Influx. """

import requests
import time
import json
from influxdb import InfluxDBClient
from pprint import pprint
import os

client = InfluxDBClient(os.getenv("INFLUX_HOSTNAME"), 8086, os.getenv("INFLUX_USERNAME"), os.getenv("INFLUX_PASSWORD"), os.getenv("INFLUX_DATABASE"))

while True:

    url = f"https://api.weather.com/v3/wx/forecast/daily/5day?geocode={os.getenv('HOME_LATLONG')}&units=e&language=en-US&format=json&apiKey={os.getenv('WEATHER_API_KEY')}"

    r = requests.get(url)
    j = r.json()
    json_body = [
                    {
                    "measurement": "weather_forecast",
                    "fields": {
                        "today": j["narrative"][0],
                        "tomorrow": j["narrative"][1],
                        }
                    }
                ]

    pprint(json_body)

    client.write_points(json_body)
    time.sleep(600)