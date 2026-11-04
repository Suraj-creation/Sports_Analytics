import { exampleCollection } from "./badminton/example";
import { recordingCollection } from "./badminton/observed";
import { CourtArtwork } from "./badminton/CourtArtwork";
import type { HighlightProvider } from "./types";

export const DEFAULT_EXAMPLE_SPORT = "badminton";

/** Explicit UI registration. Additional domains provide their own presentation adapter. */
export const highlightProviders: readonly HighlightProvider[] = [
  {
    sport: "badminton",
    example: exampleCollection,
    fromRecording: recordingCollection,
    renderDiagram: (variant, format) => createElement(CourtArtwork, { variant, format }),
  },
];

export function highlightProvider(sport: string): HighlightProvider | undefined {
  return highlightProviders.find((provider) => provider.sport === sport);
}

import { createElement } from "react";
