import { useNavigate } from "react-router-dom";

const STATUS_LABEL = { pending: "New", in_progress: "In progress" };

export function TaskList({ title, items, kind, onFlag }) {
  const navigate = useNavigate();

  function openTask(jobId) {
    if (kind === "court") navigate(`/court-task/${jobId}`);
    else navigate(`/?job=${jobId}`);
  }

  return (
    <div className="card" style={{ marginBottom: 22 }}>
      <div className="card-head"><h2>{title}</h2></div>
      <div>
        {items.map((t) => (
          <div className="task-row" key={t.id}>
            <div style={{ flex: 1, cursor: "pointer" }} onClick={() => openTask(t.id)}>
              <div className="task-name">{t.player_a} vs {t.player_b}</div>
              <div className="task-sub">{t.match_name}</div>
            </div>
            <span className={`pill ${t.status === "pending" ? "pill-amber" : "pill-slate"}`}>
              {STATUS_LABEL[t.status] || t.status}
            </span>
            <button className="btn btn-sm btn-danger" onClick={() => onFlag(t)}>
              Can't complete
            </button>
          </div>
        ))}
      </div>
      {!items.length && <div className="empty-note">Nothing assigned right now.</div>}
    </div>
  );
}
