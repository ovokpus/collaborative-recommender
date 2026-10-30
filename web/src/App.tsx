import { useEffect, useState } from "react";

type Rec = { movie_id: number; title: string; score: number };
type Hist = { movie_id: number; title: string; rating: number };
type Dist = { movie_id: number; title: string; counts: Record<string, number>; mean: number };

const api = (p: string) => fetch(`/api${p}`).then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); });

function Bars({ d }: { d: Dist }) {
  const max = Math.max(1, ...Object.values(d.counts));
  return (
    <div className="dist">
      {["1", "2", "3", "4", "5"].map((k) => (
        <div key={k} className="barcol" title={`${d.counts[k]} ratings of ${k}★`}>
          <div className="bar" style={{ height: `${(d.counts[k] / max) * 100}%` }} />
          <span>{k}★</span>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [users, setUsers] = useState<string[]>([]);
  const [user, setUser] = useState("");
  const [k, setK] = useState(10);
  const [recs, setRecs] = useState<Rec[]>([]);
  const [hist, setHist] = useState<Hist[]>([]);
  const [dists, setDists] = useState<Record<number, Dist>>({});
  const [status, setStatus] = useState("connecting…");

  useEffect(() => {
    api("/health").then((h) => setStatus(`${h.users} users · ${h.movies} movies`)).catch(() => setStatus("API offline"));
    api("/users").then((d) => { setUsers(d.users); setUser(d.users[0]); });
  }, []);

  useEffect(() => {
    if (!user) return;
    const u = encodeURIComponent(user);
    api(`/recommendations/${u}?k=${k}`).then(async (d) => {
      setRecs(d.recommendations);
      const ds = await Promise.all(d.recommendations.map((r: Rec) => api(`/movies/${r.movie_id}/ratings`)));
      setDists(Object.fromEntries(ds.map((x: Dist) => [x.movie_id, x])));
    });
    api(`/users/${u}/history?limit=8`).then((d) => setHist(d.top_rated));
  }, [user, k]);

  return (
    <div className="page">
      <header>
        <h1>🎬 Movie Recommender</h1>
        <p>User-based collaborative filtering: find viewers with similar taste, suggest what they loved.</p>
        <span className="pill">{status}</span>
      </header>
      <section className="controls">
        <label>Viewer
          <select value={user} onChange={(e) => setUser(e.target.value)}>
            {users.map((u) => <option key={u}>{u}</option>)}
          </select>
        </label>
        <label>Similar users (k): <b>{k}</b>
          <input type="range" min={1} max={50} value={k} onChange={(e) => setK(+e.target.value)} />
        </label>
      </section>
      <div className="grid">
        <section className="card wide">
          <h2>Recommended for {user}</h2>
          <div className="recs">
            {recs.map((r, i) => (
              <div className="rec" key={r.movie_id}>
                <div className="rank">#{i + 1}</div>
                <div className="title">{r.title}</div>
                <div className="meta">neighbour score {r.score.toFixed(2)}{dists[r.movie_id] && ` · avg ${dists[r.movie_id].mean}★`}</div>
                {dists[r.movie_id] && <Bars d={dists[r.movie_id]} />}
              </div>
            ))}
          </div>
        </section>
        <section className="card">
          <h2>{user}'s favourites</h2>
          <ol className="hist">
            {hist.map((h) => <li key={h.movie_id}><span>{h.title}</span><b>{"★".repeat(h.rating)}</b></li>)}
          </ol>
        </section>
      </div>
    </div>
  );
}
