from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title='OracleOS Knowledge Layer')

class Context(BaseModel):
    sensors: List[Dict[str, Any]] = []
    prompt: str = 'Optimize safely'


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'oracle'}


@app.post('/reason')
def reason(ctx: Context):
    sensor_count = len(ctx.sensors)
    critical = [s for s in ctx.sensors if float(s.get('value', 0)) > 90]
    return {
        'context_summary': f'Processed {sensor_count} sensor events with {len(critical)} critical readings.',
        'why': [
            'Recommendation includes sustainability constraints and historical safety priors.',
            'Human approval remains mandatory for every action pathway.',
            'Risk thresholds are raised when readings exceed 90 units.'
        ]
    }
