import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { SESSION } from "@/test/fixtures";
import { RecordingQuality } from "./RecordingQuality";

it("reports actual failures and availability separately from named identities", () => {
  render(
    <RecordingQuality
      session={{
        ...SESSION,
        meta: {
          degraded: [{ stage: "player_identity", reason: "Pinned appearance checkpoint is missing" }],
          capabilities: {
            player_identity: { status: "unavailable", reason: "No checkpoint" },
            pose: { status: "loaded", reason: "Configured provider initialized" },
            named_identity: { status: "review_required" },
          },
        },
      }}
    />,
  );
  expect(screen.getByText(/Pinned appearance checkpoint is missing/)).toBeVisible();
  expect(screen.getByText("Appearance matching · unavailable")).toBeVisible();
  expect(screen.getByText("Body pose · loaded")).toBeVisible();
  expect(screen.getByText(/Named players require reviewed associations/)).toBeVisible();
  expect(screen.queryByText("Two court-side identities")).not.toBeInTheDocument();
});
it("preserves missing historical runtime metadata as unknown", () => {
  render(<RecordingQuality session={{ ...SESSION, meta: {} }} />);
  expect(screen.getByText("Component availability metadata was not recorded.")).toBeVisible();
  expect(screen.getByText(/Degradation metadata was not recorded/)).toBeVisible();
});
it("does not turn malformed saved diagnostic entries into a successful capability", () => {
  render(
    <RecordingQuality session={{ ...SESSION, meta: { degraded: [null], capabilities: { pose: null } } }} />,
  );
  expect(screen.getByText("A saved limitation entry could not be read.")).toBeVisible();
  expect(screen.getByText("Body pose · unknown")).toBeVisible();
});
