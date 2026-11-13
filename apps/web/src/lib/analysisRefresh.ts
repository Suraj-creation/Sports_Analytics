import { type QueryClient, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { useSession } from "@/stores/session";
import { analysisRevision, useAnalysisQueryKey } from "./analysisQuery";
import type { Session } from "./types";

/** Raw events/overlays remain live; expensive derived snapshots refresh at most this often. */
export const ANALYSIS_REFRESH_MS = 2000;
type Key = readonly unknown[];
type Snapshot = { version: number; revision: number; processing: boolean };
type Registration = { key: Key; count: number };
const clients = new WeakMap<QueryClient, Map<string, Coordinator>>();

function snapshot(id: string): Snapshot | null {
  const state = useSession.getState();
  if (state.session?.session_id !== id) return null;
  return {
    version: state.analyticsVersion,
    revision: analysisRevision(state.session),
    processing: ["created", "ingesting", "ready_to_play", "analysing"].includes(state.session.status),
  };
}

/** One invalidation owner per client/session, including when several widgets observe the same query. */
class Coordinator {
  readonly keys = new Map<string, Registration>();
  private latest: Snapshot | null;
  private timer: ReturnType<typeof setTimeout> | null = null;
  private lastRefresh = Date.now();
  private dirty = false;
  private flushing = false;
  private cycle = 0;
  private stopped = false;
  private readonly unsubscribe: () => void;

  constructor(
    private readonly client: QueryClient,
    private readonly id: string,
  ) {
    this.latest = snapshot(id);
    this.unsubscribe = useSession.subscribe(() => this.changed());
  }

  private clearTimer() {
    if (this.timer !== null) clearTimeout(this.timer);
    this.timer = null;
  }

  private changed() {
    const next = snapshot(this.id);
    if (!next) return;
    const previous = this.latest;
    this.latest = next;
    if (!previous || next.revision !== previous.revision) {
      // New revision keys fetch themselves. Old in-flight work cannot schedule a follow-up in this epoch.
      this.clearTimer();
      this.cycle++;
      this.flushing = false;
      this.dirty = false;
      this.lastRefresh = Date.now();
      return;
    }
    if (next.version === previous.version && next.processing === previous.processing) return;
    this.dirty = true;
    if (previous.processing && !next.processing) {
      // Completion must supersede a live request that may hold a pre-completion snapshot.
      this.clearTimer();
      this.timer = setTimeout(() => this.flush(true), 0);
    } else if (!this.flushing) this.schedule();
  }

  private schedule() {
    if (this.stopped || !this.dirty || this.timer !== null) return;
    const delay = this.latest?.processing
      ? Math.max(0, ANALYSIS_REFRESH_MS - (Date.now() - this.lastRefresh))
      : 0;
    this.timer = setTimeout(() => this.flush(!this.latest?.processing), delay);
  }

  private flush(supersede: boolean) {
    this.timer = null;
    if (this.stopped || !this.dirty) return;
    const revision = this.latest?.revision;
    const matches = (key: Key) => {
      const registered = this.keys.get(JSON.stringify(key));
      return Boolean(registered && key.at(-1) === revision);
    };
    const queries = this.client.getQueryCache().findAll({ predicate: (query) => matches(query.queryKey) });
    // A live request already in progress can finish with older inputs. Follow it once rather than cancelling it repeatedly.
    const inheritedRequest = !supersede && queries.some((query) => query.state.fetchStatus === "fetching");
    this.dirty = false;
    this.flushing = true;
    this.lastRefresh = Date.now();
    const cycle = ++this.cycle;
    const invalidate = () =>
      this.client.invalidateQueries(
        { predicate: (query) => matches(query.queryKey) },
        { cancelRefetch: false },
      );
    // invalidateQueries alone does not cancel a query's first request when no cached data exists.
    const refresh = supersede
      ? this.client.cancelQueries({ predicate: (query) => matches(query.queryKey) }).then(() => {
          if (!this.stopped && cycle === this.cycle) return invalidate();
        })
      : invalidate();
    void refresh.finally(() => {
      if (this.stopped || cycle !== this.cycle) return;
      this.flushing = false;
      this.dirty ||= inheritedRequest;
      this.schedule();
    });
  }

  stop() {
    this.stopped = true;
    this.cycle++;
    this.clearTimer();
    this.unsubscribe();
  }
}

function observe(client: QueryClient, id: string, key: Key) {
  let sessions = clients.get(client);
  if (!sessions) {
    sessions = new Map();
    clients.set(client, sessions);
  }
  let coordinator = sessions.get(id);
  if (!coordinator) {
    coordinator = new Coordinator(client, id);
    sessions.set(id, coordinator);
  }
  const hash = JSON.stringify(key);
  const registered = coordinator.keys.get(hash);
  if (registered) registered.count++;
  else coordinator.keys.set(hash, { key, count: 1 });
  return () => {
    const entry = coordinator.keys.get(hash);
    if (entry && --entry.count === 0) coordinator.keys.delete(hash);
    if (!coordinator.keys.size) {
      coordinator.stop();
      sessions.delete(id);
    }
  };
}

/** Register only derived analysis queries; their observation/event sources keep their immediate path. */
export function useLiveAnalysisQueryKey(name: string, session: Session | string, ...parts: unknown[]) {
  const client = useQueryClient();
  const key = useAnalysisQueryKey(name, session, ...parts);
  const id = typeof session === "string" ? session : session.session_id;
  const hash = JSON.stringify(key);
  // biome-ignore lint/correctness/useExhaustiveDependencies: hash represents the complete primitive query key.
  useEffect(() => observe(client, id, key), [client, id, hash]);
  return key;
}
