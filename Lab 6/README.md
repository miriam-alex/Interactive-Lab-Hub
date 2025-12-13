# Distributed Interaction

Amanda Lu, Shreya Kethi Reddy, Miriam Alex, Ying Yu Chen (main repo)

## Running the System

**Server (on laptop):**
```bash
cd "Lab 6"
source .venv/bin/activate
python3 mqtt_viewer.py
```
Then open browser to `http://localhost:5001`

**Raspberry Pi (each device):**
```bash
cd "Lab 6"
source .venv/bin/activate
python3 instrument_publisher.py
```

### Requirements

**Server:** `requirements-server.txt`
- Flask, Flask-SocketIO
- paho-mqtt

**Raspberry Pi:** `requirements-pi.txt`
- Adafruit sensor libraries
- paho-mqtt
- Pillow (for display)

### MQTT Broker Details

- **Host:** farlab.infosci.cornell.edu
- **Port:** 1883
- **Username:** idd
- **Password:** device@theFarm
- **Topics:** IDD/kitchen-instrument

## Description
Our distributed kitchen instrument system creates a networked environment where multiple Raspberry Pis equipped with different sensors act as "smart kitchen utensils." Each Pi publishes sensor data (such as distance, capacitance, or rotary encoder readings) to an MQTT broker, which then forwards this data to a central web dashboard. The dashboard displays real-time data from all connected devices and can coordinate actions across multiple devices simultaneously.

Users interact with physical sensors attached to Raspberry Pis (representing kitchen utensils like cutting boards, pans, and mixing bowls). As they manipulate these sensors, they see immediate feedback on a shared web dashboard. The system can detect when multiple "utensils" are being used simultaneously and coordinate responses across all connected devices, creating a shared, distributed experience.

## Architecture Diagram

_Note: Created this architectural diagram with Claude Sonnet_

```
┌─────────────────────────────────────────────────────────────────┐
│                        DISTRIBUTED SYSTEM                         │
└─────────────────────────────────────────────────────────────────┘

INPUT LAYER (Raspberry Pis)
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  Raspberry Pi  │  │  Raspberry Pi  │  │  Raspberry Pi  │
│   (Device 1)   │  │   (Device 2)   │  │   (Device 3)   │
├────────────────┤  ├────────────────┤  ├────────────────┤
│  APDS-9960     │  │  Distance      │  │  Capacitive    │
│  Color Sensor  │  │  Sensor        │  │  Touch Sensor  │
│                │  │                │  │                │
│  MiniPiTFT     │  │  Rotary        │  │  Display       │
│  Display       │  │  Encoder       │  │                │
└───────┬────────┘  └───────┬────────┘  └───────┬────────┘
        │                   │                   │
        │ Publishes to      │ Publishes to      │ Publishes to
        │ MQTT Topic        │ MQTT Topic        │ MQTT Topic
        └───────────────────┴───────────────────┘
                            ↓

COMMUNICATION LAYER
┌─────────────────────────────────────────────────────────────┐
│            MQTT Broker (farlab.infosci.cornell.edu)          │
│                   Topic: IDD/kitchen-instrument              │
│                                                              │
│  • Receives messages from all Raspberry Pis                 │
│  • Routes messages to subscribed clients                    │
│  • Maintains lightweight pub/sub architecture               │
└──────────────────────────┬──────────────────────────────────┘
                           ↓

COMPUTATION LAYER
┌─────────────────────────────────────────────────────────────┐
│              Flask/SocketIO Server (Python)                  │
│                                                              │
│  • mqtt_viewer.py - Subscribes to MQTT topics               │
│  • Processes incoming sensor data                           │
│  • Maintains state of all connected devices                 │
│  • Broadcasts updates via WebSocket                         │
│  • Coordinates multi-device interactions                    │
└──────────────────────────┬──────────────────────────────────┘
                           ↓

OUTPUT LAYER
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser Dashboard                     │
│                    (kitchen.html interface)                  │
│                                                              │
│  • Real-time display of all utensil data                    │
│  • WebSocket connection for live updates                    │
│  • Visual feedback when utensils are in use                 │
│  • Global status indicator for coordinated actions          │
└─────────────────────────────────────────────────────────────┘

DATA FLOW:
Sensor → Pi (JSON) → MQTT Publish → Broker → Server Subscribe 
→ Server Process → WebSocket → Browser Display
```

**Key Components:**
- **Input:** Physical sensors connected to Raspberry Pis
- **Computation:** MQTT broker routes messages; Flask server processes and coordinates
- **Output:** Web dashboard displays real-time data and coordination status

## Build Documentation
- Photos of each Pi + sensors
- MQTT topics used
- Code snippets with explanations

## 3. Build Documentation

### Hardware Setup

**Sensors:**
- Color/Proximity Sensor
- Rotary encoder
- Capacitive touch sensor

![Cutting Board](https://raw.githubusercontent.com/chenyingyu-main/Interactive-Lab-Hub/refs/heads/Fall2025/Lab%206/imgs/cutting.jpg)
![Pan](https://raw.githubusercontent.com/chenyingyu-main/Interactive-Lab-Hub/refs/heads/Fall2025/Lab%206/imgs/pan.jpg)
![Mixing Bowl](https://raw.githubusercontent.com/chenyingyu-main/Interactive-Lab-Hub/refs/heads/Fall2025/Lab%206/imgs/mixing.jpg)

### MQTT Topics Used
**Primary Topic:** `IDD/kitchen-instrument`

**Message Format (JSON):**
```json
{
  "mac": "b8:27:eb:xx:xx:xx",
  "ip": "192.168.1.100",
  "utensil": "cutting_board",
  "data": {
    "sensor_type": "distance",
    "value": 42,
    "unit": "cm"
  },
  "timestamp": 1702483200
}
```
**Key Code Snippet:**
```python
# Get device identifiers
mac_address = get_mac_address()
ip_address = get_ip_address()

# Setup MQTT client
client = mqtt.Client(str(uuid.uuid1()))
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, port=MQTT_PORT, keepalive=60)

# Main loop - read sensor and publish
while True:
    # Read sensor data (e.g., distance, color, capacitance)
    sensor_value = read_sensor()
    
    # Create JSON payload
    mqtt_payload = json.dumps({
        'mac': mac_address,
        'ip': ip_address,
        'utensil': 'cutting_board',  # or 'pan', 'mixing_bowl'
        'data': {
            'sensor_type': 'distance',
            'value': sensor_value
        },
        'timestamp': int(time.time())
    })
    
    # Publish to MQTT
    client.publish(MQTT_TOPIC, mqtt_payload)
    time.sleep(0.1)
```

**Explanation:** Each Pi identifies itself with a unique MAC address and publishes sensor readings as JSON messages. The system uses a consistent message format so the server can process data from any utensil type.

## User Testing

Testers: Marianne Arriola, Deviki Veerareddy

Before trying, the testers could tell that it was a multi-player game pretty easily, however they did not realize it was a cooking game until we told them
The cutting board especially surprised one of our testers felt as if the separate tapping of the rod did not mirror the knife cutting (they didn't know what to do intuitively)
Both of our testers liked how the sounds played while doing the actions, however wished there was some way to play multiple sounds when multiple actions were being done (ie. chopping & mixing
One tester suggested a great application/extension would be to compose music using each as a instrument
Noticed that the pan distance sensor worked most of the time, but at times was slightly buggy
After revealing the intent of the final project, our testers agreed that a visual UI would be very helpful for timing and synchronization

## Reflection

- The accuracy and speed of data streamed to server wokred well (sensor inputs were detected very well) and the sounds played were also pretty accurate in terms of timing with use and non-use of the sensors
- We did face some challenges in getting all three pis to co-ordinate and switch using the shared speaker system in terms of order of usage of the different sensors due to timing and sensistivity issues as well as audio lengths
- Each pi was assigned a specific cooking action (distance sensor -> pan, joystick -> mixing bowl, capacitator -> bowl) and all of these devices published messages to the same topic which was monitored for the speaker to know what sound to currently play
- We hope to imporve the sensor interactions to be more complex as we are using this as a baseline initiial step for our final project
- In addition we hope to improve the multiple sounds playing at once by playing sounds that are stacked audios of the two/three cooking utensils that are in use
- Another aspect we hope to improve on is making the physical cutting board more realistic mimicking a single lever-style chopping motion (up-to-down) rather than requiring repeated taps across the cutting board
- We are hoping to take this project in the direction of detecting synchronized timings and gamifying the experience we have now which would allow for a more interesting user interaction


---
**Your README = story of what YOU built!**
---

Resources: [MQTT Guide](https://www.hivemq.com/mqtt-essentials/) | [Paho Python](https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php) | [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
