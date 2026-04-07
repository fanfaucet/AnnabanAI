import { useEffect, useState } from 'react';
import Panel from '../components/Panel';
import { client, login } from '../services/api';

export default function Dashboard() {
  const [token, setToken] = useState('');
  const [sensors, setSensors] = useState([]);
  const [decisions, setDecisions] = useState([]);
  const [audit, setAudit] = useState([]);

  useEffect(() => {
    login().then(setToken);
  }, []);

  async function loadAll(t) {
    const api = client(t);
    const [s, d, a] = await Promise.all([api.get('/sensors'), api.get('/decisions'), api.get('/audit')]);
    setSensors(s.data);
    setDecisions(d.data);
    setAudit(a.data);
  }

  useEffect(() => {
    if (!token) return;
    loadAll(token);
    const id = setInterval(() => loadAll(token), 8000);
    return () => clearInterval(id);
  }, [token]);

  async function recommend() {
    const api = client(token);
    await api.post('/decisions/recommend', { prompt: 'Balance efficiency and safety' });
    loadAll(token);
  }

  async function govern(id, action) {
    const api = client(token);
    await api.post(`/governance/${id}/${action}`);
    loadAll(token);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <header className="mb-6">
        <h1 className="text-3xl font-bold">AnnabanAI Ecosystem Dashboard</h1>
        <p className="text-slate-400">Human-sovereign orchestration. Autonomous execution disabled by design.</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <Panel title="Live Sensor Data">
          <ul className="space-y-2 text-sm">{sensors.slice(0, 6).map(s => <li key={s.id}>{s.location} · {s.metric}: {s.value}</li>)}</ul>
        </Panel>

        <Panel title="AI Decision Feed">
          <button className="mb-3 px-3 py-2 rounded bg-indigo-600" onClick={recommend}>Generate Recommendation</button>
          <ul className="space-y-2 text-sm">{decisions.slice(0, 5).map(d => <li key={d.id}>{d.actions?.join(', ')} · conf {d.confidence?.toFixed?.(2)} · {d.status}</li>)}</ul>
        </Panel>

        <Panel title="Explainability Panel">
          <ul className="space-y-2 text-sm">{decisions[0]?.explainability?.map((e, idx) => <li key={idx}>• {e}</li>) || <li>No decision yet</li>}</ul>
        </Panel>

        <Panel title="Governance Controls">
          <div className="space-y-3">{decisions.slice(0, 3).map(d => (
            <div key={d.id} className="border border-slate-700 rounded p-2">
              <div className="text-xs mb-1">{d.id.slice(0, 8)}... ({d.status})</div>
              <div className="flex gap-2">
                <button className="px-2 py-1 bg-emerald-700 rounded" onClick={() => govern(d.id, 'approve')}>Approve</button>
                <button className="px-2 py-1 bg-rose-700 rounded" onClick={() => govern(d.id, 'reject')}>Reject</button>
              </div>
            </div>
          ))}</div>
        </Panel>

        <Panel title="Audit Log (Blockchain Events)">
          <ul className="space-y-2 text-xs">{audit.slice(0, 8).map(a => <li key={a.id}>{a.type} · {a.timestamp} {a.txHash ? `· ${a.txHash.slice(0, 10)}...` : ''}</li>)}</ul>
        </Panel>
      </div>
    </div>
  );
}
