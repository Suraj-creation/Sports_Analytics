import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { apiGet, apiPostJson } from "../lib/api";
import { useToast } from "../components/ToastProvider";
import { ClickableFrame } from "../features/courtTask/ClickableFrame";
import { CandidateThumbnails } from "../features/courtTask/CandidateThumbnails";
import "../features/courtTask/courtTask.css";

export function CourtTaskPage() {
  const { jobId } = useParams();
  const showToast = useToast();

  const [task, setTask] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [points, setPoints] = useState([]); // [{x,y,px,py}, ...]
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    apiGet(`/api/court-task/${jobId}`)
      .then((data) => { setTask(data); setSelectedIdx(data.selected_idx || 0); })
      .catch((err) => setLoadError(err.message));
  }, [jobId]);

  function handleFrameClick([x, y], [px, py]) {
    setPoints((prev) => [...prev, { x, y, px, py }]);
  }

  function handleUndo() {
    setPoints((prev) => prev.slice(0, -1));
  }

  async function handleSelectCandidate(idx) {
    if (idx === selectedIdx) return;
    setSelectedIdx(idx);
    setPoints([]);
    try {
      await apiPostJson(`/api/court-task/${jobId}/select-candidate`, { idx });
    } catch {
      /* best-effort -- submit still sends the currently-selected idx via
         the candidate's own frame data, so a failed sync here isn't fatal */
    }
  }

  async function handleSubmit() {
    setSubmitting(true);
    try {
      await apiPostJson(`/api/court-task/${jobId}/submit`, {
        points: points.map((p) => [p.x, p.y]),
      });
      setDone(true);
    } catch (err) {
      showToast("Save failed: " + err.message, true);
      setSubmitting(false);
    }
  }

  if (loadError) {
    return (
      <div className="fail-box" style={{ marginTop: 14, padding: "18px 20px", borderRadius: "var(--radius-md)", background: "var(--coral-soft)" }}>
        <p style={{ margin: 0, color: "var(--coral)", fontSize: 13.5 }}>{loadError}</p>
      </div>
    );
  }
  if (!task) return null;

  if (done) {
    return (
      <div className="card success-box">
        <h2 style={{ fontFamily: "var(--font-head)" }}>Saved</h2>
        <p style={{ color: "var(--ink-soft)" }}>The pipeline will now run unattended -- no need to wait here.</p>
        <Link className="btn btn-primary" to="/tasks" style={{ textDecoration: "none", marginTop: 10, display: "inline-block" }}>
          Back to my tasks
        </Link>
      </div>
    );
  }

  const candidate = task.candidates[selectedIdx];
  const n = points.length;

  return (
    <div style={{ maxWidth: 900 }}>
      <div className="hero-row" style={{ padding: "26px 0 14px" }}>
        <p className="eyebrow" style={{
          fontFamily: "var(--font-head)", fontSize: 11.5, fontWeight: 800,
          letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--court)", margin: "0 0 8px",
        }}>Court task</p>
        <h1 style={{ fontFamily: "var(--font-head)", fontWeight: 800, fontSize: 22, margin: "0 0 6px" }}>
          Click the 8 court points, in order
        </h1>
        <p style={{ color: "var(--ink-soft)", fontSize: 13.5, margin: 0 }}>
          Click each point on the image below in the order shown. Pick a different candidate frame first if this one doesn't clearly show the court.
        </p>
      </div>

      <div className="card">
        <div className="ct-bar">
          <span className="ct-next">
            {n < task.labels.length
              ? `Click ${task.labels[n]} -- ${task.descs[n]} (${n + 1} / ${task.labels.length})`
              : "All 8 points placed"}
          </span>
          <button className="btn btn-sm" onClick={handleUndo} disabled={!n}>Undo</button>
          {n >= task.labels.length && (
            <button className="btn btn-primary btn-sm" onClick={handleSubmit} disabled={submitting}>
              {submitting ? "Saving..." : "Save & submit"}
            </button>
          )}
        </div>
        <ClickableFrame
          src={candidate.image_url}
          width={candidate.width}
          height={candidate.height}
          points={points}
          colors={task.colors}
          labels={task.labels}
          onClick={handleFrameClick}
        />
        <CandidateThumbnails candidates={task.candidates} selectedIdx={selectedIdx} onSelect={handleSelectCandidate} />
      </div>
    </div>
  );
}
