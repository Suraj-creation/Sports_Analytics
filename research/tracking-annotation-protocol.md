# Sampled four-person tracking validation

Use `python -m research.tracking_benchmark --help`. This read-only evaluator
measures visible tracking boxes and anonymous identity consistency. It does not
measure racket contact, shot family, named-person recognition or person-detector
accuracy. A detector-run flag applies to the whole frame, not each returned box.

Bind annotations to the source file and canonical proxy SHA-256, session ID,
exact FPS numerator/denominator, dimensions, and a half-open frame window.
Declare sorted `sampled_frames` explicitly. Every declared sample needs an
exhaustive list of visible player boxes; an empty list is a reviewed negative
sample. Missing prediction frames count as misses. Sparse samples cannot
validate unseen frames between them.

Each visible person has an in-image `bbox: [x1,y1,x2,y2]` and a stable
`person_id`. Establish anonymous names once, then follow appearance and visible
trajectory. Do not rename people by current left/right/front/rear position.
Use `person_id: null` when identity cannot be supported; retain its visible box
for localization. Fully invisible/out-of-view people receive no visible box.
Review the original frame if a crop truncates a body; do not invent hidden bounds.

Use `status: draft`, `split: diagnostic`, and `review.human_verified: false`
for AI labels. The evaluator requires `--allow-draft`, and all resulting accuracy
eligibility flags remain false. Human review must inspect the actual source
frames independently of predictions. Merely changing a JSON flag is not review.
Held-out recordings must be separate from recordings used to choose features,
thresholds or model settings. Development/draft results cannot establish a
general improvement.

For a stored snapshot, pass `--data-dir` and `--session`. Extraction verifies
actual source/proxy bytes and media metadata, hashes the event ledger and latest
selected player Parquet chunks, and detects concurrent changes. Identity keys
include the analysis generation and live birth-observation ID. Numeric track IDs
are reusable and cannot establish identity. Invalid/stale birth references,
exits, resets and track reuse leave identity unresolved. Extraction never writes
reviews or alters sessions. The caller should use an immutable backup.

Localization uses one-to-one IoU matching at the reported threshold, maximizing
valid match count before IoU. Report precision, recall and support. Identity
overlap counts use all IoU-compatible identity pairs and one global assignment
over the complete sampled window. New episodes and ID swaps cannot be repaired
by rebinding each sample. `idf1` is computed from global IDTP, IDFP and IDFN;
predictions compatible only with unknown-identity truth are excluded from identity
support. Unresolved identities on known people remain errors. The assignment
does not identify names and cannot disambiguate indistinguishable overlapping
boxes. Sampled switches are counted only where localization is unique; ambiguous
assignment support is reported separately. Sparse switches/fragments are lower
bounds on errors between samples.

Also report four-visible-player sample count, four localized boxes, four distinct
identity keys, missing prediction frames, per-person distinct-key support,
ambiguous truth and all provenance hashes. Four distinct keys in a frame do not
establish stable four-person identities across an interval.

`research.participant_benchmark` remains a separate conditional hitter test:
its external episode-to-person bindings do not validate automatic continuity.
Its new event precision/recall and joint contact/family/hitter scores penalize
spurious, wrong, unresolved and missed events. Shot-family scores require
exhaustive independent per-shot labels; partial motion drafts cannot supply them.
