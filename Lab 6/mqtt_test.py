import paho.mqtt.client as mqtt

BROKER = 'farlab.infosci.cornell.edu'
PORT = 1883
USERNAME = 'idd'
PASSWORD = 'device@theFarm'
TOPIC = 'IDD/#'

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"{msg.topic} -> {msg.payload.decode()}")

client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
