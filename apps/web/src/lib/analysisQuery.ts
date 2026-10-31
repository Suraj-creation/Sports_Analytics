import type { Session } from "@/lib/types";
import { useSession } from "@/stores/session";

export function analysisRevision(session: Session | null | undefined): number {
  const revision = session?.meta.analysis_revision;
  return typeof revision === "number" && Number.isInteger(revision) && revision >= 0 ? revision : 0;
}

/** Keep existing invalidation prefixes while isolating in-flight analysis generations. */
export function analysisQueryKey(name: string, sessionId: string, revision: number, ...parts: unknown[]) {
  return [name, sessionId, ...parts, revision] as const;
}

/** Prefer the socket generation even while a caller still holds an older REST session. */
export function useAnalysisRevision(session: Session | string) {
  const id = typeof session === "string" ? session : session.session_id;
  const fallback = typeof session === "string" ? 0 : analysisRevision(session);
  return useSession((state) =>
    state.session?.session_id === id ? Math.max(fallback, analysisRevision(state.session)) : fallback,
  );
}

export function useAnalysisQueryKey(name: string, session: Session | string, ...parts: unknown[]) {
  const id = typeof session === "string" ? session : session.session_id;
  return analysisQueryKey(name, id, useAnalysisRevision(session), ...parts);
}
