import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { SESSION } from "@/test/fixtures";
import { DoublesService } from "./DoublesService";

it("records an explicit opening pair and shows the canonical named server and receiver", async () => {
  const writes: unknown[] = [];
  vi.spyOn(globalThis, "fetch").mockImplementation(async (_input, init) => {
    if (init?.method === "POST") writes.push(JSON.parse(String(init.body)));
    return new Response(
      JSON.stringify({
        status: "known",
        server_participant_id: "person-0",
        receiver_participant_id: "person-2",
        service_court: "right",
        analysis_revision: 2,
      }),
      { status: 200 },
    );
  });
  const roster = {
    match_format: "doubles" as const,
    teams: [
      { team_id: "T1", score_slot: "P1" as const },
      { team_id: "T2", score_slot: "P2" as const },
    ],
    participants: ["Alice", "Bob", "Cara", "Dev"].map((name, index) => ({
      participant_id: `person-${index}`,
      name,
      team_id: index < 2 ? "T1" : "T2",
    })),
  };
  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <DoublesService session={{ ...SESSION, status: "analysed", meta: { analysis_revision: 2 }, roster }} />
    </QueryClientProvider>,
  );
  expect(await screen.findByText(/Alice serves to Cara/)).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Opening server"), { target: { value: "person-0" } });
  fireEvent.change(screen.getByLabelText("Opening receiver"), { target: { value: "person-2" } });
  fireEvent.click(screen.getByRole("button", { name: "Set opening service order at 0–0" }));
  await waitFor(() =>
    expect(writes).toEqual([
      {
        server_participant_id: "person-0",
        receiver_participant_id: "person-2",
        frame: 0,
        analysis_revision: 2,
      },
    ]),
  );
  fireEvent.change(screen.getByLabelText("Service setup frame"), { target: { value: "42" } });
  fireEvent.click(screen.getByRole("button", { name: "Set service order at recorded score" }));
  await waitFor(() => expect(writes).toHaveLength(2));
  expect(writes[1]).toMatchObject({ frame: 42, analysis_revision: 2 });
  vi.restoreAllMocks();
});
