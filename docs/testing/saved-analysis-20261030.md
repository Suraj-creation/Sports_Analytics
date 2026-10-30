# Saved video analysis — 30 October 2026

## Findings
- Media is content addressed under data/media/<sha256>/; per-session events, state snapshots,
  calibration and track chunks live under data/sessions/<session_id>/.
- Import endpoints always created a fresh session even for identical input. YouTube ingestion
  replaced its original URL with a local source path without retaining its video ID.
- Engine startup left interrupted jobs marked analysing. Viewing them did not itself trigger
  inference, but their stale progress looked like another analysis.
- Completed sessions without events were mistaken for new sessions when commands reattached.
- Explicitly retrying an eventless partial result did not back up its tracking data.

## Changes
- Reimports reuse an existing source/profile/format analysis and return HTTP 200; new imports
  return HTTP 201. Titles, player names, calibration and existing events are not overwritten.
- YouTube IDs are retained in session metadata. Equivalent watch/short URLs resolve to one ID.
- Legacy YouTube imports can require one identification download: an exact downloaded-byte hash
  matches saved work, then redirects to its original session before probing, transcoding,
  calibration or inference. The recovered video ID is retained for future imports.
  Different YouTube encodings cannot be identified from the old stored metadata safely.
- Alias import rows are excluded from the library and source lookup.
- Startup marks orphaned jobs interrupted while preserving all partial data. It does not
  automatically replay a GPU pipeline. Retry remains an explicit action.
- Completed empty detections are valid results; interrupted partial work is backed up before retry.
- Saved court points take precedence over new proposals on an applicable reference frame.

## Verification
Red-before-green regression tests cover duplicate uploads, normalized YouTube URLs after URI
replacement, unchanged calibration metadata, read-only REST/WebSocket opens, separate profiles,
completed empty detections, stale startup status, legacy hash redirection before any media/model
work, and backup of partial eventless tracks.

- Targeted source/lifecycle/storage verification: 48 passed.
- API, engine and agent suite (excluding GPU, slow and network markers): 178 passed.
- Frontend: 88 tests, typecheck and production build passed.
- Independent backend review found no material blockers.

Existing untracked apps/web/dist.old/ and client-website/ were preserved.


## Final live verification
The affected low-angle match completed all 38,417 frames (the old run had stopped at
16,080). Its prior event database and tracks remain in the automatic session backup.
The saved calibration now follows the actual floor instead of roof/wall beams.

The backend was restarted after completion. Two authorized session reads and an event
read preserved the exact completion timestamp and event sequence 3244; no inference
models loaded and both GPUs remained idle. Public Cloudflare health returned HTTP 200.

WebSocket generation regressions additionally cover fresh generation IDs after reset,
replaying all new events even when a prior sequence cursor is lower than the new log,
and seeking on an open socket after its old SQLite store has been replaced. The live
frontend clears obsolete events/tracks/scores and reconnects read-only on generation
changes. Opening a match never sends an analysis command.

Final validation: 178 API/engine/agent tests, 578 badminton tests, and 88 frontend tests
passed. Typecheck, production build, changed-file lint and whitespace checks passed.

See feedback-20261030-reanalysis.json for folded live event counts. The new complete
run contains 133 shot candidates, of which 42 have rule-based types and 91 remain
unknown. Unsupported labels and rally winners remain unknown; this is not a claim of
labelled classification accuracy or complete automated scoring.
