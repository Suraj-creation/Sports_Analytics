import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { EventLog } from "@/lib/events";
import { useSession } from "@/stores/session";
import { ev, SESSION } from "@/test/fixtures";
import { Timeline } from "./Timeline";
vi.mock("@/features/library/Thumb", () => ({ useSprite: () => ({ data: null }), spriteStyle: () => null }));
const original = useSession.getState();
afterEach(() => { cleanup(); useSession.setState(original); vi.restoreAllMocks(); });
function show(events = new EventLog()) {
  const session = { ...SESSION, status: "analysed" as const, frontier_frame: 8999 };
  useSession.setState({ session, events, eventsVersion: events.version });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(<QueryClientProvider client={client}><Timeline session={session} /></QueryClientProvider>);
}
it("explains an analysed recording with no shots without claiming analysis is pending", () => {
  show();
  expect(screen.getByText("No shot events were detected in this recording.")).toBeVisible();
  expect(screen.queryByText(/not analysed yet/i)).not.toBeInTheDocument();
  expect(screen.getByText("Full match")).toBeVisible();
});
it("shows unassigned unknown shots and refreshes classification while paused", () => {
  const fillRect = vi.fn();
  const context = new Proxy({ fillRect }, {
    get(target, key) { return key in target ? target[key as keyof typeof target] : () => {}; },
  });
  vi.spyOn(HTMLCanvasElement.prototype, "getContext").mockReturnValue(context as unknown as CanvasRenderingContext2D);
  const events = new EventLog();
  events.apply([ev("stroke", 30, { payload: { stroke: "unknown" } })]);
  show(events);
  expect(screen.getByText("1 shot event · classification unavailable")).toBeVisible();
  expect(screen.getByRole("img", { name: "Shot activity near the playhead" })).toHaveStyle({ height: "96px" });
  expect(screen.getByText(/unassigned lane/i)).toBeVisible();
  expect(fillRect).toHaveBeenCalledWith(expect.any(Number), 65, 2, 10);
  act(() => {
    events.apply([ev("stroke", 60, { actors: { player_id: "P1", track_id: null, opponent_id: null }, payload: { stroke: "smash" } })]);
    useSession.setState({ eventsVersion: events.version });
  });
  expect(screen.getByText("1 of 2 shot events classified")).toBeVisible();
  expect(fillRect).toHaveBeenCalledWith(expect.any(Number), 14, 4, 16);
});
