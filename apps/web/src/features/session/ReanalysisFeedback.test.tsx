import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReanalysisFeedback } from "./ReanalysisFeedback";

describe("reanalysis feedback", () => {
  it("shows a preserved-results failure from the live status even after request acceptance", () => {
    render(
      <ReanalysisFeedback
        accepted
        liveDetail="Reanalysis could not start; existing results were preserved. Check server logs."
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("existing results were preserved");
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
  });
  it("shows a persisted startup failure without requiring a failed session status", () => {
    render(
      <ReanalysisFeedback
        accepted={false}
        sessionDetail="Reanalysis could not start; existing results were preserved. Check server logs."
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Reanalysis could not start");
  });
  it("acknowledges acceptance without claiming that analysis completed", () => {
    render(<ReanalysisFeedback accepted />);
    expect(screen.getByRole("status")).toHaveTextContent("Processing status will update when it starts");
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });
});
