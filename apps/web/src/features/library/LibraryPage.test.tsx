import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import type { ReactNode } from "react";
import { expect, it, vi } from "vitest";
import * as apiModule from "@/lib/api";
import { SESSION } from "@/test/fixtures";
import { LibraryPage } from "./LibraryPage";

vi.mock("@tanstack/react-router", () => ({useNavigate: () => vi.fn(), Link: ({children}: {children: ReactNode}) => <span>{children}</span>}));

it("sends the selected doubles format when uploading", async () => {
  vi.spyOn(apiModule.api, "sessions").mockResolvedValue([]);
  vi.spyOn(apiModule.api, "system").mockResolvedValue({youtube_ingest: false} as Awaited<ReturnType<typeof apiModule.api.system>>);
  const upload = vi.spyOn(apiModule, "uploadVideo").mockReturnValue({promise: Promise.resolve(SESSION), abort: vi.fn()});
  const client = new QueryClient({defaultOptions: {queries: {retry: false}}});
  const {container} = render(<QueryClientProvider client={client}><LibraryPage /></QueryClientProvider>);
  const fileInput = container.querySelector('input[type="file"]') as HTMLInputElement;
  fireEvent.change(fileInput, {target: {files: [new File(["video"], "rally.mp4", {type: "video/mp4"})]}});
  const uploadCard = screen.getByText("Analyse a match").closest(".panel") as HTMLElement;
  fireEvent.change(within(uploadCard).getByLabelText(/Match format/), {target: {value: "doubles"}});
  expect(within(uploadCard).getByText("Team 1 label")).toBeInTheDocument();
  fireEvent.click(within(uploadCard).getByRole("button", {name: "Analyse video"}));
  await waitFor(() => expect(upload).toHaveBeenCalled());
  expect(upload.mock.calls[0]![0].get("match_format")).toBe("doubles");
  vi.restoreAllMocks();
});

it("sends the selected doubles format when importing a YouTube video", async () => {
  vi.spyOn(apiModule.api, "sessions").mockResolvedValue([]);
  vi.spyOn(apiModule.api, "system").mockResolvedValue({youtube_ingest: true} as Awaited<ReturnType<typeof apiModule.api.system>>);
  const create = vi.spyOn(apiModule.api, "youtube").mockResolvedValue(SESSION);
  const client = new QueryClient({defaultOptions: {queries: {retry: false}}});
  render(<QueryClientProvider client={client}><LibraryPage /></QueryClientProvider>);
  const importForm = screen.getByText("Import from YouTube").closest("form") as HTMLFormElement;
  await within(importForm).findByLabelText("Video link");
  fireEvent.change(within(importForm).getByLabelText("Video link"), {target: {value: "https://www.youtube.com/watch?v=abcdefghijk"}});
  fireEvent.change(within(importForm).getByLabelText(/Match format/), {target: {value: "doubles"}});
  fireEvent.click(within(importForm).getByRole("checkbox"));
  fireEvent.click(within(importForm).getByRole("button", {name: "Import and analyse"}));
  await waitFor(() => expect(create).toHaveBeenCalledWith(expect.objectContaining({match_format: "doubles"})));
  vi.restoreAllMocks();
});
