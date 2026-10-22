import { Card, Page } from "./ui";

const topics = [
  [
    "Counted rallies and scores",
    "Only official, non-retracted rally events contribute to the score and match statistics. Warm-up and replay rallies stay available for review. Corrections refold the canonical events and update the analytics.",
  ],
  [
    "Shot naming",
    "Shot types are inferred by rules from motion and contact evidence. They are a preview, not manually labelled accuracy. Select a shot or rally to check its source frames.",
  ],
  [
    "Court maps",
    "Presence uses calibrated player positions. Origin uses the hitter’s position. The map labelled shot destination uses where the receiver met the shuttle; it does not measure shuttle landing points. An empty map means missing evidence, rather than zero movement.",
  ],
  [
    "Distance and active play",
    "Distance comes from calibrated tracking and can include tracking jitter. Active play is the duration of counted rally events. Missing calibrated tracks make distance unavailable.",
  ],
  [
    "Moments",
    "The moment ranker chooses actual rallies and supplies category and reason contributions. Its internal excitement score is not a rating of a player. Opening a moment seeks the stored video to its start frame.",
  ],
  [
    "People, progress and doubles",
    "P1 and P2 identify tracks within one recording. People history groups names explicitly entered for those tracks. Four-player identity, pair chemistry and persistent partner relationships require additional pipeline evidence and are marked unavailable.",
  ],
  [
    "Video and processing",
    "Video playback uses the server’s HLS or progressive video. Frame links use the recording’s constant-frame-rate media timebase. Analytics from unfinished processing are identified as partial; completed totals use completed analyses.",
  ],
];
export function HelpPage() {
  return (
    <Page
      title="Understanding your analytics"
      lead="What each metric measures, and where it gets less certain."
    >
      <div className="rally-stack">
        {topics.map(([title, body]) => (
          <Card key={title} title={title}>
            <p className="rally-muted">{body}</p>
          </Card>
        ))}
      </div>
    </Page>
  );
}
