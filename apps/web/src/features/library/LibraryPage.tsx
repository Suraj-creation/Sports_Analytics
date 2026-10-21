import * as Dialog from "@radix-ui/react-dialog";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "@tanstack/react-router";
import { clsx } from "clsx";
import { CircleAlert, Trash2, Upload, Youtube } from "lucide-react";
import { useRef, useState } from "react";
import { Button, Empty, ErrorNote, Field, inputClass, Meter, Spinner } from "@/components/ui";
import { api, uploadVideo } from "@/lib/api";
import { playerName, STATUS_LABEL } from "@/lib/format";
import type { Session } from "@/lib/types";
import { Thumb } from "./Thumb";

const ACCEPT = "video/mp4,video/quicktime,video/x-matroska,video/webm,.mp4,.mov,.mkv,.webm,.m4v,.avi";

export function LibraryPage() {
  const sessions = useQuery({
    queryKey: ["sessions"],
    queryFn: api.sessions,
    refetchInterval: (q) =>
      q.state.data?.some((s) => ["created", "ingesting", "analysing", "ready_to_play"].includes(s.status))
        ? 3000
        : false,
  });
  const system = useQuery({ queryKey: ["system"], queryFn: api.system, staleTime: 60_000 });

  return (
    <div className="mx-auto max-w-7xl space-y-10 px-4 py-8 sm:px-6">
      <section className="grid items-start gap-4 lg:grid-cols-[1.4fr_1fr]">
        <UploadCard maxMb={system.data?.limits?.max_upload_mb} />
        <YouTubeCard enabled={Boolean(system.data?.youtube_ingest)} loading={system.isPending} />
      </section>

      <section className="space-y-4">
        <div className="flex items-baseline justify-between">
          <h2 className="text-lg font-semibold">Matches</h2>
          {sessions.data && (
            <span className="text-sm text-line-3">{sessions.data.length} in your library</span>
          )}
        </div>
        {sessions.isPending && (
          <div className="grid h-40 place-items-center">
            <Spinner />
          </div>
        )}
        <ErrorNote error={sessions.error} />
        {sessions.data?.length === 0 && (
          <div className="panel">
            <Empty title="No matches yet">
              Upload a match video or import one from YouTube to start analysing.
            </Empty>
          </div>
        )}
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {sessions.data?.map((s) => (
            <SessionCard key={s.session_id} s={s} />
          ))}
        </ul>
      </section>
    </div>
  );
}

function UploadCard({ maxMb }: { maxMb?: number }) {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [drag, setDrag] = useState(false);
  const [title, setTitle] = useState("");
  const [p1, setP1] = useState("");
  const [p2, setP2] = useState("");
  const [progress, setProgress] = useState<number | null>(null);
  const [error, setError] = useState<unknown>(null);
  const abortRef = useRef<(() => void) | null>(null);

  const pick = (f: File | undefined) => {
    if (!f) return;
    setError(null);
    if (maxMb && f.size > maxMb * 2 ** 20) {
      setError(
        new Error(`That file is ${(f.size / 2 ** 30).toFixed(1)} GB; this server accepts up to ${maxMb} MB.`),
      );
      return;
    }
    setFile(f);
    if (!title) setTitle(f.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " "));
  };

  const start = async () => {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    if (title) form.append("title", title);
    if (p1) form.append("player1", p1);
    if (p2) form.append("player2", p2);
    setProgress(0);
    setError(null);
    const up = uploadVideo(form, setProgress);
    abortRef.current = up.abort;
    try {
      const s = await up.promise;
      await qc.invalidateQueries({ queryKey: ["sessions"] });
      navigate({ to: "/sessions/$sessionId", params: { sessionId: s.session_id } });
    } catch (e) {
      setError(e);
      setProgress(null);
    } finally {
      abortRef.current = null;
    }
  };

  const uploading = progress !== null;
  return (
    <div className="panel space-y-5 p-5">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Analyse a match</h1>
        <p className="mt-1 text-sm text-line-2">
          The video starts playing as soon as it's prepared; shots, rallies and the score fill in while you
          watch.
        </p>
      </div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          pick(e.dataTransfer.files[0]);
        }}
        disabled={uploading}
        className={clsx(
          "flex w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-4 py-8 transition-colors",
          drag ? "border-signal bg-signal/5" : "border-seam bg-mat-deep/50 hover:border-line-3",
        )}
      >
        <Upload className="size-6 text-line-2" aria-hidden />
        {file ? (
          <span className="text-sm">
            <span className="font-medium">{file.name}</span>
            <span className="text-line-3"> · {(file.size / 2 ** 20).toFixed(0)} MB</span>
          </span>
        ) : (
          <span className="text-sm text-line-2">
            Drop a video here, or{" "}
            <span className="text-line underline underline-offset-4">choose a file</span>
          </span>
        )}
        <span className="text-xs text-line-3">
          MP4, MOV, MKV or WebM{maxMb ? ` · up to ${maxMb} MB` : ""}
        </span>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="sr-only"
        tabIndex={-1}
        onChange={(e) => pick(e.target.files?.[0])}
      />
      <div className="grid gap-3 sm:grid-cols-3">
        <Field label="Title">
          <input
            className={inputClass}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={120}
          />
        </Field>
        <Field label="Player 1" hint="Starts on the near side">
          <input className={inputClass} value={p1} onChange={(e) => setP1(e.target.value)} maxLength={80} />
        </Field>
        <Field label="Player 2" hint="Starts on the far side">
          <input className={inputClass} value={p2} onChange={(e) => setP2(e.target.value)} maxLength={80} />
        </Field>
      </div>
      <ErrorNote error={error} />
      <div className="flex items-center gap-3">
        <Button variant="primary" onClick={start} disabled={!file || uploading}>
          Analyse video
        </Button>
        {uploading && (
          <>
            <div className="flex-1">
              <Meter value={progress ?? 0} />
            </div>
            <span className="tabular w-24 text-right text-sm text-line-2">
              {progress !== null && progress < 1
                ? `Uploading ${Math.round(progress * 100)}%`
                : "Checking video"}
            </span>
            <Button variant="ghost" size="sm" onClick={() => abortRef.current?.()}>
              Cancel
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

function YouTubeCard({ enabled, loading }: { enabled: boolean; loading: boolean }) {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [url, setUrl] = useState("");
  const [p1, setP1] = useState("");
  const [p2, setP2] = useState("");
  const [ack, setAck] = useState(false);
  const create = useMutation({
    mutationFn: () =>
      api.youtube({ url, player1: p1 || undefined, player2: p2 || undefined, acknowledge_rights: ack }),
    onSuccess: async (s) => {
      await qc.invalidateQueries({ queryKey: ["sessions"] });
      navigate({ to: "/sessions/$sessionId", params: { sessionId: s.session_id } });
    },
  });

  return (
    <form
      className="panel flex flex-col gap-4 p-5"
      onSubmit={(e) => {
        e.preventDefault();
        create.mutate();
      }}
    >
      <div className="flex items-center gap-2">
        <Youtube className="size-5 text-line-2" aria-hidden />
        <h2 className="font-semibold">Import from YouTube</h2>
      </div>
      {!enabled && !loading ? (
        <p className="flex gap-2 text-sm text-line-2">
          <CircleAlert className="mt-0.5 size-4 shrink-0 text-caution" aria-hidden />
          YouTube import is turned off on this server. Set BAI_YOUTUBE_INGEST=true in .env and restart to use
          it.
        </p>
      ) : (
        <>
          <Field label="Video link">
            <input
              className={inputClass}
              type="url"
              inputMode="url"
              placeholder="https://www.youtube.com/watch?v=…"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              maxLength={300}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Player 1">
              <input
                className={inputClass}
                value={p1}
                onChange={(e) => setP1(e.target.value)}
                maxLength={80}
              />
            </Field>
            <Field label="Player 2">
              <input
                className={inputClass}
                value={p2}
                onChange={(e) => setP2(e.target.value)}
                maxLength={80}
              />
            </Field>
          </div>
          <label className="flex items-start gap-2.5 text-sm text-line-2">
            <input
              type="checkbox"
              className="mt-0.5 size-4 accent-[var(--color-signal)]"
              checked={ack}
              onChange={(e) => setAck(e.target.checked)}
            />
            <span>
              I have the rights to download and analyse this video. YouTube's terms restrict downloading
              content you don't own.
            </span>
          </label>
          <ErrorNote error={create.error} />
          <div className="mt-auto">
            <Button type="submit" variant="secondary" busy={create.isPending} disabled={!url || !ack}>
              Import and analyse
            </Button>
          </div>
        </>
      )}
    </form>
  );
}

function statusTone(s: Session["status"]): string {
  if (s === "failed") return "text-alert";
  if (s === "analysed") return "text-line-2";
  return "text-signal";
}

function SessionCard({ s }: { s: Session }) {
  const qc = useQueryClient();
  const del = useMutation({
    mutationFn: () => api.deleteSession(s.session_id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["sessions"] }),
  });
  const n = s.media?.n_frames ?? 0;
  const durationS = s.media ? s.media.duration_us / 1e6 : 0;
  const analysed = n ? Math.min(1, s.analysed_frames / n) : 0;
  const busy = ["created", "ingesting", "analysing", "ready_to_play"].includes(s.status);
  const players = s.players.length ? `${playerName(s, "P1")} vs ${playerName(s, "P2")}` : null;

  return (
    <li className="panel group relative flex flex-col transition-colors hover:border-line-3">
      <Thumb
        sessionId={s.session_id}
        durationS={durationS}
        ready={s.status !== "created" && s.status !== "ingesting"}
      />
      <div className="flex flex-1 flex-col gap-2 p-4">
        <Link
          to="/sessions/$sessionId"
          params={{ sessionId: s.session_id }}
          className="font-medium leading-snug after:absolute after:inset-0 after:content-['']"
        >
          {s.title}
        </Link>
        {players && <p className="text-sm text-line-2">{players}</p>}
        <div className="mt-auto flex items-center gap-2 pt-1 text-xs">
          <span className={clsx("inline-flex items-center gap-1.5 font-medium", statusTone(s.status))}>
            {busy && <span className="size-1.5 animate-pulse rounded-full bg-signal" aria-hidden />}
            {STATUS_LABEL[s.status] ?? s.status}
            {s.status === "analysing" && n > 0 && ` ${Math.round(analysed * 100)}%`}
          </span>
          {durationS > 0 && (
            <span className="tabular text-line-3">
              · {Math.floor(durationS / 60)}:{String(Math.floor(durationS % 60)).padStart(2, "0")}
            </span>
          )}
          <span className="ml-auto text-line-3">{new Date(s.created_at).toLocaleDateString()}</span>
        </div>
        {s.status === "analysing" && <Meter value={analysed} className="h-1" />}
        {s.status === "failed" && s.status_detail && <p className="text-xs text-line-2">{s.status_detail}</p>}
      </div>
      <Dialog.Root>
        <Dialog.Trigger asChild>
          <button
            type="button"
            aria-label={`Delete ${s.title}`}
            className="absolute top-2 right-2 z-10 grid size-8 place-items-center rounded-lg bg-mat-deep/80 text-line-2 opacity-0 transition-opacity hover:text-alert focus-visible:opacity-100 group-hover:opacity-100"
          >
            <Trash2 className="size-4" aria-hidden />
          </button>
        </Dialog.Trigger>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-40 bg-black/60" />
          <Dialog.Content className="panel fixed top-1/2 left-1/2 z-50 w-[min(92vw,420px)] -translate-x-1/2 -translate-y-1/2 space-y-4 p-5">
            <Dialog.Title className="font-semibold">Delete “{s.title}”?</Dialog.Title>
            <Dialog.Description className="text-sm text-line-2">
              This removes the analysis and your corrections for this match. The prepared video stays in the
              media cache, so adding the same file again doesn't re-encode it.
            </Dialog.Description>
            <ErrorNote error={del.error} />
            <div className="flex justify-end gap-2">
              <Dialog.Close asChild>
                <Button variant="ghost">Keep it</Button>
              </Dialog.Close>
              <Button variant="danger" busy={del.isPending} onClick={() => del.mutate()}>
                Delete match
              </Button>
            </div>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </li>
  );
}
