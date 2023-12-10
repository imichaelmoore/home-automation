""" Gets MQTT Events from broker, writes to Pushover """

import random
import os
from paho.mqtt import client as mqtt_client
from pushover import init, Client

# Initialize Pushover with the app token
init(os.getenv("PUSHOVER_APP_TOKEN"))

# MQTT Broker settings
broker = os.getenv("MQTT_BROKER")
port = 1883
topic = "#"
client_id = f"python-mqtt-{random.randint(0, 100)}"


def connect_mqtt() -> mqtt_client:
    """Connect to MQTT broker and return the client object."""

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client) -> None:
    """Subscribe to MQTT topic and handle incoming messages."""

    def on_message(client, userdata, msg):
        """Handle incoming MQTT messages."""
        if (
            "snapshot" in msg.topic
            and "state" not in msg.topic
            and ("backdeck" in msg.topic or "driveway" in msg.topic)
        ):
            cleantopic = msg.topic.replace("frigate", "").replace("snapshot", "")
            details = cleantopic[1:-1].split("/")
            message = f"Alert from {details[0]} - Found {details[1]}"
            Client(os.getenv("PUSHOVER_CLIENT_ID")).send_message(
                message, attachment=msg.payload
            )
            print(message)

    client.subscribe(topic)
    client.on_message = on_message


def run() -> None:
    """Run the MQTT client."""
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == "__main__":
    run()
