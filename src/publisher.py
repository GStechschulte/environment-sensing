import paho.mqtt.client as mqtt


# MQTT broker information
BROKER_ADDRESS = "localhost"
PORT = 1883
TOPIC = "testing"
RESPONSE = {
    0: "connection succeeded",
    1: "connection failed - incorrect protocol version",
    2: "connection failed - invalid client identifier",
    3: "connection failed - the broker is not available",
    4: "connection failed - wrong username or password",
    5: "connection failed - unauthorized"
}


def on_publish(mid):
    print(f"Connected to broker with status: {mid}: {RESPONSE.get(mid, 'Unknown')}")


def main():

    client = mqtt.Client(client_id="jetson", protocol=mqtt.MQTTv5)
    # Set the callback function for when the publisher connects to the broker
    client.on_publish = on_publish
    # Connect to the broker
    client.connect(BROKER_ADDRESS, PORT)

    # Publish a message to the "testing" topic
    message = "Hello, world!"
    client.publish(TOPIC, message)

    # Keep client running "forever"
    client.loop_forever()


if __name__ == '__main__':
    main()