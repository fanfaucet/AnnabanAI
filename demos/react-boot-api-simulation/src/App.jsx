import { useState } from "react";
import {
  Activity, ArrowRight, Check, CircleAlert, Cpu, Database, LockKeyhole,
  Play, RotateCcw, ShieldCheck, Terminal, Wifi
} from "lucide-react";

const bootSteps = [
  { id: "runtime", title: "Runtime initialized", detail: "React shell and local state mounted", icon: Cpu },
  { id: "policy", title: "Policy loaded", detail: "Advisory-only mode and human gate checked", icon: ShieldCheck },
  { id: "transport", title: "Transport handshake", detail: "Mock provider adapter returned a simulated response", icon: Wifi },
  { id: "session", title: "Session configured", detail: "Model label, limits, and trace metadata assigned", icon: Database },
  { id: "ready", title: "Ready for input", detail: "No external request or model inference was performed", icon: Check },
];

const stamp = () => new Date().toLocaleTimeString([], { hour12: false });

export default function App() {
  const [status, setStatus] = useState("idle");
  const [stepIndex, setStepIndex] = useState(-1);
  const [events, setEvents] = useState([
    { time: stamp(), level: "INFO", message: "Simulation loaded. Awaiting operator start." },
    { time: stamp(), level: "GUARD", message: "External effects = 0; live API calls disabled." },
  ]);
  const [model, setModel] = useState("gpt-style-sim");
  const [environment, setEnvironment] = useState("sandbox");
  const [humanGate, setHumanGate] = useState(true);

  const append = (level, message) =>
    setEvents((previous) => [...previous, { time: stamp(), level, message }]);

  const runBoot = async () => {
    if (status === "booting") return;
    setStatus("booting");
    setStepIndex(-1);
    setEvents([{ time: stamp(), level: "INFO", message: "Boot sequence requested by operator." }]);
    append("GUARD", "Advisory mode enforced locally; no credentials are read.");
    for (let i = 0; i < bootSteps.length; i += 1) {
      await new Promise((resolve) => setTimeout(resolve, 480));
      setStepIndex(i);
      append(i === bootSteps.length - 1 ? "READY" : "INFO", bootSteps[i].title);
    }
    setStatus("ready");
    append("AUDIT", `Boot complete | model=${model} | env=${environment} | human_gate=${humanGate}`);
  };

  const reset = () => {
    setStatus("idle");
    setStepIndex(-1);
    setEvents([
      { time: stamp(), level: "INFO", message: "Local simulation reset." },
      { time: stamp(), level: "GUARD", message: "No remote state was changed." },
    ]);
  };

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="AnnabanAI home">
          <span className="brand-mark"><Activity size={19} /></span>
          <span>annaban<span className="brand-accent">ai</span></span>
          <span className="build-tag">LAB / 0.1</span>
        </a>
        <div className="top-status"><span className="status-dot" /> LOCAL SIMULATION</div>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow"><span /> SYSTEM ORCHESTRATION / DEMO</div>
        <h1>Boot sequence<span className="muted-title">, made observable.</span></h1>
        <p className="hero-copy">A React prototype of a model-service boot lifecycle, with explicit policy checks, trace events, and a human authorization boundary.</p>
        <div className="disclaimer"><CircleAlert size={16} /><span><strong>Simulation only.</strong> This does not reproduce OpenAI's private boot API, call OpenAI, or run model inference. All provider responses are mocked locally.</span></div>
      </section>

      <section className="workspace">
        <aside className="panel config-panel">
          <div className="panel-heading"><span className="section-index">01</span><div><h2>Boot configuration</h2><p>Set the simulated runtime parameters.</p></div></div>
          <label className="field-label" htmlFor="model">MODEL PROFILE</label>
          <select id="model" value={model} onChange={(e) => setModel(e.target.value)} disabled={status === "booting"}>
            <option value="gpt-style-sim">GPT-style / simulated</option>
            <option value="annaban-advisory">Annaban advisory engine</option>
            <option value="mock-provider">Generic mock provider</option>
          </select>
          <label className="field-label" htmlFor="environment">ENVIRONMENT</label>
          <select id="environment" value={environment} onChange={(e) => setEnvironment(e.target.value)} disabled={status === "booting"}>
            <option value="sandbox">Sandbox (recommended)</option>
            <option value="test">Test fixture</option>
          </select>
          <div className="gate-card">
            <div className="gate-icon"><LockKeyhole size={17} /></div>
            <div className="gate-copy"><strong>Human authorization gate</strong><span>Required before any proposed external action.</span></div>
            <label className="switch"><input type="checkbox" checked={humanGate} onChange={(e) => setHumanGate(e.target.checked)} disabled={status === "booting"} /><span /></label>
          </div>
          {!humanGate && <p className="warning-note">Gate disabled in this configuration. The simulation will flag this state; no real action is enabled.</p>}
          <div className="button-row">
            <button className="primary-button" onClick={runBoot} disabled={status === "booting"}><Play size={16} fill="currentColor" /> {status === "booting" ? "Booting…" : "Run boot sequence"} <ArrowRight size={16} /></button>
            <button className="icon-button" onClick={reset} aria-label="Reset simulation" title="Reset"><RotateCcw size={17} /></button>
          </div>
          <div className="config-foot"><span><span className="mini-dot" /> External effects</span><strong>0</strong></div>
        </aside>

        <section className="panel lifecycle-panel">
          <div className="panel-heading"><span className="section-index">02</span><div><h2>Lifecycle monitor</h2><p>State transitions are simulated in sequence.</p></div><span className={`state-pill ${status}`}>{status.toUpperCase()}</span></div>
          <div className="steps">
            {bootSteps.map((step, i) => {
              const Icon = step.icon;
              const complete = i <= stepIndex;
              const active = status === "booting" && i === stepIndex + 1;
              return <div className={`step ${complete ? "complete" : ""} ${active ? "active" : ""}`} key={step.id}>
                <div className="step-rail"><div className="step-icon">{complete ? <Check size={16} /> : <Icon size={16} />}</div>{i < bootSteps.length - 1 && <div className="step-line" />}</div>
                <div className="step-text"><strong>{step.title}</strong><span>{step.detail}</span></div>
                <span className="step-state">{complete ? "DONE" : active ? "RUNNING" : "WAITING"}</span>
              </div>;
            })}
          </div>
          <div className="runtime-summary">
            <div><span className="summary-label">ACTIVE PROFILE</span><strong>{model}</strong></div>
            <div><span className="summary-label">AUTHORITY</span><strong>{humanGate ? "HUMAN-LED" : "GATE DISABLED"}</strong></div>
            <div><span className="summary-label">NETWORK</span><strong>MOCK / OFFLINE</strong></div>
          </div>
        </section>
      </section>

      <section className="panel event-panel">
        <div className="panel-heading event-heading"><span className="section-index">03</span><div><h2>Trace console</h2><p>Append-only for this page session; not a durable audit ledger.</p></div><span className="event-count">{events.length} EVENTS</span></div>
        <div className="console">
          <div className="console-bar"><span><Terminal size={14} /> BOOT_TRACE.LOG</span><span>SESSION / LOCAL</span></div>
          <div className="console-body">
            {events.map((event, i) => <div className="log-line" key={i}><time>{event.time}</time><span className={`log-level ${event.level.toLowerCase()}`}>{event.level}</span><span className="log-message">{event.message}</span></div>)}
            {status === "booting" && <div className="log-line pending"><span className="cursor" /> waiting for next state transition…</div>}
          </div>
        </div>
      </section>

      <footer className="footer">
        <div><span className="footer-mark">A</span><span>AnnabanAI <span className="footer-muted">/ Response Calibration Lab</span></span></div>
        <span>AI recommends. Humans decide. Everything is logged.</span>
      </footer>
    </main>
  );
}
