import { useQuery } from "@tanstack/react-query";
import { ApiError } from "@/lib/api";
import type { Overview } from "./types";

/** Shared catalogue query: one request backs home, matches, people and progress. */
export async function fetchOverview(signal?: AbortSignal): Promise<Overview> {
  const response = await fetch("/api/analytics/overview", { credentials: "same-origin", signal });
  if (!response.ok) {
    let message = response.statusText;
    try {
      const body: unknown = await response.json();
      if (body && typeof body === "object" && "detail" in body && typeof body.detail === "string")
        message = body.detail;
    } catch {
      /* Preserve the HTTP error for non-JSON failures. */
    }
    throw new ApiError(response.status, message);
  }
  const result = await response.json();
  if (
    result?.schema_version !== 1 ||
    !Array.isArray(result.matches) ||
    !Array.isArray(result.people) ||
    !result.progress
  ) {
    throw new Error(
      "The server returned an unsupported analytics response. Reload after updating the application.",
    );
  }
  return result as Overview;
}

export function useOverview() {
  return useQuery({
    queryKey: ["product-overview"],
    queryFn: ({ signal }) => fetchOverview(signal),
    refetchInterval: (query) =>
      query.state.data?.matches.some(({ session }) =>
        ["created", "ingesting", "ready_to_play", "analysing"].includes(session.status),
      )
        ? 5_000
        : 30_000,
  });
}
