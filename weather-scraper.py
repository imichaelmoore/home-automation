""" Scrapes AmbientWeather station for current conditions, writes to Influx """

from lxml import html
import requests
from influxdb import InfluxDBClient
from pprint import pprint
import os

station_ip = os.getenv("WEATHER_STATION_IP") # Change this to your ObserverIP address

# Get the latest live data from the ObserverIP, then create a tree from the content we can parse
page = requests.get("http://{}/livedata.htm".format(station_ip))
tree = html.fromstring(page.content)
print(tree)

# Screen scrape the data. Help from:
# http://docs.python-guide.org/en/latest/scenarios/scrape/
# http://stackoverflow.com/a/22469878/1177153
inBattery = tree.xpath('//input[@name="inBattSta"]')[0].value
outBattery = tree.xpath('//input[@name="outBattSta1"]')[0].value
inTemp = tree.xpath('//input[@name="inTemp"]')[0].value
inHumid = tree.xpath('//input[@name="inHumi"]')[0].value
absPressure = tree.xpath('//input[@name="AbsPress"]')[0].value
relPressure = tree.xpath('//input[@name="RelPress"]')[0].value
outTemp = tree.xpath('//input[@name="outTemp"]')[0].value
outHumid = tree.xpath('//input[@name="outHumi"]')[0].value
windDir = tree.xpath('//input[@name="windir"]')[0].value
windSpeed = tree.xpath('//input[@name="avgwind"]')[0].value
windGust = tree.xpath('//input[@name="gustspeed"]')[0].value
solarRadiation = tree.xpath('//input[@name="solarrad"]')[0].value
uv = tree.xpath('//input[@name="uv"]')[0].value
uvi = tree.xpath('//input[@name="uvi"]')[0].value
rainHourly = tree.xpath('//input[@name="rainofhourly"]')[0].value

jblob = {"inBattery":inBattery, "outBattery":outBattery, "inTemp":inTemp, "inHumid":inHumid, "absPressure":absPressure, "relPressure":relPressure, "outTemp":outTemp, "outHumid":outHumid, "windDir":windDir, "windSpeed":windSpeed, "windGust":windGust, "solarRadiation":solarRadiation, "uv":uv, "uvi":uvi, "rainHourly":rainHourly}
#requests.post("http://mon.33901.cloud:5000/post", json=jblob)

client = InfluxDBClient(os.getenv("INFLUX_HOSTNAME"), 8086, os.getenv("INFLUX_USERNAME"), os.getenv("INFLUX_PASSWORD"), os.getenv("INFLUX_DATABASE"))

json_body = [
                {
                    "measurement": "weather",
                    "fields": {
                        "temperature": float(outTemp),
                        "humidity": float(outHumid),
                        "windDir": float(windDir),
                        "windSpeed": float(windSpeed),
                        "windGust": float(windGust),
                        "solarRadiation": float(solarRadiation),
                        "uv": float(uv),
                        "uvi": float(uvi),
                        "rainHourly": float(rainHourly)
                        }
                }
            ]
client.write_points(json_body)
pprint(json_body)
