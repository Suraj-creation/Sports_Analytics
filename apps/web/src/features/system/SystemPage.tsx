import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Check, Cpu, HardDrive, X } from "lucide-react";
import { ErrorNote, Meter, Spinner } from "@/components/ui";
import { api } from "@/lib/api";

interface Gpu {
  index: number;
  name: string;
  util: number;
  mem_used_mb: number;
  mem_total_mb: number;
  power_w?: number;
  temp_c?: number;
}

export function SystemPage() {
  const sys = useQuery({ queryKey: ["system"], queryFn: api.system, refetchInterval: 3000 });
  const models = useQuery({ queryKey: ["models"], queryFn: api.models, staleTime: 30_000 });
  const d = sys.data;
  const gpus = (d?.system?.gpus ?? []) as Gpu[];
  const ort = d?.system?.onnxruntime as { version: string; providers: string[] } | null | undefined;
  const prof = d?.profile as Record<string, any> | null | undefined;

  return (
    <div className="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">System</h1>
        <p className="text-sm text-line-2">Compute, models and running analyses on this machine.</p>
      </div>
      {sys.isPending && <Spinner />}
      <ErrorNote error={sys.error} />

      {d && (
        <div className="grid items-start gap-4 md:grid-cols-3">
          <section className="panel space-y-3 p-4 md:col-span-2" aria-labelledby="gpu-h">
            <h2 id="gpu-h" className="flex items-center gap-2 font-semibold">
              <HardDrive className="size-4 text-line-2" aria-hidden /> GPU
            </h2>
            {gpus.length === 0 && (
              <p className="text-sm text-line-2">
                No NVIDIA GPU found{d.system?.cuda ? "" : " (CUDA unavailable)"} — analysis runs on the CPU,
                slower than real time.
              </p>
            )}
            {gpus.map((g) => (
              <div key={g.index} className="space-y-2">
                <p className="text-sm font-medium">{g.name}</p>
                <Stat label="Utilisation" value={`${g.util}%`} fraction={g.util / 100} />
                <Stat
                  label="Memory"
                  value={`${(g.mem_used_mb / 1024).toFixed(1)} / ${(g.mem_total_mb / 1024).toFixed(1)} GB`}
                  fraction={g.mem_used_mb / Math.max(1, g.mem_total_mb)}
                />
                {g.power_w != null && (
                  <p className="tabular text-xs text-line-2">Power {Math.round(g.power_w)} W</p>
                )}
              </div>
            ))}
          </section>
          <section className="panel space-y-2 p-4 text-sm" aria-labelledby="host-h">
            <h2 id="host-h" className="flex items-center gap-2 font-semibold">
              <Cpu className="size-4 text-line-2" aria-hidden /> Host
            </h2>
            <dl className="space-y-2">
              <KV k="Profile" v={prof?.name ?? "—"} />
              <KV k="Device" v={prof?.device ?? "—"} />
              <KV k="Engine" v={d.engine_mode} />
              <KV k="CPU cores" v={d.system?.cpu_count} />
              <KV k="Python" v={d.system?.python} />
              <KV k="ONNX Runtime" v={ort ? `${ort.version}` : "not installed"} />
              {ort && (
                <KV
                  k="Runtimes"
                  v={ort.providers.map((p) => p.replace("ExecutionProvider", "")).join(" · ")}
                />
              )}
              <KV k="YouTube import" v={d.youtube_ingest ? "on" : "off"} />
              <KV k="Upload limit" v={`${d.limits?.max_upload_mb} MB · ${d.limits?.max_duration_min} min`} />
            </dl>
          </section>
        </div>
      )}

      {d && (
        <section className="panel p-4" aria-labelledby="run-h">
          <h2 id="run-h" className="mb-2 font-semibold">
            Running analyses
          </h2>
          {(d.runners as { session_id: string; alive: boolean; main_segment: number }[]).length === 0 ? (
            <p className="text-sm text-line-2">Nothing is being analysed right now.</p>
          ) : (
            <ul className="space-y-1 text-sm">
              {(d.runners as { session_id: string; alive: boolean; main_segment: number }[]).map((r) => (
                <li key={r.session_id} className="flex items-center gap-3">
                  <span
                    className={clsx("size-2 rounded-full", r.alive ? "bg-signal" : "bg-line-3")}
                    aria-hidden
                  />
                  <span className="tabular">{r.session_id}</span>
                  <span className="text-line-2">{r.alive ? `segment ${r.main_segment}` : "finished"}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {prof && (
        <section className="panel p-4" aria-labelledby="prof-h">
          <h2 id="prof-h" className="mb-1 font-semibold">
            Profile · {prof.name}
          </h2>
          <p className="mb-3 text-sm text-line-2">{prof.description}</p>
          <dl className="grid gap-x-6 gap-y-1 text-sm sm:grid-cols-2 lg:grid-cols-3">
            {(["shuttle", "player_detector", "pose", "stroke", "contact", "racket", "ocr"] as const).map(
              (k) =>
                prof[k] ? (
                  <KV key={k} k={k.replace("_", " ")} v={(prof[k] as { model: string }).model} />
                ) : null,
            )}
            <KV k="analysis height" v={`${prof.analysis_height} px`} />
            <KV k="lead buffer" v={`${prof.lead_buffer_s} s`} />
          </dl>
        </section>
      )}

      <section className="panel overflow-hidden" aria-labelledby="models-h">
        <h2 id="models-h" className="p-4 pb-2 font-semibold">
          Models
        </h2>
        <ErrorNote error={models.error} />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-line-3">
              <tr className="border-b border-seam">
                <th className="px-4 py-2 font-medium">Model</th>
                <th className="px-4 py-2 font-medium">Task</th>
                <th className="px-4 py-2 font-medium">Format</th>
                <th className="px-4 py-2 font-medium">Licence</th>
                <th className="px-4 py-2 font-medium">Downloaded</th>
              </tr>
            </thead>
            <tbody>
              {models.data?.map((m) => (
                <tr key={m.name} className="border-b border-seam/60 last:border-0">
                  <td className="px-4 py-2">
                    <span className="font-medium">{m.name}</span>
                    {m.status !== "active" && <span className="ml-2 text-xs text-line-3">{m.status}</span>}
                  </td>
                  <td className="px-4 py-2 text-line-2">{m.task}</td>
                  <td className="px-4 py-2 text-line-2">{m.format}</td>
                  <td className="px-4 py-2 text-line-2">{m.license}</td>
                  <td className="px-4 py-2">
                    {m.available ? (
                      <span className="inline-flex items-center gap-1 text-signal">
                        <Check className="size-4" aria-hidden /> yes
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-line-3">
                        <X className="size-4" aria-hidden /> no
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="p-4 pt-2 text-xs text-line-3">
          Missing models download on first use; run <code>bai models fetch</code> to get them ahead of time.
        </p>
      </section>
    </div>
  );
}

function Stat({ label, value, fraction }: { label: string; value: string; fraction: number }) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-line-2">{label}</span>
        <span className="tabular">{value}</span>
      </div>
      <Meter value={fraction} tone="line" />
    </div>
  );
}

function KV({ k, v }: { k: string; v: unknown }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-line-2 first-letter:uppercase">{k}</dt>
      <dd className="tabular truncate text-right">{v == null ? "—" : String(v)}</dd>
    </div>
  );
}
