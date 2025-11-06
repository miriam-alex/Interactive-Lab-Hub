"""
MQTT Bridge for Pixel Grid
Enable this to connect MQTT -> WebSocket
"""

import paho.mqtt.client as mqtt
import ssl
import json
from flask_socketio import SocketIO

# MQTT Configuration
MQTT_BROKER = 'farlab.infosci.cornell.edu'
MQTT_PORT = 1883
MQTT_TOPIC = 'IDD/kitchen-instrument'
MQTT_USERNAME = 'idd'
MQTT_PASSWORD = 'device@theFarm'

mqtt_client = None


def on_connect(client, userdata, flags, rc):
    """MQTT connected"""
    if rc == 0:
        print(f'[OK] MQTT connected to {MQTT_BROKER}:{MQTT_PORT}')
        client.subscribe(MQTT_TOPIC)
        print(f'[OK] Subscribed to {MQTT_TOPIC}')
    else:
        print(f'[ERR] MQTT connection failed: {rc}')


def on_message(client, userdata, msg):
    """MQTT message received - forward instrument events to WebSocket"""
    try:
        data = json.loads(msg.payload.decode('UTF-8'))
        socketio = userdata.get('socketio')
        instruments = userdata.get('instruments', {})

        # Only handle kitchen instrument messages (instrument_publisher.py)
        if 'utensil' not in data:
            print(f'[DBG] Ignored MQTT message on {msg.topic} (no utensil field)')
            return

        mac = data.get('mac')
        ip = data.get('ip')
        utensil = data.get('utensil')
        timestamp = data.get('timestamp')

        # Check if new instrument
        is_new = mac not in instruments

        from datetime import datetime
        if is_new:
            instruments[mac] = {
                'utensil': utensil,
                'ip': ip,
                'last_update': datetime.now(),
                'timestamp': timestamp
            }
            print(f'[OK] MQTT instrument: {mac[:17]} utensil={utensil}')
        else:
            instruments[mac]['utensil'] = utensil
            instruments[mac]['ip'] = ip
            instruments[mac]['timestamp'] = timestamp
            instruments[mac]['last_update'] = datetime.now()

        # Broadcast instrument event to web clients
        if socketio:
            socketio.emit('instrument_event', {
                'mac': mac,
                'ip': ip,
                'utensil': utensil,
                'timestamp': timestamp,
                'is_new': is_new,
                'total': len(instruments)
            }, namespace='/')

        # Save back instruments into userdata
        userdata['instruments'] = instruments

    except Exception as e:
        print(f'Error processing MQTT message: {e}')


def start_mqtt_bridge(socketio_instance, pixels_dict):
    """Start MQTT client that forwards to WebSocket"""
    global mqtt_client
    
    try:
        import uuid
        mqtt_client = mqtt.Client(str(uuid.uuid1()))
        
        # Only use TLS if port is 8883
        if MQTT_PORT == 8883:
            mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
        
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    # Provide instruments dict in userdata so bridge and app can share state
    mqtt_client.user_data_set({'socketio': socketio_instance, 'instruments': pixels_dict})
        
        mqtt_client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        
        print('MQTT bridge started')
        return True
        
    except Exception as e:
        print(f'[WARN]  MQTT bridge failed: {e}')
        print('    Server will run with WebSocket only')
        return False


def stop_mqtt_bridge():
    """Stop MQTT client"""
    global mqtt_client
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print('MQTT bridge stopped')
