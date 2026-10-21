import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowUp, BookOpen, CircleAlert } from "lucide-react";
import { Fragment, type ReactNode, useEffect, useRef, useState } from "react";
import { Empty, ErrorNote, Spinner } from "@/components/ui";
import { api } from "@/lib/api";
import { clock, fps as fpsOf, shortName } from "@/lib/format";
import type { AskAnswer, Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";

interface Turn {
  q: string;
  a?: AskAnswer;
  error?: unknown;
}

const CITE = /\[\[(ev|kb):([^\]]+)\]\]/g;

export function AskTab({ session }: { session: Session }) {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [q, setQ] = useState("");
  const listRef = useRef<HTMLDivElement>(null);
  const provider = useQuery({
    queryKey: ["ask-provider", session.session_id],
    queryFn: () => api.askProvider(session.session_id),
    staleTime: 60_000,
  });
  const ask = useMutation({
    mutationFn: (question: string) => {
      const history = turns
        .filter((t) => t.a)
        .slice(-5)
        .flatMap((t) => [
          { role: "user", content: t.q },
          { role: "assistant", content: t.a?.text ?? "" },
        ]);
      return api.ask(session.session_id, question, history);
    },
    onMutate: (question) => setTurns((t) => [...t, { q: question }]),
    onSuccess: (a) => setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, a } : x))),
    onError: (error) => setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, error } : x))),
  });

  // biome-ignore lint/correctness/useExhaustiveDependencies: scroll whenever a turn is added or answered
  useEffect(() => {
    const el = listRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [turns]);

  const p1 = shortName(session, "P1");
  const p2 = shortName(session, "P2");
  const suggestions = [
    `How did ${p1} win most of their points?`,
    `Show ${p2}'s smash winners`,
    "Which rally was the turning point?",
    `What should ${p1} change in the next game?`,
  ];
  const submit = (text: string) => {
    const t = text.trim();
    if (!t || ask.isPending) return;
    setQ("");
    ask.mutate(t);
  };

  return (
    <div className="flex h-full min-h-[360px] flex-col gap-3">
      {provider.data && !provider.data.available && (
        <p className="flex gap-2 rounded-lg border border-caution/40 bg-caution/10 px-3 py-2 text-sm">
          <CircleAlert className="mt-0.5 size-4 shrink-0 text-caution" aria-hidden />
          No language model is configured, so answers are built from the match data only. Set BAI_LLM_PROVIDER
          (and its key) in .env for written analysis.
        </p>
      )}
      <div ref={listRef} className="min-h-0 flex-1 space-y-5 overflow-y-auto pr-1" aria-live="polite">
        {!turns.length && (
          <div className="space-y-3">
            <Empty title="Ask about this match">
              Answers cite the rallies and shots they're based on — click a citation to watch that moment.
            </Empty>
            <div className="flex flex-wrap justify-center gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  type="button"
                  className="rounded-full border border-seam px-3 py-1.5 text-sm text-line-2 hover:border-line-3 hover:text-line"
                  onClick={() => submit(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {turns.map((t, i) => (
          // biome-ignore lint/suspicious/noArrayIndexKey: turns are append-only
          <div key={i} className="space-y-2">
            <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-stand-raised px-3.5 py-2 text-sm">
              {t.q}
            </p>
            {!t.a && !t.error && (
              <div className="flex items-center gap-2 text-sm text-line-2">
                <Spinner /> Looking through the match…
              </div>
            )}
            {t.error ? <ErrorNote error={t.error} /> : null}
            {t.a && <Answer a={t.a} session={session} />}
          </div>
        ))}
      </div>
      <form
        className="flex items-end gap-2 rounded-xl border border-seam bg-mat-deep p-1.5 focus-within:border-line-3"
        onSubmit={(e) => {
          e.preventDefault();
          submit(q);
        }}
      >
        <label htmlFor="ask" className="sr-only">
          Question
        </label>
        <textarea
          id="ask"
          rows={1}
          value={q}
          maxLength={1000}
          placeholder="Ask about rallies, shots, tactics…"
          className="max-h-32 min-h-9 flex-1 resize-none bg-transparent px-2 py-2 text-sm text-line placeholder:text-line-3 focus:outline-none"
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit(q);
            }
          }}
        />
        <button
          type="submit"
          aria-label="Ask"
          disabled={!q.trim() || ask.isPending}
          className="grid size-9 place-items-center rounded-lg bg-line text-mat-deep disabled:opacity-40"
        >
          <ArrowUp className="size-4" />
        </button>
      </form>
    </div>
  );
}

function Answer({ a, session }: { a: AskAnswer; session: Session }) {
  const seekFrame = usePlayback((s) => s.seekFrame);
  const fps = fpsOf(session.media);
  const evIndex = new Map<string, number>();
  for (const c of a.citations)
    if (c.kind === "ev" && !evIndex.has(c.ref)) evIndex.set(c.ref, evIndex.size + 1);
  const byRef = new Map(a.citations.map((c) => [c.ref, c]));

  const inline = (text: string, key: string): ReactNode[] => {
    const out: ReactNode[] = [];
    let last = 0;
    let n = 0;
    for (const m of text.matchAll(CITE)) {
      const [whole, kind, ref] = m as unknown as [string, "ev" | "kb", string];
      out.push(<Bold key={`${key}-t${n}`} text={text.slice(last, m.index)} />);
      const c = byRef.get(ref);
      if (kind === "ev") {
        out.push(
          <button
            key={`${key}-c${n}`}
            type="button"
            className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded-md bg-line/12 px-1 align-[1px] text-[11px] font-semibold tabular-nums text-line hover:bg-line hover:text-mat-deep"
            title={c?.frame != null ? `Watch at ${clock(c.frame, session.media)}` : "Event"}
            disabled={c?.frame == null}
            onClick={() => c?.frame != null && seekFrame(Math.max(0, c.frame - Math.round(fps)), fps)}
          >
            {evIndex.get(ref)}
          </button>,
        );
      } else {
        out.push(
          <span
            key={`${key}-c${n}`}
            title={`Background: ${ref}`}
            className="mx-0.5 inline-flex h-5 items-center rounded-md border border-seam px-1 align-[1px] text-line-3"
          >
            <BookOpen className="size-3" aria-label="background source" />
          </span>,
        );
      }
      last = (m.index ?? 0) + whole.length;
      n++;
    }
    out.push(<Bold key={`${key}-end`} text={text.slice(last)} />);
    return out;
  };

  const blocks = a.text.split(/\n{2,}/);
  return (
    <div className="space-y-2 text-sm leading-relaxed">
      {blocks.map((b, i) => {
        const lines = b.split("\n");
        const bullets = lines.every((l) => /^\s*([-*]|\d+[.)])\s+/.test(l));
        return bullets ? (
          // biome-ignore lint/suspicious/noArrayIndexKey: static text
          <ul key={i} className="list-disc space-y-1 pl-5">
            {lines.map((l, j) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: static text
              <li key={j}>{inline(l.replace(/^\s*([-*]|\d+[.)])\s+/, ""), `${i}-${j}`)}</li>
            ))}
          </ul>
        ) : (
          // biome-ignore lint/suspicious/noArrayIndexKey: static text
          <p key={i}>
            {lines.map((l, j) => (
              // biome-ignore lint/suspicious/noArrayIndexKey: static text
              <Fragment key={j}>
                {j > 0 && <br />}
                {inline(l, `${i}-${j}`)}
              </Fragment>
            ))}
          </p>
        );
      })}
      <p className="text-xs text-line-3">
        {a.grounded
          ? "Every match fact above is linked to its moment."
          : "Some statements couldn't be linked to match data."}
        {a.provider && ` · ${a.provider}${a.model ? ` ${a.model}` : ""}`}
      </p>
    </div>
  );
}

function Bold({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith("**") && p.endsWith("**") ? (
          // biome-ignore lint/suspicious/noArrayIndexKey: static text
          <strong key={i} className="font-semibold text-line">
            {p.slice(2, -2)}
          </strong>
        ) : (
          p
        ),
      )}
    </>
  );
}
