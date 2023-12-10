""" 
Gets weather forecast from weather.com and writes to InfluxDB.
"""

import os
import time
import requests
from influxdb import InfluxDBClient


def get_weather_forecast(api_key: str, geocode: str) -> dict:
    """
    Fetches the weather forecast from weather.com.

    Args:
        api_key (str): API key for weather.com.
        geocode (str): Geocode for the location (latitude,longitude).

    Returns:
        dict: Weather forecast data.
    """
    url = f"https://api.weather.com/v3/wx/forecast/daily/5day?geocode={geocode}&units=e&language=en-US&format=json&apiKey={api_key}"
    response = requests.get(url)
    return response.json()


def write_to_influx(client: InfluxDBClient, forecast_data: dict) -> None:
    """
    Writes weather forecast data to InfluxDB.

    Args:
        client (InfluxDBClient): InfluxDB client instance.
        forecast_data (dict): Weather forecast data to write.
    """
    json_body = [
        {
            "measurement": "weather_forecast",
            "fields": {
                "today": forecast_data["narrative"][0],
                "tomorrow": forecast_data["narrative"][1],
            },
        }
    ]
    client.write_points(json_body)


def main():
    influx_client = InfluxDBClient(
        host=os.getenv("INFLUX_HOSTNAME"),
        port=8086,
        username=os.getenv("INFLUX_USERNAME"),
        password=os.getenv("INFLUX_PASSWORD"),
        database=os.getenv("INFLUX_DATABASE"),
    )

    while True:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        home_geocode = os.getenv("HOME_LATLONG")

        forecast_data = get_weather_forecast(weather_api_key, home_geocode)
        write_to_influx(influx_client, forecast_data)

        time.sleep(600)


if __name__ == "__main__":
    main()
