import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { fetchOverview } from "@/features/product/api";
import { req } from "@/lib/api";
import { DEFAULT_EXAMPLE_SPORT, highlightProvider } from "./providers";

export function useCollection(
  source: "example" | "recordings",
  format: "singles" | "doubles",
  sessionId: string,
  subjectId: string,
) {
  const overview = useQuery({
    queryKey: ["highlights-recordings"],
    queryFn: ({ signal }) => fetchOverview(signal),
    enabled: source === "recordings",
    retry: false,
    staleTime: 30_000,
  });
  const match =
    overview.data?.matches.find((entry) => entry.session.session_id === sessionId) ??
    overview.data?.matches[0];
  const provider = match ? highlightProvider(match.session.sport) : undefined;
  const revision = match?.session.meta.analysis_revision ?? 0;
  const snapshot = useQuery({
    queryKey: [
      "highlights-snapshot",
      match?.session.session_id,
      revision,
      match?.lineage.event_seq,
      match?.lineage.metric_version,
      match?.session.source.sha256,
    ],
    queryFn: ({ signal }) =>
      req<unknown>(`/api/sessions/${encodeURIComponent(match?.session.session_id ?? "")}/insights`, {
        signal,
      }),
    enabled: source === "recordings" && Boolean(match && provider),
    retry: false,
  });
  const result = useMemo(() => {
    if (source === "example")
      return { collection: highlightProvider(DEFAULT_EXAMPLE_SPORT)?.example(format) ?? null, issue: null };
    if (!match || !provider || !snapshot.data) return { collection: null, issue: null };
    try {
      return { collection: provider.fromRecording(match, snapshot.data, subjectId), issue: null };
    } catch (error) {
      return {
        collection: null,
        issue: error instanceof Error ? error.message : "This recording's highlights could not be read.",
      };
    }
  }, [source, format, match, provider, snapshot.data, subjectId]);
  return {
    ...result,
    matches: overview.data?.matches ?? [],
    loading:
      source === "recordings" && (overview.isPending || Boolean(match && provider && snapshot.isPending)),
    error:
      source === "recordings" ? (overview.error?.message ?? snapshot.error?.message ?? result.issue) : null,
    unsupported: source === "recordings" && Boolean(match && !provider),
    truncated: source === "recordings" && overview.data?.scope.truncated,
    activeSessionId: match?.session.session_id ?? "",
    refresh: () => {
      void overview.refetch();
      if (match && provider) void snapshot.refetch();
    },
  };
}
