import { FileDown, FileJson, FileSpreadsheet, FileText } from "lucide-react";
import { exportUrl } from "@/lib/api";
import type { Session } from "@/lib/types";

const ITEMS = [
  {
    kind: "report.pdf",
    icon: FileText,
    title: "Match report",
    body: "Player statistics, the top highlights and every rally, as a PDF.",
  },
  {
    kind: "rallies.csv",
    icon: FileSpreadsheet,
    title: "Rallies table",
    body: "One row per rally: game, start and end time, winner, outcome and the shots played.",
  },
  {
    kind: "legacy.csv",
    icon: FileSpreadsheet,
    title: "Classic CSV",
    body: "The 8-column format the earlier Streamlit app reads.",
  },
  {
    kind: "events.jsonl",
    icon: FileJson,
    title: "Event log",
    body: "Every event with evidence, confidence and corrections — the source of truth, one JSON per line.",
  },
  { kind: "summary.json", icon: FileJson, title: "Summary", body: "Final state and statistics as JSON." },
];

export function ExportTab({ session }: { session: Session }) {
  const done = session.status === "analysed";
  return (
    <div className="space-y-3">
      {!done && (
        <p className="text-sm text-line-2">
          Analysis is still running — exports include everything analysed so far.
        </p>
      )}
      <ul className="grid gap-2 md:grid-cols-2">
        {ITEMS.map((it) => (
          <li key={it.kind}>
            <a
              href={exportUrl(session.session_id, it.kind)}
              download
              className="panel flex items-start gap-3 p-3 transition-colors hover:border-line-3"
            >
              <it.icon className="mt-0.5 size-5 shrink-0 text-line-2" aria-hidden />
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-medium">{it.title}</span>
                <span className="block text-xs text-line-2">{it.body}</span>
              </span>
              <FileDown className="size-4 shrink-0 text-line-3" aria-hidden />
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
