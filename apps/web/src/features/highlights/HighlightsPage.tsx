import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import { ArrowRight, Info, RotateCcw } from "lucide-react";
import { useId } from "react";
import { Page } from "@/features/product/ui";
import { HighlightsWorkspace } from "./HighlightsWorkspace";
import { useCollection } from "./useCollection";
import "./highlights.css";

export function HighlightsPage() {
  const id = useId();
  const search = useSearch({ from: "/highlights" });
  const navigate = useNavigate({ from: "/highlights" });
  const source = search.source ?? "example";
  const format = search.format ?? "doubles";
  const sessionId = search.session ?? "";
  const subjectId = search.subject ?? "";
  const change = (next: Partial<typeof search>) => {
    void navigate({ search: { ...search, ...next }, replace: true });
  };
  const setSource = (value: "example" | "recordings") => change({ source: value, subject: "" });
  const setFormat = (value: "singles" | "doubles") => change({ format: value, subject: "" });
  const setSession = (value: string) => change({ session: value, subject: "" });
  const setSubject = (value: string) => change({ subject: value });
  const data = useCollection(source, format, sessionId, subjectId);
  const collection = data.collection;
  return (
    <Page title="Highlights" lead="The parts you'll want to play again." className="hl-page">
      <div className="hl-source-toolbar">
        <div className="hl-source-switch" role="group" aria-label="Highlight source">
          <button type="button" aria-pressed={source === "example"} onClick={() => setSource("example")}>
            Example session
          </button>
          <button
            type="button"
            aria-pressed={source === "recordings"}
            onClick={() => setSource("recordings")}
          >
            Your recordings
          </button>
        </div>
        <div className="hl-scope-controls">
          {source === "example" ? (
            <label htmlFor={`${id}-format`}>
              Format
              <select
                id={`${id}-format`}
                value={format}
                onChange={(event) => setFormat(event.target.value as "singles" | "doubles")}
              >
                <option value="doubles">Doubles</option>
                <option value="singles">Singles</option>
              </select>
            </label>
          ) : (
            <label htmlFor={`${id}-session`}>
              Recording
              <select
                id={`${id}-session`}
                value={data.activeSessionId}
                disabled={!data.matches.length}
                onChange={(event) => setSession(event.target.value)}
              >
                {!data.matches.length && <option value="">No recordings loaded</option>}
                {data.matches.map(({ session }) => (
                  <option key={session.session_id} value={session.session_id}>
                    {session.title}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label htmlFor={`${id}-subject`}>
            Player or team
            <select
              id={`${id}-subject`}
              value={subjectId}
              disabled={!collection}
              onChange={(event) => setSubject(event.target.value)}
            >
              <option value="">Everyone</option>
              {Boolean(collection?.teams.length) && (
                <optgroup label="Teams / scoring sides">
                  {collection?.teams.map((team) => (
                    <option key={team.id} value={`team:${team.id}`}>
                      {team.name}
                    </option>
                  ))}
                </optgroup>
              )}
              {Boolean(collection?.participants.length) && (
                <optgroup label="Participants">
                  {collection?.participants.map((person) => (
                    <option key={person.id} value={`person:${person.id}`}>
                      {person.name}
                    </option>
                  ))}
                </optgroup>
              )}
            </select>
          </label>
        </div>
      </div>
      <div className="hl-source-notice">
        <Info size={16} aria-hidden />
        <p>
          {source === "example" ? (
            <>
              <strong>A look at what's possible.</strong> You're exploring synthetic names, moments and
              numbers. Your recordings are separate.
            </>
          ) : (
            <>
              <strong>Your recorded observations.</strong> Insights show their supporting evidence. Your
              personal picks stay on this device.
            </>
          )}
        </p>
      </div>
      {data.truncated && (
        <p className="hl-caption hl-scope-note">
          Showing the latest available recordings. This selection is not a complete history.
        </p>
      )}
      {data.loading ? (
        <div className="hl-loading" role="status" aria-live="polite">
          <p>Opening your highlight collection…</p>
          <div aria-hidden>
            <span />
            <span />
            <span />
          </div>
        </div>
      ) : data.error ? (
        <div className="hl-page-state" role="alert">
          <h2>We couldn't open these highlights</h2>
          <p>{data.error}</p>
          <div>
            <button type="button" className="hl-button hl-button-primary" onClick={data.refresh}>
              <RotateCcw size={16} aria-hidden />
              Try again
            </button>
            <button
              type="button"
              className="hl-button hl-button-quiet"
              onClick={() => {
                setSource("example");
              }}
            >
              Explore the example
            </button>
          </div>
        </div>
      ) : data.unsupported ? (
        <div className="hl-page-state">
          <h2>This sport's highlights aren't connected yet</h2>
          <p>
            Its recording is still available. These insight definitions won't be applied to a different sport.
          </p>
          <Link to="/matches" className="hl-button hl-button-quiet">
            See recordings
            <ArrowRight size={16} aria-hidden />
          </Link>
        </div>
      ) : collection ? (
        <HighlightsWorkspace
          key={`${collection.id}:${collection.sourceKey}:${collection.revision}`}
          collection={collection}
          subjectId={subjectId}
        />
      ) : (
        <div className="hl-page-state">
          <h2>A place for your next favourite.</h2>
          <p>
            There are no recordings in this collection yet. Explore the example to see the ten kinds of
            highlight.
          </p>
          <button type="button" className="hl-button hl-button-primary" onClick={() => setSource("example")}>
            Explore example highlights
            <ArrowRight size={16} aria-hidden />
          </button>
        </div>
      )}
    </Page>
  );
}
