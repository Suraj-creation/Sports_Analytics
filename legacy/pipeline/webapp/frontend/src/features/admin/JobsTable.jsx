import { useState } from "react";
import { usePolling } from "../../hooks/usePolling";
import { apiGet, apiPostJson } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";
import { Pill } from "../../components/Pill";
import { PIPELINE_LABEL, TASK_LABEL } from "./labels";

function AssignSelect({ jobId, task, status, currentAssignee, interns, onAssigned }) {
  const showToast = useToast();
  if ((task === "court" && status === "not_needed") ||
      (task === "review" && status === "not_ready") ||
      status === "submitted") {
    return null;
  }
  async function handleChange(e) {
    const internId = e.target.value;
    if (!internId) return;
    try {
      await apiPostJson(`/api/admin/jobs/${jobId}/assign-${task}`, { intern_id: parseInt(internId, 10) });
      showToast("Assigned");
      onAssigned();
    } catch (err) {
      showToast("Assign failed: " + err.message, true);
    }
  }
  return (
    <select className="assign-select" defaultValue={currentAssignee || ""} onChange={handleChange}>
      <option value="">-- assign --</option>
      {interns.map((a) => (
        <option key={a.id} value={a.id}>{a.username}</option>
      ))}
    </select>
  );
}

export function JobsTable({ interns }) {
  const [reloadKey, setReloadKey] = useState(0);
  const { data } = usePolling(() => apiGet("/api/admin/jobs"), {
    intervalMs: 2000, deps: [reloadKey],
  });
  const jobs = data?.jobs || [];

  const isFlagged = (j) => j.court_task_status === "flagged" || j.review_task_status === "flagged";
  const sorted = [...jobs].sort((a, b) => (isFlagged(b) ? 1 : 0) - (isFlagged(a) ? 1 : 0));

  return (
    <div className="card">
      <div className="card-head"><h2>Jobs</h2></div>
      <div className="table-scroll">
        <table className="jobs-table">
          <thead>
            <tr>
              <th>Match</th><th>Players</th><th>Court mode</th><th>Pipeline</th>
              <th>Court task</th><th>Review task</th><th>Uploaded by</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((j) => (
              <tr key={j.id}>
                <td><strong>{j.match_name}</strong></td>
                <td>{j.player_a} vs {j.player_b}</td>
                <td>{j.court_mode}</td>
                <td><Pill map={PIPELINE_LABEL} statusKey={j.status} /></td>
                <td>
                  <Pill map={TASK_LABEL} statusKey={j.court_task_status} />
                  {j.court_task_flag_reason && <div className="flag-reason">{j.court_task_flag_reason}</div>}
                  <AssignSelect jobId={j.id} task="court" status={j.court_task_status}
                                currentAssignee={j.court_task_assignee} interns={interns}
                                onAssigned={() => setReloadKey((k) => k + 1)} />
                </td>
                <td>
                  <Pill map={TASK_LABEL} statusKey={j.review_task_status} />
                  {j.review_task_flag_reason && <div className="flag-reason">{j.review_task_flag_reason}</div>}
                  <AssignSelect jobId={j.id} task="review" status={j.review_task_status}
                                currentAssignee={j.review_task_assignee} interns={interns}
                                onAssigned={() => setReloadKey((k) => k + 1)} />
                </td>
                <td className="assignee">{j.created_by || "--"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!sorted.length && <div className="empty-note">No jobs yet.</div>}
    </div>
  );
}
