import { useState } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [owner, setOwner] = useState("");
  const [repo, setRepo] = useState("");
  const [issues, setIssues] = useState([]);
  const [selected, setSelected] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadIssues(e) {
    e?.preventDefault(); setLoading(true); setError(""); setAnalysis(null);
    try {
      const res = await fetch(`${API}/api/github/issues?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}`);
      if (!res.ok) throw new Error(await res.text());
      setIssues(await res.json());
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  async function analyzeIssue(issue) {
    setSelected(issue); setLoading(true); setError("");
    try {
      const res = await fetch(`${API}/api/github/analyze`, {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({owner, repo, issue_number: issue.number})
      });
      if (!res.ok) throw new Error(await res.text());
      setAnalysis(await res.json());
    } catch (err) { setError(err.message); } finally { setLoading(false); }
  }

  return <main className="shell">
    <header>
      <div><span className="eyebrow">OPEN-SOURCE DEV TOOL</span><h1>IssuePilot</h1><p>AI-assisted GitHub issue triage.</p></div>
      <div className="status">● API-ready</div>
    </header>
    <section className="card">
      <form onSubmit={loadIssues} className="repo-form">
        <input value={owner} onChange={e=>setOwner(e.target.value)} placeholder="owner" required />
        <span>/</span>
        <input value={repo} onChange={e=>setRepo(e.target.value)} placeholder="repository" required />
        <button disabled={loading}>{loading ? "Loading..." : "Load issues"}</button>
      </form>
      {error && <div className="error">{error}</div>}
    </section>
    <section className="grid">
      <div className="card"><div className="card-head"><h2>Open issues</h2><span>{issues.length}</span></div>
        {issues.length === 0 ? <p className="muted">Enter a GitHub repository to load issues.</p> :
          <div className="issues">{issues.map(issue=><button className="issue" key={issue.number} onClick={()=>analyzeIssue(issue)}>
            <span>#{issue.number}</span><strong>{issue.title}</strong>
          </button>)}</div>}
      </div>
      <div className="card"><div className="card-head"><h2>Analysis</h2></div>
        {!analysis ? <p className="muted">Select an issue to see classification, priority, duplicates and a suggested reply.</p> :
        <>
          <h3>{selected?.title}</h3>
          <div className="metrics">
            <Metric label="Category" value={analysis.category}/><Metric label="Priority" value={analysis.priority}/>
            <Metric label="Severity" value={analysis.severity}/><Metric label="Confidence" value={`${Math.round(analysis.confidence*100)}%`}/>
          </div>
          <h4>Likely duplicates</h4>
          {analysis.duplicate_matches.length ? <ul>{analysis.duplicate_matches.map((m,i)=><li key={i}>{m.title} — {Math.round(m.score*100)}%</li>)}</ul> : <p className="muted">No likely duplicates found.</p>}
          <h4>Suggested reply</h4><div className="reply">{analysis.suggested_reply}</div>
        </>}
      </div>
    </section>
  </main>;
}

function Metric({label,value}) { return <div className="metric"><small>{label}</small><strong>{value}</strong></div>; }
