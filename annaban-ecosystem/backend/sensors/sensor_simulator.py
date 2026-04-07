import random
import time
import requests
import os

API_URL = os.getenv('API_URL', 'http://localhost:4000')
TOKEN = os.getenv('API_TOKEN', '')
HEADERS = {'Authorization': f'Bearer {TOKEN}'} if TOKEN else {}
LOCATIONS = ['Plant-A', 'Plant-B', 'Grid-01', 'Grid-02']


def generate_event():
    return {
        'source': 'simulator',
        'metric': 'load_index',
        'value': round(random.uniform(45, 98), 2),
        'unit': 'index',
        'location': random.choice(LOCATIONS)
    }


if __name__ == '__main__':
    while True:
        event = generate_event()
        try:
            r = requests.post(f'{API_URL}/sensors/ingest', json=event, headers=HEADERS, timeout=5)
            print('sent', event, 'status', r.status_code)
        except Exception as e:
            print('error', e)
        time.sleep(5)
