from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import numpy as np

app = FastAPI(title='AetherOS Simulation Engine')

class Context(BaseModel):
    sensors: List[Dict[str, Any]] = []
    prompt: str = 'Optimize safely'


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'aether'}


@app.post('/simulate')
def simulate(ctx: Context):
    base = np.mean([float(s.get('value', 50)) for s in ctx.sensors] or [50])
    scenarios = []
    for i in range(1, 6):
        efficiency = float(max(0, min(100, 80 + np.random.normal(0, 5) - (base / 20) + i)))
        risk = float(max(0, min(100, 20 + np.random.normal(0, 5) + (base / 15) - i)))
        sustainability = float(max(0, min(100, 70 + np.random.normal(0, 5) - (base / 30) + i / 2)))
        score = efficiency * 0.45 + sustainability * 0.4 - risk * 0.35
        scenarios.append({
            'scenario_id': f'scenario_{i}',
            'efficiency': round(efficiency, 2),
            'risk': round(risk, 2),
            'sustainability': round(sustainability, 2),
            'score': round(score, 2)
        })

    ranked = sorted(scenarios, key=lambda x: x['score'], reverse=True)
    return {'top_scenario': ranked[0], 'ranked_scenarios': ranked}
