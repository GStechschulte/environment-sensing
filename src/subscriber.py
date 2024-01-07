import msgspec
import paho.mqtt.client as mqtt

from msgspec import Struct


# MQTT broker information
BROKER_ADDRESS = "192.168.1.143"
PORT = 1883
TOPIC = "home/telemetry"


class Telemetry(Struct):
    time: str
    temperature: float
    humidity: float
    pressure: float


def on_connect(client, userdata, flags, rc):
    print(f"Connected to broker with status: {rc}")


def on_message(client, userData, msg):

    payload = msgspec.json.decode(msg.payload, type=Telemetry)
    print(f"Received `{payload}` from `{msg.topic}` topic")


def main():
    
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_ADDRESS, 1883)
    client.subscribe(TOPIC)
    client.loop_forever()


if __name__ == '__main__':
    main()