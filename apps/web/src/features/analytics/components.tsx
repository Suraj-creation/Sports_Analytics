import { Play } from "lucide-react";
import type { ReactNode } from "react";
import { playEvidence } from "@/features/player/clip";

export function AnalysisPanel({
  title,
  hint,
  basis,
  children,
  preview,
}: {
  title: string;
  hint?: string;
  basis?: string;
  children: ReactNode;
  preview?: string;
}) {
  return (
    <section className="analysis-panel">
      <h2>
        {title}
        {preview && (
          <span className="analysis-preview" title={preview}>
            Preview
          </span>
        )}
      </h2>
      {hint && <p className="analysis-panel-hint">{hint}</p>}
      {preview && <p className="analysis-panel-hint">{preview}</p>}
      <div className="mt-4">{children}</div>
      {basis && <p className="analysis-basis">{basis}</p>}
    </section>
  );
}

export function AnalysisStat({ value, label, note }: { value: ReactNode; label: string; note?: string }) {
  return (
    <div className="analysis-stat">
      <div className="analysis-stat-value">{value ?? "—"}</div>
      <div className="analysis-stat-label">{label}</div>
      {note && <p className="analysis-stat-note">{note}</p>}
    </div>
  );
}

export function Watch({ start, end, label }: { start: number; end: number; label: string }) {
  return (
    <button
      type="button"
      className="analysis-watch"
      onClick={() => playEvidence(start, end, label)}
      aria-label={`Watch ${label}`}
    >
      <Play className="size-3" aria-hidden />
      Watch
    </button>
  );
}

export function Unavailable({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="analysis-panel">
      <h2>{title}</h2>
      <div className="analysis-panel-hint mt-3">{children}</div>
    </section>
  );
}
