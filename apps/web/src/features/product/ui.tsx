import { Link } from "@tanstack/react-router";
import { ArrowRight, Play } from "lucide-react";
import { type ReactNode, useEffect, useRef } from "react";
import type { Highlight } from "@/lib/types";
import { useOverview } from "./api";
import { dateLabel, processingPercent, strokeLabel } from "./model";
import type { MatchSummary, Overview } from "./types";
import "./product.css";

export function Page({ title, lead, children }: { title: string; lead?: string; children: ReactNode }) {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
  }, []);
  return (
    <div className="rally-page">
      <header className="rally-page-heading">
        <h1 ref={heading} tabIndex={-1}>
          {title}
        </h1>
        {lead && <p>{lead}</p>}
      </header>
      {children}
    </div>
  );
}
export function Card({
  title,
  children,
  className = "",
}: {
  title?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rally-card ${className}`}>
      {title && <h2>{title}</h2>}
      {children}
    </section>
  );
}
export function Stat({
  value,
  label,
  unit,
  detail,
}: {
  value: number | string | null | undefined;
  label: string;
  unit?: string;
  detail?: string;
}) {
  return (
    <div className={`rally-stat ${value == null ? "rally-missing" : ""}`}>
      <p className="rally-figure">
        {typeof value === "number"
          ? value.toLocaleString(undefined, { maximumFractionDigits: 1 })
          : (value ?? "—")}{" "}
        {value != null && unit && <small>{unit}</small>}
      </p>
      <p className="rally-stat-label">{label}</p>
      {detail && <p className="rally-caption">{detail}</p>}
    </div>
  );
}
export function Empty({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card title={title}>
      <p className="rally-muted">{children}</p>
    </Card>
  );
}
export function Catalogue({
  title,
  lead,
  children,
}: {
  title: string;
  lead?: string;
  children: (data: Overview) => ReactNode;
}) {
  const query = useOverview();
  return (
    <Page title={title} lead={lead}>
      {query.isPending ? (
        <div className="rally-card" role="status">
          Loading your matches…
        </div>
      ) : query.isError ? (
        <div className="rally-card" role="alert">
          <h2>We couldn’t load your analytics</h2>
          <p>{query.error.message}</p>
          <button type="button" className="rally-action" onClick={() => query.refetch()}>
            Try again
          </button>
        </div>
      ) : (
        <>
          {query.isRefetchError && (
            <p role="status">Updates are temporarily unavailable. Showing the last saved response.</p>
          )}
          {query.data.scope?.truncated && (
            <p className="rally-caption" role="status">
              Showing the latest {query.data.scope.returned_matches} recordings. Totals, people and progress
              apply to this selection.
            </p>
          )}
          {children(query.data)}
        </>
      )}
    </Page>
  );
}
export function MatchLink({
  id,
  tab = "overview",
  frame,
  children,
  className,
}: {
  id: string;
  tab?: string;
  frame?: number | null;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Link
      to="/matches/$matchId"
      params={{ matchId: id }}
      search={{ tab, ...(frame != null ? { f: frame } : {}) }}
      className={className}
    >
      {children}
    </Link>
  );
}
export function Status({ match }: { match: MatchSummary }) {
  const { session } = match;
  const progress = processingPercent(session.analysed_frames, session.media?.n_frames ?? 0);
  const labels: Record<string, string> = {
    created: "Queued",
    ingesting: "Preparing video",
    ready_to_play: "Ready to analyse",
    analysing: "Analysing",
    analysed: "Analysed",
    failed: "Processing failed",
  };
  return (
    <span className="rally-status">
      {labels[session.status] ?? session.status}
      {session.status === "analysing" && progress != null ? ` ${progress}%` : ""}
    </span>
  );
}
export function MatchCard({ match, hero = false }: { match: MatchSummary; hero?: boolean }) {
  const { session, analytics } = match;
  const lastScore = analytics?.score_timeline.at(-1)?.score;
  return (
    <Card className={hero ? "rally-match-hero" : "rally-match-card"}>
      <div className="product-card-heading">
        <div>
          <p className="rally-eyebrow">
            {dateLabel(session.created_at)} · <Status match={match} />
          </p>
          <h2>
            <MatchLink id={session.session_id}>{session.title}</MatchLink>
          </h2>
          <p className="rally-muted">
            {session.players.map((p) => p.name || p.player_id).join(" vs ")}
            {lastScore ? ` · ${lastScore.P1}–${lastScore.P2}` : ""}
          </p>
        </div>
        <MatchLink id={session.session_id} className={hero ? "rally-action" : "rally-text-action"}>
          Open the match <ArrowRight size={16} aria-hidden />
        </MatchLink>
      </div>
      {analytics ? (
        <div className="rally-stats">
          <MatchLink id={session.session_id} tab="rallies">
            <Stat value={analytics.rallies} label="Counted rallies" />
          </MatchLink>
          <MatchLink id={session.session_id} tab="rallies">
            <Stat
              value={analytics.rallies ? analytics.longest_rally_shots : null}
              unit="shots"
              label="Longest rally"
            />
          </MatchLink>
          <MatchLink id={session.session_id} tab="rallies">
            <Stat value={analytics.avg_rally_shots} unit="shots" label="Average rally" />
          </MatchLink>
          <MatchLink id={session.session_id} tab="moments">
            <Stat value={match.highlights.length} label="Moments to watch" detail="Up to 10 ranked moments" />
          </MatchLink>
        </div>
      ) : (
        <p className="rally-muted">
          {match.availability.reason ||
            session.status_detail ||
            "Analytics will appear when processing is complete."}
        </p>
      )}
      {hero && match.highlights[0] && <MomentRow match={match} highlight={match.highlights[0]} />}
    </Card>
  );
}
export function MomentRow({ match, highlight }: { match: MatchSummary; highlight: Highlight }) {
  const fps = match.session.media ? match.session.media.fps_num / match.session.media.fps_den : null;
  return (
    <MatchLink
      id={match.session.session_id}
      tab="moments"
      frame={highlight.frame_start}
      className="rally-moment"
    >
      <span className="rally-play">
        <Play size={18} aria-hidden />
      </span>
      <span>
        <strong>
          Rally {highlight.rally_no} · {highlight.categories.map(strokeLabel).join(" · ") || "Match moment"}
        </strong>
        <span className="rally-caption">
          {match.session.title}
          {fps
            ? ` · ${(highlight.frame_start / fps).toFixed(1)}s–${(highlight.frame_end / fps).toFixed(1)}s`
            : ""}
        </span>
      </span>
      <ArrowRight size={16} aria-hidden />
    </MatchLink>
  );
}
