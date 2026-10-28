# Session reanalysis and video diagnostic — 2026-10-28

All five original sessions were backed up before reanalysis and then processed sequentially using release `83e9da5`. Each newly generated per-session backup has an SQLite `integrity_check` result of `ok`. The independent pre-reanalysis snapshot is `/home/administrator/Desktop/sport-analytics/backups/pre-reanalysis-20261028T064619Z`; the earlier complete media and checkout snapshot is `/home/administrator/Desktop/sport-analytics/backups/task2-20261028T060514Z`. The automated run record, exact per-session backup paths, and aggregate results are in `/home/administrator/Desktop/sport-analytics/evaluation-task3-20261028/`.

| Session | Frames analysed / media | Stroke candidates | Unknown classifications | Old / new point events | Format |
| --- | ---: | ---: | ---: | ---: | --- |
| SampleRally | 480 / 480 | 2 | 2 | 0 / 0 | singles spot-check |
| Singles broadcast | 12,075 / 12,075 | 235 | 226 | 24 / 0 | singles |
| Doubles broadcast | 12,148 / 12,148 | 298 | 193 | 28 / 1 | doubles |
| A02 amateur | 22,802 / 22,802 | 513 | 432 | 50 / 0 | doubles spot-check |
| Real Video | 4,462 / 4,462 | 0 | 0 | 0 / 0 | doubles spot-check |

The three doubles rosters contain four unnamed, unassigned participants each, not verified identities or team assignments. The two human-verified doubles-broadcast edits (match-start and P1 rally-end at frame 326) survived reanalysis. Prior automatic point events were not all reproduced: the new output requires evidence before declaring a rally official, and the former point records remain available in the backups. These changes are significant and should not be interpreted as validated scoring improvements.

The doubles broadcast produced 287 provisional shot-to-episode links across 87 separate anonymous shot-bearing episodes. A02 produced 489 such links across 43 episodes. Episodes can fragment and switch; they are not four persistent people. A frame-level detector-run flag does not guarantee a particular person was matched. The high unknown counts show that usable shot classification remains incomplete.

Real Video produced no rallies or strokes in either the old or new analysis. Its current perception cache contains 1,111 lost frames and 404 reacquiring frames among 4,462; the active-play state covered only seven frames. The selected fixed court is frequently rejected and reacquired, interrupting activity evidence. The exact cause of the verification failures remains to be isolated. Do not loosen court-isolation checks without evaluating neighboring-court leakage and genuine labelled shuttle and event evidence.

The AI-only source-bound drafts in `annotations/` include short windows from the broadcast, Test7, A02 and Real Video. They are non-exhaustive, not human-verified, and leave contact, shot family and durable identity unknown where obscured. In A02 the possible 31.75–32.4 s racket motion had no stroke candidate in that window; because contact is unconfirmed, this is not a measured false negative. Neither these drafts nor rally-level CSVs provide the independent, exhaustive contact/family/person labels required to calculate precision, recall, classification F1 or four-player identity accuracy. See `provenance-gpu-comparison-20261028.md` for the matched 250-frame GPU diagnostic.
