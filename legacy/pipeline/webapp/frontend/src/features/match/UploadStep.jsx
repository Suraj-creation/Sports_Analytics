import { useRef, useState } from "react";
import { postFormWithProgress } from "../../lib/xhrUpload";

export function UploadStep({ onJobCreated }) {
  const fileInputRef = useRef(null);
  const [pickedFile, setPickedFile] = useState(null);
  const [playerA, setPlayerA] = useState("Player A");
  const [playerB, setPlayerB] = useState("Player B");
  const [matchName, setMatchName] = useState("");
  const [courtMode, setCourtMode] = useState("auto");
  const [broadcast, setBroadcast] = useState(true);
  const [drag, setDrag] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function pickFile(f) {
    if (f) setPickedFile(f);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!pickedFile) return;
    setError("");
    setSubmitting(true);
    setProgress(0);

    const fd = new FormData();
    fd.append("video", pickedFile);
    fd.append("player_a", playerA || "Player A");
    fd.append("player_b", playerB || "Player B");
    fd.append("match_name", matchName || "");
    fd.append("court_mode", courtMode);
    fd.append("court_type", "singles");
    fd.append("broadcast", broadcast ? "true" : "false");

    try {
      const job = await postFormWithProgress("/api/jobs", fd, setProgress);
      setProgress(null);
      onJobCreated(job.id);
    } catch (err) {
      setSubmitting(false);
      setProgress(null);
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="hero-row">
        <p className="eyebrow">New match</p>
        <h1 className="page-title">Upload a match to analyze</h1>
        <p className="page-lede">
          We'll detect the court, track the shuttle, find every rally, and call the winner
          automatically. Nothing here is final until you review it.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div
          className={"dropzone" + (drag ? " drag" : "")}
          tabIndex={0}
          role="button"
          aria-label="Choose match video"
          onClick={() => fileInputRef.current.click()}
          onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") fileInputRef.current.click(); }}
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragEnter={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={(e) => { e.preventDefault(); setDrag(false); }}
          onDrop={(e) => { e.preventDefault(); setDrag(false); pickFile(e.dataTransfer.files?.[0]); }}
        >
          <svg className="dropzone-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 16V4M12 4l-4 4M12 4l4 4" />
            <path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
          </svg>
          {pickedFile ? (
            <>
              <p><span className="picked">{pickedFile.name}</span></p>
              <p className="hint">{(pickedFile.size / (1024 * 1024)).toFixed(1)} MB -- click to choose a different file</p>
            </>
          ) : (
            <>
              <p>Drop your match video here, or click to browse</p>
              <p className="hint">MP4, MOV, or MKV -- full broadcast or a pre-trimmed clip both work</p>
            </>
          )}
          <input type="file" accept="video/*" style={{ display: "none" }} ref={fileInputRef}
                 onChange={(e) => pickFile(e.target.files?.[0])} />
        </div>

        <div className="field-grid">
          <div className="field">
            <label htmlFor="p1name"><span className="swatch-p1">&#9679;</span> Player 1 (far side)</label>
            <input type="text" id="p1name" value={playerA} onChange={(e) => setPlayerA(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="p2name"><span className="swatch-p2">&#9679;</span> Player 2 (near side)</label>
            <input type="text" id="p2name" value={playerB} onChange={(e) => setPlayerB(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="match-name">Match name (optional)</label>
            <input type="text" id="match-name" placeholder="Defaults to the file name"
                   value={matchName} onChange={(e) => setMatchName(e.target.value)} />
          </div>
          <div className="field">
            <label>Court annotation</label>
            <div className="radio-row">
              <label><input type="radio" checked={courtMode === "auto"} onChange={() => setCourtMode("auto")} /> Automatic</label>
              <label><input type="radio" checked={courtMode === "manual"} onChange={() => setCourtMode("manual")} /> Manual (click 4 corners)</label>
            </div>
          </div>
        </div>

        <label className="check-row">
          <input type="checkbox" checked={broadcast} onChange={(e) => setBroadcast(e.target.checked)} />
          Full broadcast (has intro/crowd/replay cutaways, not a pre-trimmed rally-only clip)
        </label>

        <div className="btn-row">
          <button type="submit" className="btn btn-primary" disabled={!pickedFile || submitting}>
            Start analysis
          </button>
          {progress != null && <span className="page-lede">Uploading... {progress}%</span>}
        </div>
        {error && <div className="form-error" style={{ display: "block" }}>{error}</div>}
      </form>
    </div>
  );
}
