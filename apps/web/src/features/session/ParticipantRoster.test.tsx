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
