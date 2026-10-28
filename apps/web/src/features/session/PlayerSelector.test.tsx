import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { SESSION } from "@/test/fixtures";
import { PlayerSelector } from "./PlayerSelector";

it("warns about legacy slots without assuming doubles and retains selection", () => {
  const onSelect = vi.fn();
  render(<PlayerSelector session={SESSION} selected="P1" onSelect={onSelect} />);
  expect(screen.getByText(/legacy two-slot estimates/i)).toBeVisible();
  expect(screen.getByText(/in doubles, they cannot identify four individual players/i)).toBeVisible();
  expect(screen.getByText(/review the video/i)).toBeVisible();
  expect(screen.getByRole("button", { name: /show Axelsen numbers/i })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  fireEvent.click(screen.getByRole("button", { name: /show Momota numbers/i }));
  expect(onSelect).toHaveBeenCalledWith("P2");
});
