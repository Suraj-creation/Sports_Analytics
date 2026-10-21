import { useState } from "react";
import { useReviewState, useReviewDispatch, sortedRallies } from "./ReviewContext";
import { apiPostJson } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";

export function ActionBar({ jobId }) {
  const { rallies, comments, dirtyCount, confirmed } = useReviewState();
  const dispatch = useReviewDispatch();
  const showToast = useToast();
  const [saving, setSaving] = useState(false);

  async function save(confirm) {
    setSaving(true);
    const payload = {
      rallies: sortedRallies(rallies).map((r) => ({
        id: r.id, start: Math.round(r.start * 100) / 100, end: Math.round(r.end * 100) / 100,
        winner: r.winner || null, reason: r.reason || null, source: r.source,
        flagged: !!r.flagged, note: r.note || null,
      })),
      comments, confirmed: !!confirm,
    };
    try {
      await apiPostJson(`/api/jobs/${jobId}/corrections`, payload);
      dispatch({ type: "SAVED", confirmed: !!confirm });
      showToast(confirm ? "Report finalized" : "Draft saved");
    } catch (err) {
      showToast("Save failed: " + err.message, true);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="actionbar">
      <div className="actionbar-inner">
        <div className="dirty-note">
          <span className={"dirty-dot" + (dirtyCount === 0 ? " clean" : "")} />
          <span>
            {confirmed && dirtyCount === 0 ? "All changes saved"
              : dirtyCount === 0 ? "No changes yet"
              : `${dirtyCount} unsaved edit${dirtyCount === 1 ? "" : "s"}`}
          </span>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button className="btn" onClick={() => save(false)} disabled={saving}>Save draft</button>
          <button className="btn btn-primary" onClick={() => save(true)} disabled={saving}>Confirm &amp; finalize</button>
        </div>
      </div>
    </div>
  );
}
