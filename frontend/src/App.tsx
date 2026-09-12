import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Clock3,
  Gauge,
  MapPin,
  Route,
  ShieldCheck,
  Siren,
  Zap
} from "lucide-react";

const API = "http://127.0.0.1:8000";

type RouteData = {
  id: string;
  name: string;
  distance_km: number;
  eta_min: number;
  traffic: number;
  congestion: string;
  risk: number;
  intervention: number;
  delay: number;
  score?: number;
  reasons?: string[];
};

type Analysis = {
  recommended_route: RouteData;
  routes: RouteData[];
  explanation: string;
};

function App() {
  const [page, setPage] = useState("Command Center");
  const [severity, setSeverity] = useState(5);
  const [emergency, setEmergency] = useState("Cardiac emergency");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    fetch(`${API}/api/health`)
      .then((r) => r.ok && setApiOnline(true))
      .catch(() => setApiOnline(false));
  }, []);

  async function analyze() {
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emergency_type: emergency, severity })
      });
      const data = await response.json();
      setAnalysis(data);
    } catch {
      alert("Backend is not running. Start FastAPI on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  const recommended = analysis?.recommended_route;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Siren size={22} /></div>
          <div>
            <strong>LifeLine AI</strong>
            <span>Response Intelligence</span>
          </div>
        </div>

        <nav>
          <a className={page === "Command Center" ? "active" : ""} onClick={() => setPage("Command Center")}><Gauge size={18} /> Command Center</a>
          <a className={page === "Route Analysis" ? "active" : ""} onClick={() => setPage("Route Analysis")}><Route size={18} /> Route Analysis</a>
          <a className={page === "Incidents" ? "active" : ""} onClick={() => setPage("Incidents")}><Activity size={18} /> Incidents</a>
          <a className={page === "Safety Rules" ? "active" : ""} onClick={() => setPage("Safety Rules")}><ShieldCheck size={18} /> Safety Rules</a>
        </nav>

        <div className="side-note">
          <div className="pulse-dot" />
          <div>
            <strong>System operational</strong>
            <span>Decision engine ready</span>
          </div>
        </div>
      </aside>

      <main className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">EMERGENCY OPERATIONS</p>
            <h1>{page}</h1>
          </div>
          <div className="status">
            <span className={`status-dot ${apiOnline ? "online" : ""}`} />
            {apiOnline ? "API Online" : "API Offline"}
          </div>
        </header>

        {page === "Command Center" && (
          <>
        <section className="hero">
          <div>
            <span className="tag"><Zap size={14} /> Explainable AI</span>
            <h2>Make faster, safer route decisions.</h2>
            <p>
              LifeLine AI compares emergency routes using ETA, traffic,
              risk and intervention cost, then explains the recommendation.
            </p>
          </div>
          <div className="hero-stat">
            <span>Decision mode</span>
            <strong>Real-time</strong>
            <small>Multi-factor scoring</small>
          </div>
        </section>

        <section className="grid two">
          <div className="panel">
            <div className="panel-head">
              <div>
                <p className="eyebrow">NEW INCIDENT</p>
                <h3>Emergency parameters</h3>
              </div>
              <Siren size={22} />
            </div>

            <label>Emergency type</label>
            <select value={emergency} onChange={(e) => setEmergency(e.target.value)}>
              <option>Cardiac emergency</option>
              <option>Road accident</option>
              <option>Critical medical transfer</option>
              <option>Fire emergency</option>
            </select>

            <label>Severity level <b>{severity}/5</b></label>
            <input
              type="range"
              min="1"
              max="5"
              value={severity}
              onChange={(e) => setSeverity(Number(e.target.value))}
            />

            <div className="severity-labels">
              <span>Routine</span><span>Critical</span>
            </div>

            <button className="primary" onClick={analyze} disabled={loading}>
              {loading ? "Analyzing routes..." : "Analyze best route"}
              <ArrowUpRight size={18} />
            </button>
          </div>

          <div className="panel recommendation">
            <div className="panel-head">
              <div>
                <p className="eyebrow">AI RECOMMENDATION</p>
                <h3>{recommended ? "Recommended route" : "Awaiting analysis"}</h3>
              </div>
              <div className="confidence">LIVE</div>
            </div>

            {recommended ? (
              <>
                <div className="decision-context">
                  <span>{emergency}</span>
                  <span>Severity {severity}/5</span></div>   
                  
                <div className="route-title">
                  <div className="route-icon"><MapPin size={20} /></div>
                  <div>
                    <strong>{recommended.name}</strong>
                    <span>{recommended.distance_km} km route</span>
                  </div>
                </div>

                <div className="metrics">
                  <div><Clock3 /><strong>{recommended.eta_min} min</strong><span>ETA</span></div>
                  <div><Activity /><strong>{recommended.traffic}%</strong><span>Traffic</span></div>
                  <div><ShieldCheck /><strong>{recommended.risk}</strong><span>Risk</span></div>
                </div>

                <div className="explanation">
                  <strong>Why this route?</strong>
                  <p>{analysis?.explanation}</p>
                </div>
              </>
            ) : (
              <div className="empty">
                <Route size={38} />
                <p>Run the analysis to receive an explainable route recommendation.</p>
              </div>
            )}
          </div>
        </section>

        <section className="panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">ALTERNATIVE ANALYSIS</p>
              <h3>Route comparison</h3>
            </div>
            <span className="mini">Lower score = better</span>
          </div>

          <div className="table">
            <div className="table-row header">
              <span>Route</span><span>ETA</span><span>Traffic</span><span>Risk</span><span>Score</span>
            </div>
            {(analysis?.routes ?? [
              { id: "R1", name: "City Center → Medical District", eta_min: 14, traffic: 32, risk: 12 },
              { id: "R2", name: "Ring Road → Medical District", eta_min: 12, traffic: 46, risk: 18 },
              { id: "R3", name: "Market Road → Medical District", eta_min: 18, traffic: 71, risk: 35 }
            ] as RouteData[]).map((route) => (
              <div className="table-row" key={route.id}>
                <span><b>{route.id}</b> {route.name}</span>
                <span>{route.eta_min} min</span>
                <span>{route.traffic}%</span>
                <span>{route.risk}</span>
                <span className="score">{route.score ?? "—"}</span>
              </div>
            ))}
          </div>
        </section>
          </>
        )}

        {page === "Route Analysis" && (
          <section className="page-grid">
            <div className="panel full">
              <div className="panel-head">
                <div><p className="eyebrow">ROUTE INTELLIGENCE</p><h3>Compare every available route</h3></div>
                <Route size={22} />
              </div>
              <p className="page-copy">The decision engine ranks routes using ETA, traffic, route risk, intervention effort and emergency severity.</p>
              <div className="route-cards">
                {(analysis?.routes ?? []).map((route) => (
                  <div className="route-card" key={route.id}>
                    <div><b>{route.id}</b><strong>{route.name}</strong></div>
                    <span>{route.eta_min} min ETA</span><span>{route.traffic}% traffic</span><span>{route.risk} risk</span>
                    <strong className="score">{route.score ?? "—"}</strong>
                  </div>
                ))}
                {!analysis && <div className="empty-inline">Run an analysis from Command Center to populate live route scores.</div>}
              </div>
              <button className="primary compact" onClick={() => setPage("Command Center")}>← Back to command center</button>
            </div>
          </section>
        )}

        {page === "Incidents" && (
          <section className="page-grid">
            <div className="panel full">
              <div className="panel-head">
                <div><p className="eyebrow">INCIDENT LOG</p><h3>Recent emergency incidents</h3></div>
                <Activity size={22} />
              </div>
              <div className="incident-list">
                {[
                  ["INC-1042", "Cardiac emergency", "Rajpur Road", "Critical", "Active", "09:18"],
                  ["INC-1041", "Road accident", "ISBT Junction", "High", "Resolved", "08:51"],
                  ["INC-1040", "Medical transfer", "Clock Tower", "Medium", "Resolved", "08:24"]
                ].map(([id, type, location, priority, status, time]) => (
                  <div className="incident-row" key={id}>
                    <div><b>{id}</b><strong>{type}</strong><span>{location}</span></div>
                    <span className="priority">{priority}</span><span>{status}</span><span>{time}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {page === "Safety Rules" && (
          <section className="page-grid">
            <div className="panel full">
              <div className="panel-head">
                <div><p className="eyebrow">DECISION POLICY</p><h3>Safety rules used by LifeLine AI</h3></div>
                <ShieldCheck size={22} />
              </div>
              <div className="rules">
                <div><ShieldCheck /><div><strong>Severity-aware decisions</strong><p>Critical emergencies increase the influence of route risk in the scoring model.</p></div></div>
                <div><ShieldCheck /><div><strong>Explainable recommendations</strong><p>Every recommendation exposes the main operational factors behind the score.</p></div></div>
                <div><ShieldCheck /><div><strong>Lower score is better</strong><p>Routes are ranked consistently so dispatchers can compare alternatives.</p></div></div>
                <div><ShieldCheck /><div><strong>Prototype safety boundary</strong><p>This system is a decision-support prototype and must not replace certified emergency-dispatch procedures.</p></div></div>
              </div>
            </div>
          </section>
        )}

        <footer>
          <span>LifeLine AI · Recruitment MVP</span>
          <span>Prototype for emergency-response decision support</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
