import { useEffect, useRef, useState } from "react";
import { apiGet } from "../../lib/api";
import { ReviewProvider, useReviewState, useReviewDispatch, fmt } from "./ReviewContext";
import { RallyTimeline } from "./RallyTimeline";
import { RallyTable } from "./RallyTable";
import { WinnerSummaryCard } from "./WinnerSummaryCard";
import { ReportCard } from "./ReportCard";
import { CommentsCard } from "./CommentsCard";
import { ActionBar } from "./ActionBar";

function Monitor({ videoRef, videoUrl }) {
  const { rallies, fps } = useReviewState();
  const [frame, setFrame] = useState(0);
  const [showBanner, setShowBanner] = useState(false);

  function update() {
    const t = videoRef.current?.currentTime || 0;
    setFrame(Math.round(t * fps));
    setShowBanner(rallies.some((r) => t >= r.start && t <= r.end));
  }

  return (
    <div className="card">
      <div className="monitor">
        <video ref={videoRef} controls preload="auto" src={videoUrl}
               onTimeUpdate={update} onLoadedMetadata={update} />
        <div className={"rally-banner" + (showBanner ? " show" : "")}>
          <span className="rb-dot" />RALLY DETECTED
        </div>
        <div className="monitor-frame">frame {frame}</div>
      </div>
    </div>
  );
}

function ReviewInner({ jobId, data }) {
  const { rallies, total, confirmed, dirtyCount } = useReviewState();
  const dispatch = useReviewDispatch();
  const videoRef = useRef(null);

  useEffect(() => {
    dispatch({
      type: "INIT",
      rallies: data.rallies || [],
      comments: data.comments,
      confirmed: data.confirmed,
      total: data.total_duration,
      fps: data.fps,
      playerA: data.player_a,
      playerB: data.player_b,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  const statusConfirmed = confirmed && dirtyCount === 0;

  return (
    <div>
      <div className="review-head">
        <div>
          <h1 className="match-title">{data.player_a} vs {data.player_b}</h1>
          <div className="match-meta">
            <span>{fmt(total)} &middot; {rallies.length} rallies detected</span>
            {data.presence_pct != null && (
              <span className="dot-sep">{data.presence_pct}% of video is court footage</span>
            )}
          </div>
        </div>
        <span className={"pill " + (statusConfirmed ? "pill-court" : "pill-amber")}>
          {statusConfirmed ? "Confirmed" : "Needs review"}
        </span>
      </div>

      <div className="review-grid">
        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <Monitor videoRef={videoRef} videoUrl={data.video_url} />
          <RallyTimeline videoRef={videoRef} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <RallyTable />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 22 }}>
          <WinnerSummaryCard />
          <ReportCard reportText={data.report_text} reportPdfUrl={data.report_pdf_url} />
          <CommentsCard />
          <div className="card" style={{ padding: "14px 20px", fontSize: 12.5, color: "var(--ink-faint)", lineHeight: 1.6 }}>
            Corrections are saved separately from the model's own output
            (<code style={{ fontFamily: "var(--font-mono)" }}>corrections.json</code>) -- the
            original detection is never overwritten.
          </div>
        </div>
      </div>

      <ActionBar jobId={jobId} />
    </div>
  );
}

export function ReviewStep({ jobId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    apiGet(`/api/jobs/${jobId}/data`)
      .then(setData)
      .catch((err) => setError("Pipeline finished but review data couldn't be loaded: " + err.message));
  }, [jobId]);

  if (error) {
    return (
      <div className="fail-box">
        <h3>Something went wrong</h3>
        <pre>{error}</pre>
      </div>
    );
  }
  if (!data) return null;

  return (
    <ReviewProvider>
      <ReviewInner jobId={jobId} data={data} />
    </ReviewProvider>
  );
}
