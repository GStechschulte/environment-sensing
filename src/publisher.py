"""
Creates an MQTT publisher.
"""

import configparser
import time

from argparse import ArgumentParser
from datetime import datetime

import paho.mqtt.client as mqtt

from sqlalchemy import create_engine

from sensor import BME280


# MQTT broker information
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC = "testing"


def on_publish(client, data, mid):
    print(f"Message published with mid: {mid}")


def main(args):

    client = mqtt.Client()
    # Set the callback function for when the publisher connects to the broker
    client.on_publish = on_publish
    # Connect to the broker
    client.connect(BROKER_ADDRESS, PORT)

    # Publish a message to the "testing" topic
    message = "Hello, world!"
    client.publish(TOPIC, message)

    # Keep client running "forever"
    client.loop_forever()

    # sensor = BME280()
    # print("Connection to sensor successful...")
    # print("Sampling every 60 seconds...")

    # while True:
    #     try:
    #         pressure, temperature, humidity = sensor.read_data()
    #         print(f"Time: {datetime.now()}, Temperature: {temperature:.2f} °C")
    #         time.sleep(1)
    #     except KeyboardInterrupt:1


if __name__ == '__main__':
    parser = ArgumentParser(description="Bosche Sensor")
    parser.add_argument("--write_to_db", default=False, type=bool)
    args = parser.parse_args()
    main(args)