import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, expect, it, vi } from "vitest";
import * as apiModule from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { LibraryPage } from "./LibraryPage";

vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => vi.fn(),
  Link: ({ children }: { children: ReactNode }) => <span>{children}</span>,
}));

const clients: QueryClient[] = [];
afterEach(() => {
  cleanup();
  for (const client of clients) client.clear();
  clients.length = 0;
  vi.restoreAllMocks();
});

function showLibrary() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: 0 } } });
  clients.push(client);
  render(
    <QueryClientProvider client={client}>
      <LibraryPage />
    </QueryClientProvider>,
  );
}

it("sends the selected doubles format when uploading", async () => {
  vi.spyOn(apiModule.api, "sessions").mockResolvedValue([]);
  vi.spyOn(apiModule.api, "system").mockResolvedValue({
    youtube_ingest: false,
  } as Awaited<ReturnType<typeof apiModule.api.system>>);
  const upload = vi.spyOn(apiModule, "uploadVideo").mockReturnValue({
    promise: Promise.resolve(SESSION),
    abort: vi.fn(),
  });
  showLibrary();
  const uploadForm = screen.getByRole("form", { name: "Upload a video" });
  fireEvent.change(within(uploadForm).getByLabelText("Video file"), {
    target: { files: [new File(["video"], "rally.mp4", { type: "video/mp4" })] },
  });
  fireEvent.change(within(uploadForm).getByLabelText(/Match format/), { target: { value: "doubles" } });
  expect(within(uploadForm).getByText("Team 1 label")).toBeInTheDocument();
  fireEvent.click(within(uploadForm).getByRole("button", { name: "Analyse video" }));
  await waitFor(() => expect(upload).toHaveBeenCalledTimes(1));
  expect(upload.mock.calls[0]?.[0].get("match_format")).toBe("doubles");
});

it("sends the selected doubles format when importing a YouTube video", async () => {
  vi.spyOn(apiModule.api, "sessions").mockResolvedValue([]);
  vi.spyOn(apiModule.api, "system").mockResolvedValue({
    youtube_ingest: true,
  } as Awaited<ReturnType<typeof apiModule.api.system>>);
  const create = vi.spyOn(apiModule.api, "youtube").mockResolvedValue(SESSION);
  showLibrary();
  const importForm = screen.getByRole("form", { name: "Import from YouTube" });
  fireEvent.change(within(importForm).getByLabelText("Video link"), {
    target: { value: "https://www.youtube.com/watch?v=abcdefghijk" },
  });
  fireEvent.change(within(importForm).getByLabelText(/Match format/), { target: { value: "doubles" } });
  fireEvent.click(within(importForm).getByRole("checkbox"));
  const submit = within(importForm).getByRole("button", { name: "Import and analyse" });
  await waitFor(() => expect(submit).toBeEnabled());
  fireEvent.click(submit);
  await waitFor(() =>
    expect(create).toHaveBeenCalledWith(expect.objectContaining({ match_format: "doubles" })),
  );
});
