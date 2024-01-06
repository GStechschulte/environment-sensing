import paho.mqtt.client as mqtt


# MQTT broker information
BROKER_ADDRESS = "172.17.0.1 192.168.1.143 2001:1711:fa4d:d200:ad4f:36e1:48d:77c3 2001:1711:fa4d:d200:25cd:a20d:f56f:7600 fdaa:bbcc:ddee:0:ad4f:36e1:48d:77c3 fdaa:bbcc:ddee:0:df6e:5dc1:2c8a:b455"
PORT = 1883
TOPIC = "testing"


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("testing")


def on_message(client, data, msg):
    print(f"Received topic: {msg.topic}, message:{msg.payload.decode()}")


def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883)
    client.loop_forever()


if __name__ == '__main__':
    main()