import json
import time

from datetime import datetime
from typing import TypedDict

import paho.mqtt.client as mqtt

from sensor import BME280


# MQTT broker information
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC = "home/telemetry"


class Telemetry(TypedDict):
    time: datetime.isoformat
    pressure: float
    temperature: float
    humidity: float


def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with status: {rc}")


def on_publish(client, data, mid):
    print(f"Publish completed: {mid}")


def collect_sensor_data(sampling_rate: int = 60) -> Telemetry:
    """Reads pressure, temperature, and humidity data from the BME280 sensor.

    Parameters
    ----------
    sampling_rate : int
        The sampling rate in seconds.

    Returns
    -------
    dict : Telemetry
        A dictionary containing the pressure, temperature, and humidity data.
    """
    sensor = BME280()

    time.sleep(sampling_rate)
    pressure, temperature, humidity = sensor.read_data()
    data: Telemetry = {
        "time": datetime.now().isoformat(),
        "pressure": pressure,
        "temperature": temperature,
        "humidity": humidity,
    }

    return data


def main():

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    
    client.on_connect = on_connect
    client.on_publish = on_publish

    client.connect(BROKER_ADDRESS, PORT)
    
    while True:
        try:
            payload = json.dumps(collect_sensor_data(sampling_rate=1))
            client.publish(TOPIC, payload)
        except KeyboardInterrupt:
            break
    
    client.loop_forever()


if __name__ == '__main__':
    main()