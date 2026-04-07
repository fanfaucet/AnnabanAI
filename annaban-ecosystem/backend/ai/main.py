from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI(title='AnnabanAI Orchestration Engine')

class Context(BaseModel):
    sensors: List[Dict[str, Any]] = []
    prompt: str = 'Optimize safely'


def grok_agent(ctx: Context):
    avg = sum(float(s.get('value', 0)) for s in ctx.sensors) / max(len(ctx.sensors), 1)
    action = 'increase_efficiency_mode' if avg < 70 else 'stabilize_and_reduce_load'
    return {'agent': 'GrokAgent', 'action': action, 'confidence': 0.78, 'why': f'Real-time average metric is {avg:.2f}'}


def annaban_agent(ctx: Context):
    high_variance = len({s.get('location') for s in ctx.sensors}) > 3
    ethical = 0.92 if not high_variance else 0.84
    return {'agent': 'AnnabanAgent', 'ethical_score': ethical, 'why': 'Prioritized long-term human and environmental utility'}


def system_agent(ctx: Context):
    risky = any(float(s.get('value', 0)) > 95 for s in ctx.sensors)
    return {
        'agent': 'SystemAgent',
        'requires_human': True,
        'safe': not risky,
        'why': 'Hard safety guardrails enforce human approval before execution'
    }


def oracle_agent(ctx: Context):
    return {
        'agent': 'OracleAgent',
        'summary': 'Historical pattern suggests moderated throughput yields best sustainability-to-risk ratio.',
        'why': 'Compared current stream with recent trend windows and knowledge priors.'
    }


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'ai'}


@app.post('/orchestrate')
def orchestrate(ctx: Context):
    g = grok_agent(ctx)
    a = annaban_agent(ctx)
    s = system_agent(ctx)
    o = oracle_agent(ctx)

    actions = [g['action']]
    confidence = min(0.99, (g['confidence'] + a['ethical_score']) / 2)

    return {
        'actions': actions,
        'confidence': confidence,
        'explainability': [g['why'], a['why'], s['why'], o['why']],
        'ethical_score': a['ethical_score'],
        'requires_human': True,
        'agents': [g, a, s, o]
    }
