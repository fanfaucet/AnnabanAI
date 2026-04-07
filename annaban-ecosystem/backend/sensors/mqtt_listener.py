import json
import os
import paho.mqtt.client as mqtt
import requests

BROKER = os.getenv('MQTT_BROKER', 'localhost')
TOPIC = os.getenv('MQTT_TOPIC', 'annaban/sensors')
API_URL = os.getenv('API_URL', 'http://localhost:4000')
TOKEN = os.getenv('API_TOKEN', '')
HEADERS = {'Authorization': f'Bearer {TOKEN}'} if TOKEN else {}


def normalize(payload: dict):
    return {
        'source': payload.get('source', 'mqtt'),
        'metric': payload.get('metric', 'unknown_metric'),
        'value': float(payload.get('value', 0)),
        'unit': payload.get('unit', 'n/a'),
        'location': payload.get('location', 'unknown')
    }


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        event = normalize(payload)
        requests.post(f'{API_URL}/sensors/ingest', json=event, headers=HEADERS, timeout=5)
        print('ingested', event)
    except Exception as e:
        print('failed', e)


if __name__ == '__main__':
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_message = on_message
    c.connect(BROKER, 1883, 60)
    c.subscribe(TOPIC)
    c.loop_forever()
