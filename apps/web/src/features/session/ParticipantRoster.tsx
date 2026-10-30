import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { ErrorNote } from "@/components/ui";
import { api } from "@/lib/api";
import type { RosterParticipant, Session, SessionRoster } from "@/lib/types";
import { useSession } from "@/stores/session";

function blankParticipant(): RosterParticipant {
  return { participant_id: `person-${crypto.randomUUID()}`, name: null, team_id: null };
}

export function ParticipantRoster({ session }: { session: Session }) {
  const queryClient = useQueryClient();
  const [saved, setSaved] = useState<SessionRoster | null>(session.roster ?? null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<SessionRoster | null>(session.roster ?? null);
  // Socket/query refreshes update saved data without replacing a form being edited.
  useEffect(() => setSaved(session.roster ?? null), [session.roster]);
  const save = useMutation({
    mutationFn: (roster: SessionRoster) => api.updateRoster(session.session_id, roster),
    onSuccess: (updated) => {
      setSaved(updated.roster ?? null);
      setDraft(updated.roster ?? null);
      setEditing(false);
      useSession.setState((state) =>
        state.session?.session_id === updated.session_id ? { session: { ...state.session, roster: updated.roster } } : {},
      );
      void queryClient.invalidateQueries({ queryKey: ["session", session.session_id] });
      void queryClient.invalidateQueries({ queryKey: ["individual-analytics", session.session_id] });
      void queryClient.invalidateQueries({ queryKey: ["estimated-individual-analytics", session.session_id] });
    },
  });
  const chooseFormat = (value: string) => {
    if (value !== "singles" && value !== "doubles") {
      setDraft(null);
      return;
    }
    const count = value === "doubles" ? 4 : 2;
    const previous = draft?.participants ?? [];
    const participants = Array.from({ length: count }, (_, index) => previous[index] ?? blankParticipant());
    setDraft({ match_format: value, teams: draft?.teams ?? [{ team_id: "T1", score_slot: null }, { team_id: "T2", score_slot: null }], participants });
  };
  const changeParticipant = (index: number, change: Partial<RosterParticipant>) => {
    setDraft((current) => current ? {
      ...current,
      participants: current.participants.map((participant, i) => i === index ? { ...participant, ...change } : participant),
    } : null);
  };
  return (
    <section className="analysis-panel mt-5" aria-labelledby="participants-heading">
      <h2 id="participants-heading" className="font-medium">Participants</h2>
      <p className="analysis-panel-hint mt-2">
        Names and teams are supplied by you; entering them does not link people to video tracks or verify shot events. Format applies when analysis starts; an existing recording needs a backed-up reanalysis to apply a format change. Doubles scoring still requires review.
      </p>
      {!editing && saved && (
        <ul className="mt-3 space-y-1 text-sm">
          {saved.participants.map((participant, index) => (
            <li key={participant.participant_id}>
              {participant.name?.trim() || `Player ${index + 1}`} · {participant.team_id ? `Team ${participant.team_id === "T1" ? "A" : participant.team_id === "T2" ? "B" : participant.team_id}` : "Team unassigned"}
            </li>
          ))}
        </ul>
      )}
      {!editing && (
        <button className="rally-action mt-4" type="button" onClick={() => { save.reset(); setDraft(saved); setEditing(true); }}>
          {saved ? "Edit participants" : "Set up participants"}
        </button>
      )}
      {editing && (
        <form className="mt-4 space-y-4" onSubmit={(event) => {
          event.preventDefault();
          if (draft) save.mutate({ ...draft, participants: draft.participants.map((person) => ({ ...person, name: person.name?.trim() || null })) });
        }}>
          <label className="block text-sm">
            Match format
            <select className="mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3" value={draft?.match_format ?? ""} disabled={save.isPending} onChange={(event) => chooseFormat(event.target.value)}>
              <option value="">Choose a format</option>
              <option value="singles">Singles</option>
              <option value="doubles">Doubles</option>
            </select>
          </label>
          {draft?.participants.map((person, index) => (
            <div key={person.participant_id} className="grid gap-3 sm:grid-cols-2">
              <label className="block text-sm">
                Player {index + 1} name
                <input className="mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3" maxLength={80} value={person.name ?? ""} onChange={(event) => changeParticipant(index, { name: event.target.value })} />
              </label>
              <label className="block text-sm">
                Player {index + 1} team
                <select className="mt-2 block min-h-11 w-full rounded-lg border border-seam bg-stand px-3" value={person.team_id ?? ""} onChange={(event) => changeParticipant(index, { team_id: event.target.value || null })}>
                  <option value="">Unassigned</option>
                  {draft.teams.map((team) => <option key={team.team_id} value={team.team_id}>{team.team_id === "T1" ? "Team A" : team.team_id === "T2" ? "Team B" : team.team_id}</option>)}
                </select>
              </label>
            </div>
          ))}
          {save.error && <ErrorNote error={save.error} />}
          <div className="flex flex-wrap gap-2">
            <button className="rally-action" type="submit" disabled={!draft || save.isPending}>Save participants</button>
            <button className="rally-action" type="button" onClick={() => { setDraft(saved); setEditing(false); }}>Cancel</button>
          </div>
        </form>
      )}
    </section>
  );
}
