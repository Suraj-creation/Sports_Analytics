import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, expect, it, vi } from "vitest";
import * as apiModule from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { LibraryPage } from "./LibraryPage";

const navigate = vi.hoisted(() => vi.fn());
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => navigate,
  Link: ({ children }: { children: ReactNode }) => <span>{children}</span>,
}));

const clients: QueryClient[] = [];
afterEach(() => {
  cleanup();
  for (const client of clients) client.clear();
  clients.length = 0;
  vi.restoreAllMocks();
  navigate.mockReset();
});

function beginUpload() {
  vi.spyOn(apiModule.api, "sessions").mockResolvedValue([]);
  vi.spyOn(apiModule.api, "system").mockResolvedValue({ youtube_ingest: false });
  let resolve!: (session: typeof SESSION) => void;
  const promise = new Promise<typeof SESSION>((done) => {
    resolve = done;
  });
  const abort = vi.fn();
  vi.spyOn(apiModule, "uploadVideo").mockReturnValue({ promise, abort });
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } });
  clients.push(client);
  const view = render(
    <QueryClientProvider client={client}>
      <LibraryPage />
    </QueryClientProvider>,
  );
  const form = screen.getByRole("form", { name: "Upload a video" });
  fireEvent.change(within(form).getByLabelText("Video file"), {
    target: { files: [new File(["fixture"], "match.mp4", { type: "video/mp4" })] },
  });
  fireEvent.click(within(form).getByRole("button", { name: "Analyse video" }));
  return { ...view, abort, resolve };
}

it("cancels the in-flight upload when its recording form is unmounted", () => {
  const upload = beginUpload();
  upload.unmount();
  expect(upload.abort).toHaveBeenCalledTimes(1);
});

it("does not navigate back to a recording after the user has left its upload page", async () => {
  const upload = beginUpload();
  upload.unmount();
  await act(async () => upload.resolve(SESSION));
  expect(navigate).not.toHaveBeenCalled();
});

it("opens the completed recording while its upload page remains active", async () => {
  const upload = beginUpload();
  await act(async () => upload.resolve(SESSION));
  await waitFor(() =>
    expect(navigate).toHaveBeenCalledWith({ to: "/sessions/$sessionId", params: { sessionId: SESSION.session_id } }),
  );
});
