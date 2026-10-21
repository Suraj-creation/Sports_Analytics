import { useRef, useState } from "react";
import { apiPostForm } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";

export function BatchUploadForm({ onUploaded }) {
  const fileInputRef = useRef(null);
  const [playerA, setPlayerA] = useState("Player A");
  const [playerB, setPlayerB] = useState("Player B");
  const [courtMode, setCourtMode] = useState("auto");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const showToast = useToast();

  async function handleUpload() {
    const files = fileInputRef.current?.files;
    if (!files || !files.length) {
      setStatus("Choose one or more video files first.");
      return;
    }
    setBusy(true);
    setStatus(`Uploading ${files.length} file(s)...`);
    const fd = new FormData();
    for (const f of files) fd.append("video", f);
    fd.append("player_a", playerA || "Player A");
    fd.append("player_b", playerB || "Player B");
    fd.append("court_mode", courtMode);
    fd.append("court_type", "singles");
    fd.append("broadcast", "false");
    try {
      const data = await apiPostForm("/api/jobs/batch", fd);
      setStatus(`${data.created.length} job(s) created` +
        (data.errors.length ? `, ${data.errors.length} failed` : ""));
      showToast(`${data.created.length} job(s) queued`);
      fileInputRef.current.value = "";
      onUploaded();
    } catch (err) {
      setStatus("Batch upload failed: " + err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card" style={{ marginBottom: 22 }}>
      <div className="card-head"><h2>Batch upload</h2></div>
      <div style={{ padding: "16px 20px 20px" }}>
        <input type="file" accept="video/*" multiple ref={fileInputRef} style={{ marginBottom: 14 }} />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14, alignItems: "end" }}>
          <div className="field">
            <label htmlFor="batch-p1">Player A (default)</label>
            <input id="batch-p1" type="text" value={playerA} onChange={(e) => setPlayerA(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="batch-p2">Player B (default)</label>
            <input id="batch-p2" type="text" value={playerB} onChange={(e) => setPlayerB(e.target.value)} />
          </div>
          <div className="field">
            <label>Court annotation</label>
            <div style={{ display: "flex", gap: 14, marginTop: 6 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13.5, fontWeight: 400 }}>
                <input type="radio" name="batch-court-mode" checked={courtMode === "auto"}
                       onChange={() => setCourtMode("auto")} /> Automatic
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13.5, fontWeight: 400 }}>
                <input type="radio" name="batch-court-mode" checked={courtMode === "manual"}
                       onChange={() => setCourtMode("manual")} /> Manual (assign to interns)
              </label>
            </div>
          </div>
        </div>
        <button className="btn btn-primary btn-sm" style={{ marginTop: 16 }} onClick={handleUpload} disabled={busy}>
          Upload all
        </button>
        <span style={{ fontSize: 12.5, color: "var(--ink-faint)", marginLeft: 10 }}>{status}</span>
      </div>
    </div>
  );
}
