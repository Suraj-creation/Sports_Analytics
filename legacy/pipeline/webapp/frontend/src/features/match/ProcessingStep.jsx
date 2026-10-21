import { usePolling } from "../../hooks/usePolling";
import { apiGet, apiPost } from "../../lib/api";
import { useEffect, useState } from "react";

function ProcStepList({ job }) {
  if (job.status === "pending_court_task") {
    const note = job.court_task_status === "extracting" ? "Extracting candidate frames..."
      : job.court_task_status === "extraction_failed" ? "Frame extraction failed -- see Admin dashboard"
      : "Waiting for the court-annotation task to be assigned and submitted";
    return (
      <div className="proc-list">
        <div className="proc-item">
          <div className="proc-dot" />
          <div>
            <div className="proc-title" style={{ color: "var(--ink-faint)" }}>Court annotation needed</div>
            <div className="proc-note">{note}</div>
          </div>
        </div>
      </div>
    );
  }
  if (job.status === "queued") {
    return (
      <div className="proc-list">
        <div className="proc-item">
          <div className="proc-dot" />
          <div><div className="proc-title" style={{ color: "var(--ink-faint)" }}>Waiting in queue</div></div>
        </div>
      </div>
    );
  }
  const steps = job.steps_seen || [];
  if (!steps.length) {
    return (
      <div className="proc-list">
        <div className="proc-item active">
          <div className="proc-dot" />
          <div>
            <div className="proc-title">Starting up...</div>
            <div className="proc-note">Preprocessing the video (codec/resolution/fps check)</div>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="proc-list">
      {steps.map((s, i) => {
        const active = i === steps.length - 1 && job.status !== "done";
        return (
          <div className={"proc-item " + (active ? "active" : "done")} key={i}>
            <div className="proc-dot">
              {!active && (
                <svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              )}
            </div>
            <div><div className="proc-title">{s.label}</div></div>
          </div>
        );
      })}
    </div>
  );
}

export function ProcessingStep({ jobId, onDone, onRetry, onCancelledOrGiveUp }) {
  const { data: job } = usePolling(() => apiGet(`/api/jobs/${jobId}`), { intervalMs: 2000, deps: [jobId] });
  const [retrying, setRetrying] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (job?.status === "done") onDone(job);
    if (job?.status === "cancelled") onCancelledOrGiveUp();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [job?.status]);

  if (!job) return null;

  async function handleRetry() {
    setRetrying(true);
    try {
      const newJob = await apiPost(`/api/jobs/${jobId}/retry`);
      onRetry(newJob.id);
    } finally {
      setRetrying(false);
    }
  }

  async function handleCancel() {
    setCancelling(true);
    try {
      await apiPost(`/api/jobs/${jobId}/cancel`);
    } finally {
      setCancelling(false);
    }
  }

  return (
    <div>
      <div className="hero-row">
        <p className="eyebrow">Analyzing</p>
        <h1 className="page-title">Watching the match</h1>
        <p className="page-lede">This runs unattended except for one step -- confirming the court boundary, if you chose manual annotation.</p>
      </div>

      <ProcStepList job={job} />

      {job.status === "queued" && (
        <div className="wait-annotate">
          <h3>Queued</h3>
          <p>{job.queue_position ? `Waiting behind ${job.queue_position} other job${job.queue_position === 1 ? "" : "s"} already in the queue.` : "Next up -- the current job just needs to finish."}</p>
          <button className="btn btn-sm" style={{ marginTop: 10 }} onClick={handleCancel} disabled={cancelling}>
            Cancel this job
          </button>
          <span style={{ fontSize: 12, color: "var(--ink-soft)", marginLeft: 10 }}>
            Only jobs that haven't started yet can be cancelled -- once processing begins, let it finish or use Retry if it fails.
          </span>
        </div>
      )}

      {job.status === "pending_court_task" && job.court_task_status !== "extracting" && job.court_task_status !== "extraction_failed" && (
        <div className="wait-annotate">
          <h3>Waiting on court annotation</h3>
          <p>This match needs a court-annotation task before the pipeline can run. Assign it to yourself or an intern from the Admin dashboard -- this page will keep checking and move on automatically once it's submitted.</p>
        </div>
      )}

      {job.status === "failed" && (
        <div className="fail-box">
          <h3>Something went wrong</h3>
          <pre>{job.error || "(no details captured)"}</pre>
          <button className="btn btn-primary btn-sm" style={{ marginTop: 12 }} onClick={handleRetry} disabled={retrying}>
            {retrying ? "Retrying..." : "Retry from here"}
          </button>
          <span style={{ fontSize: 12, color: "var(--ink-soft)", marginLeft: 10 }}>
            Steps already completed are skipped -- only the failed step (and anything after it) re-runs.
          </span>
        </div>
      )}
    </div>
  );
}
