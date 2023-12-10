""" 
Scrapes AmbientWeather station for current conditions and writes to InfluxDB.
"""

import os
import requests
from lxml import html
from influxdb import InfluxDBClient


def scrape_weather_data(station_ip: str) -> dict:
    """
    Scrapes the weather data from AmbientWeather station.

    Args:
        station_ip (str): IP address of the AmbientWeather station.

    Returns:
        dict: Scraped weather data.
    """
    page = requests.get(f"http://{station_ip}/livedata.htm")
    tree = html.fromstring(page.content)

    weather_data = {
        "inBattery": tree.xpath('//input[@name="inBattSta"]/@value')[0],
        "outBattery": tree.xpath('//input[@name="outBattSta1"]/@value')[0],
        "inTemp": tree.xpath('//input[@name="inTemp"]/@value')[0],
        "inHumid": tree.xpath('//input[@name="inHumi"]/@value')[0],
        "absPressure": tree.xpath('//input[@name="AbsPress"]/@value')[0],
        "relPressure": tree.xpath('//input[@name="RelPress"]/@value')[0],
        "outTemp": tree.xpath('//input[@name="outTemp"]/@value')[0],
        "outHumid": tree.xpath('//input[@name="outHumi"]/@value')[0],
        "windDir": tree.xpath('//input[@name="windir"]/@value')[0],
        "windSpeed": tree.xpath('//input[@name="avgwind"]/@value')[0],
        "windGust": tree.xpath('//input[@name="gustspeed"]/@value')[0],
        "solarRadiation": tree.xpath('//input[@name="solarrad"]/@value')[0],
        "uv": tree.xpath('//input[@name="uv"]/@value')[0],
        "uvi": tree.xpath('//input[@name="uvi"]/@value')[0],
        "rainHourly": tree.xpath('//input[@name="rainofhourly"]/@value')[0],
    }

    return weather_data


def write_to_influx(client: InfluxDBClient, weather_data: dict) -> None:
    """
    Writes weather data to InfluxDB.

    Args:
        client (InfluxDBClient): InfluxDB client instance.
        weather_data (dict): Weather data to write.
    """
    json_body = [
        {
            "measurement": "weather",
            "fields": {
                "temperature": float(weather_data["outTemp"]),
                "humidity": float(weather_data["outHumid"]),
                "windDir": float(weather_data["windDir"]),
                "windSpeed": float(weather_data["windSpeed"]),
                "windGust": float(weather_data["windGust"]),
                "solarRadiation": float(weather_data["solarRadiation"]),
                "uv": float(weather_data["uv"]),
                "uvi": float(weather_data["uvi"]),
                "rainHourly": float(weather_data["rainHourly"]),
            },
        }
    ]
    client.write_points(json_body)


def main():
    station_ip = os.getenv("WEATHER_STATION_IP")
    weather_data = scrape_weather_data(station_ip)

    influx_client = InfluxDBClient(
        host=os.getenv("INFLUX_HOSTNAME"),
        port=8086,
        username=os.getenv("INFLUX_USERNAME"),
        password=os.getenv("INFLUX_PASSWORD"),
        database=os.getenv("INFLUX_DATABASE"),
    )

    write_to_influx(influx_client, weather_data)


if __name__ == "__main__":
    main()
