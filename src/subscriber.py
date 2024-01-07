import paho.mqtt.client as mqtt


# MQTT broker information
BROKER_ADDRESS = "192.168.1.143"
PORT = 1883
TOPIC = "testing"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("testing")


def on_message(client, userData, msg):
    print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")


def main():
    
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.connect(BROKER_ADDRESS, 1883)

    client.subscribe(TOPIC)
    client.on_message = on_message

    client.loop_forever()


if __name__ == '__main__':
    main()