import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { ParticipantRoster } from "./ParticipantRoster";

it("creates four distinct participants only after an explicit doubles choice", async () => {
  const session = { ...SESSION, roster: null };
  const save = vi.spyOn(api, "updateRoster").mockImplementation(async (_id, roster) => ({ ...session, roster }));
  const client = new QueryClient({ defaultOptions: { mutations: { retry: false } } });
  render(<QueryClientProvider client={client}><ParticipantRoster session={session} /></QueryClientProvider>);
  fireEvent.click(screen.getByRole("button", { name: /set up participants/i }));
  fireEvent.change(screen.getByLabelText(/match format/i), { target: { value: "doubles" } });
  fireEvent.change(screen.getByLabelText("Player 1 name"), { target: { value: "Alice" } });
  fireEvent.click(screen.getByRole("button", { name: /save participants/i }));
  await waitFor(() => expect(save).toHaveBeenCalledTimes(1));
  const draft = save.mock.calls[0]![1];
  expect(draft.match_format).toBe("doubles");
  expect(draft.participants).toHaveLength(4);
  expect(new Set(draft.participants.map((p) => p.participant_id)).size).toBe(4);
  expect(draft.participants[0]!.name).toBe("Alice");
  expect(draft.participants.every((p) => p.team_id === null)).toBe(true);
  expect(draft.teams.every((team) => team.score_slot === null)).toBe(true);
  expect(await screen.findByText(/does not link people to video tracks/i)).toBeVisible();
  save.mockRestore();
});

it("allows a saved singles roster to change to doubles while retaining names and teams", () => {
  const roster = { match_format: "singles" as const, teams: [{ team_id: "T1", score_slot: null }, { team_id: "T2", score_slot: null }], participants: [
    { participant_id: "alice", name: "Alice", team_id: "T1" }, { participant_id: "bob", name: "Bob", team_id: "T2" },
  ] };
  const client = new QueryClient();
  render(<QueryClientProvider client={client}><ParticipantRoster session={{ ...SESSION, roster }} /></QueryClientProvider>);
  fireEvent.click(screen.getByRole("button", { name: /edit participants/i }));
  expect(screen.getByLabelText("Match format")).toBeEnabled();
  fireEvent.change(screen.getByLabelText("Match format"), { target: { value: "doubles" } });
  expect(screen.getByLabelText("Player 1 name")).toHaveValue("Alice");
  expect(screen.getByLabelText("Player 1 team")).toHaveValue("T1");
  expect(screen.getByLabelText("Player 4 name")).toBeVisible();
});
it("refreshes the saved roster without replacing an unsaved draft during live updates", () => {
  const client = new QueryClient();
  const roster = { match_format: "singles" as const, teams: [{ team_id: "T1", score_slot: null }, { team_id: "T2", score_slot: null }], participants: [
    { participant_id: "alice", name: "Alice", team_id: "T1" }, { participant_id: "bob", name: "Bob", team_id: "T2" },
  ] };
  const view = render(<QueryClientProvider client={client}><ParticipantRoster session={{ ...SESSION, roster: null }} /></QueryClientProvider>);
  view.rerender(<QueryClientProvider client={client}><ParticipantRoster session={{ ...SESSION, roster }} /></QueryClientProvider>);
  expect(screen.getByText(/Alice · Team A/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /edit participants/i }));
  fireEvent.change(screen.getByLabelText("Player 1 name"), { target: { value: "Alicia" } });
  view.rerender(<QueryClientProvider client={client}><ParticipantRoster session={{ ...SESSION, frontier_frame: 7000, roster: structuredClone(roster) }} /></QueryClientProvider>);
  expect(screen.getByLabelText("Player 1 name")).toHaveValue("Alicia");
});
