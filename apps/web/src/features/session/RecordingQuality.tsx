import { fps as fpsOf } from "@/lib/format";
import type { Session } from "@/lib/types";

const STAGE_NAMES: Record<string, string> = {
  named_identity: "Named player association",
  player_identity: "Appearance matching",
  player_reid: "Appearance matching provider",
  player_detector: "Player detection",
  pose: "Body pose",
  shuttle: "Shuttle tracking",
  racket: "Racket geometry",
  ocr: "Scoreboard reading",
  stroke: "Shot classification",
  contact: "Contact estimation",
  rally: "Rally segmentation",
};

function record(value: unknown): Record<string, unknown> | null {
  return value !== null && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;
}

export function RecordingQuality({ session }: { session: Session }) {
  const capabilities = record(session.meta.capabilities);
  const degradations = Array.isArray(session.meta.degraded) ? session.meta.degraded : null;
  const limitations = degradations
    ? [...new Map(degradations.map((value) => [String(JSON.stringify(value)), value])).entries()]
    : null;
  return (
    <>
      <h2 id="recording-quality-heading">What this recording can tell us</h2>
      <dl className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <dt className="text-line-2">Analysis proxy frames</dt>
          <dd>{session.media?.n_frames ? session.media.n_frames.toLocaleString() : "Media not prepared"}</dd>
        </div>
        <div>
          <dt className="text-line-2">Analysed frames</dt>
          <dd>{session.analysed_frames.toLocaleString()}</dd>
        </div>
        <div>
          <dt className="text-line-2">Frame rate</dt>
          <dd>{session.media ? `${fpsOf(session.media).toFixed(3)} fps` : "Unavailable"}</dd>
        </div>
        <div>
          <dt className="text-line-2">Identity evidence</dt>
          <dd>Visual track episodes are provisional. Named players require reviewed associations.</dd>
        </div>
      </dl>
      <p className="analysis-panel-hint mt-4">
        Frame numbers use the fixed-rate analysis proxy timeline. Processed frames do not measure rally
        coverage or detection accuracy. Shot labels and court movement remain estimates. Individual
        participants, track episodes and the two scoring slots have separate meanings.
      </p>
      <section className="mt-5" aria-label="Recorded analysis limitations">
        <h3 className="font-medium">Recorded analysis limitations</h3>
        {degradations?.length ? (
          <ul className="mt-2 space-y-2 text-sm">
            {limitations?.map(([key, value]) => {
              const item = record(value);
              if (typeof item?.stage !== "string" || typeof item?.reason !== "string")
                return <li key={key}>A saved limitation entry could not be read.</li>;
              return (
                <li key={key}>
                  <strong>{STAGE_NAMES[item.stage] ?? item.stage.replaceAll("_", " ")}</strong>: {item.reason}
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="analysis-panel-hint mt-2">
            {degradations
              ? "No degradation entries were recorded. This does not establish accuracy."
              : "Degradation metadata was not recorded for this saved analysis."}
          </p>
        )}
      </section>
      <section className="mt-5" aria-label="Reported component availability">
        <h3 className="font-medium">Reported component availability</h3>
        <p className="analysis-panel-hint mt-2">
          Availability describes the reported runtime state; it does not validate sporting accuracy.
        </p>
        {capabilities && Object.keys(capabilities).length ? (
          <dl className="mt-3 space-y-3 text-sm">
            {Object.entries(capabilities).map(([stage, value]) => {
              const item = record(value);
              const status = typeof item?.status === "string" ? item.status.replaceAll("_", " ") : "unknown";
              return (
                <div key={stage}>
                  <dt className="font-medium">
                    {STAGE_NAMES[stage] ?? stage.replaceAll("_", " ")} · {status}
                  </dt>
                  {typeof item?.reason === "string" && item.reason && (
                    <dd className="text-line-2">{item.reason}</dd>
                  )}
                </div>
              );
            })}
          </dl>
        ) : (
          <p className="analysis-panel-hint mt-2">Component availability metadata was not recorded.</p>
        )}
      </section>
    </>
  );
}
