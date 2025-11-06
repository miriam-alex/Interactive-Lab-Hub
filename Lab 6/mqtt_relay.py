import asyncio
import json
from collections import defaultdict
import websockets
import paho.mqtt.client as mqtt

BROKER = "farlab.infosci.cornell.edu"
PORT = 1883
USERNAME = "idd"
PASSWORD = "device@theFarm"
TOPIC = "IDD/#"

latest_data = defaultdict(dict)
clients = set()
queue = asyncio.Queue()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        utensil = payload.get("utensil", "unknown")
        latest_data[utensil] = payload
        queue.put_nowait({utensil: payload})
        print(f"MQTT -> {msg.topic} queued for broadcast")
    except Exception as e:
        print("Error processing message:", e)

async def broadcast_loop():
    print("Broadcast loop started")
    while True:
        message = await queue.get()
        print("BROADCASTING!", message)
        if clients:
            data = json.dumps(message)
            for ws in clients.copy():
                try:
                    await ws.send(data)
                except:
                    clients.remove(ws)

async def ws_handler(websocket, path):
    clients.add(websocket)
    print("Web client connected")
    await websocket.send(json.dumps(latest_data))
    try:
        async for _ in websocket:
            pass
    finally:
        clients.remove(websocket)
        print("Web client disconnected")

def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    print("MQTT client started")

async def main():
    start_mqtt()
    # ✅ start the broadcast loop inside the main event loop
    asyncio.create_task(broadcast_loop())
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("WebSocket server running on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
