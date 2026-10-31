import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ErrorNote, Field, inputClass } from "@/components/ui";
import { useAnalysisQueryKey, useAnalysisRevision } from "@/lib/analysisQuery";
import { req } from "@/lib/api";
import type { Session } from "@/lib/types";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

interface ServiceState {
  status: "known" | "unknown";
  reason?: string;
  server_participant_id?: string;
  receiver_participant_id?: string;
  service_court?: string;
  analysis_revision: number;
}

export function DoublesService({ session }: { session: Session }) {
  const frame = usePlayback((state) => state.frame);
  const events = useSession((state) => state.events);
  const version = useSession((state) => state.eventsVersion);
  // biome-ignore lint/correctness/useExhaustiveDependencies: version signals mutation of the shared event log.
  const changes = useMemo(
    () => [
      events.latestBefore("point", frame)?.event_id,
      events.latestBefore("doubles_service_setup", frame)?.event_id,
    ],
    [events, version, frame],
  );
  const revision = useAnalysisRevision(session);
  const client = useQueryClient();
  const base = `/api/sessions/${encodeURIComponent(session.session_id)}/doubles-service`;
  const query = useQuery({
    queryKey: useAnalysisQueryKey("doubles-service", session, ...changes),
    queryFn: ({ signal }) => req<ServiceState>(`${base}?frame=${frame}`, { signal }),
  });
  const people = session.roster?.participants ?? [];
  const [server, setServer] = useState("");
  const [receiver, setReceiver] = useState("");
  const [setupFrame, setSetupFrame] = useState(0);
  const serving = people.find((person) => person.participant_id === server) ?? people[0];
  const opponents = people.filter((person) => person.team_id && person.team_id !== serving?.team_id);
  const receiving = opponents.find((person) => person.participant_id === receiver) ?? opponents[0];
  const teamsReady =
    session.roster?.teams.length === 2 &&
    new Set(session.roster.teams.map((team) => team.score_slot).filter(Boolean)).size === 2 &&
    session.roster.teams.every(
      (team) => people.filter((person) => person.team_id === team.team_id).length === 2,
    );
  const mutation = useMutation({
    mutationFn: () =>
      req(base, {
        method: "POST",
        body: JSON.stringify({
          server_participant_id: serving?.participant_id,
          receiver_participant_id: receiving?.participant_id,
          frame: setupFrame,
          analysis_revision: revision,
        }),
      }),
    onSuccess: () => client.invalidateQueries({ queryKey: ["doubles-service", session.session_id] }),
  });
  const name = (id: string | undefined) =>
    people.find((person) => person.participant_id === id)?.name || "Unnamed player";
  return (
    <section className="mt-4 space-y-3" aria-label="Doubles service order">
      <h3 className="font-medium">Partner service order</h3>
      {query.data?.status === "known" ? (
        <p className="text-sm">
          {name(query.data.server_participant_id)} serves to {name(query.data.receiver_participant_id)} ·{" "}
          {query.data.service_court} court
        </p>
      ) : (
        <p className="text-sm text-line-2">
          Partner service order unknown. Choose the opening pair only when this recording begins at 0–0. A
          later game or changed score evidence needs a new explicit selection.
        </p>
      )}
      {!teamsReady && (
        <p className="text-sm text-line-2">
          Assign two players to each team and map the teams to P1/P2 score slots in Participants first.
        </p>
      )}
      <form
        className="grid gap-3 sm:grid-cols-2"
        onSubmit={(event) => {
          event.preventDefault();
          if (teamsReady) mutation.mutate();
        }}
      >
        <Field label="Service setup frame">
          <input
            className={inputClass}
            type="number"
            min={0}
            max={(session.media?.n_frames ?? 1) - 1}
            required
            value={setupFrame}
            onChange={(event) => setSetupFrame(event.target.valueAsNumber)}
          />
        </Field>
        <button className="rally-action" type="button" onClick={() => setSetupFrame(frame)}>
          Use current frame
        </button>
        <Field label={setupFrame === 0 ? "Opening server" : "Server at selected frame"}>
          <select
            className={inputClass}
            value={serving?.participant_id ?? ""}
            onChange={(event) => {
              setServer(event.target.value);
              setReceiver("");
            }}
          >
            {people.map((person, index) => (
              <option value={person.participant_id} key={person.participant_id}>
                {person.name || `Player ${index + 1}`}
              </option>
            ))}
          </select>
        </Field>
        <Field label={setupFrame === 0 ? "Opening receiver" : "Receiver at selected frame"}>
          <select
            className={inputClass}
            value={receiving?.participant_id ?? ""}
            onChange={(event) => setReceiver(event.target.value)}
          >
            {opponents.map((person, index) => (
              <option value={person.participant_id} key={person.participant_id}>
                {person.name || `Opponent ${index + 1}`}
              </option>
            ))}
          </select>
        </Field>
        <button
          className="rally-action"
          type="submit"
          disabled={
            !teamsReady ||
            session.status !== "analysed" ||
            query.data?.analysis_revision !== revision ||
            mutation.isPending
          }
        >
          {setupFrame === 0 ? "Set opening service order at 0–0" : "Set service order at recorded score"}
        </button>
      </form>
      <ErrorNote error={query.error || mutation.error} />
    </section>
  );
}
