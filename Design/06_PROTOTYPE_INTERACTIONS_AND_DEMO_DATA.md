# 06 --- Clickable Prototype Behavior and Demo Data

## 1. Prototype objective

The prototype must demonstrate a coherent end-to-end experience. It
should be possible to start as a new user, configure preferences, open a
sample session, view a recap, inspect a clip, explore analytics, compare
progress, change privacy preferences, and report an incorrect result.

Use deterministic demo fixtures so screenshots, tests, and user research
sessions are repeatable.

## 2. Prototype modes

### Demo mode

-   Uses fictional, clearly labelled data.
-   Does not upload actual footage.
-   Does not claim real analysis or real sharing.
-   Resettable from Settings → Data.
-   Demo actions show honest feedback such as "Demo action completed".

### Connected mode

-   Available only when real backend endpoints are integrated.
-   Clearly distinguish real session data from demo data.
-   Respect the backend's consent and processing states.

## 3. Required interactive behaviors

-   Welcome CTA starts onboarding.
-   Explore demo opens a populated sample session.
-   Goal cards support multi-select.
-   Experience mode cards update selection.
-   Continue/skip moves through onboarding.
-   Consent toggles remain separate.
-   Finish onboarding updates the Home page modules.
-   Session cards navigate to session detail.
-   Processing demo advances through stage states only when user
    initiates or when a documented simulation runs.
-   Recap hero clip opens clip detail/player.
-   Highlight cards can be favorited.
-   Share opens a consent-aware share dialog; demo mode never creates a
    public URL.
-   Analytics filters update visible cards/charts and show active filter
    chips.
-   Chart points/rows open the related rally or clip where supported.
-   Metric info opens a definition popover/drawer.
-   Compare-session controls select valid comparable sessions.
-   Feedback action records simulated feedback locally in the prototype
    state.
-   Privacy controls update the simulated consent ledger.
-   Destructive actions require confirmation.
-   Mode switch updates information density, not underlying data.
-   All interactive controls need visible response; no decorative
    buttons that do nothing.

## 4. Suggested demo scenario

Fictional player: "Alex"\
Experience mode: Relax + Explore\
Recent sessions: - Session A: Casual doubles, completed, 9 verified
rallies, 3 approved highlights. - Session B: Singles, completed, 14
verified rallies, 4 highlights. - Session C: Doubles, partial
processing, rally results ready but movement analysis pending.

Use believable but explicitly illustrative values. Add a persistent
"Sample data" label on all relevant screens. Avoid presenting these
values as actual measurements from a real person.

Example session recap: - Best moment: "Longest verified rally in this
sample session --- 13 shots." - Personal record: "New sample-data
personal best." - Shot repertoire: "5 shot categories observed." -
Caveat: "Movement view is illustrative and not calibrated."

## 5. State model

Global app state: - `userProfile` - `onboardingStatus` -
`selectedGoals` - `experienceMode` - `consentPreferences` - `sessions` -
`selectedSessionId` - `clips` - `favorites` - `activeFilters` -
`feedbackItems` - `demoMode` - `uiPreferences`

Session state: - `draft` - `uploading` - `queued` - `processing` -
`partial` - `complete` - `needs_review` - `failed` - `cancelled`

Clip state: - `candidate` - `verified` - `estimated` - `needs_review` -
`rejected` - `approved_for_sharing` - `private`

## 6. Interaction patterns

### Modal vs route

Use routes for major destinations and deep links. Use modals/drawers
for: - metric definitions; - filters on mobile; - share confirmation; -
correction form; - delete confirmation; - quick clip preview if the
parent context should remain visible.

### Feedback

After favorite/save: update icon and show a short confirmation. After a
correction report: show that it was submitted or simulated; do not
promise a fix. After consent change: explain what changes now and what
requires backend processing.

### Errors

Use actionable messages: - Upload failed: retry, choose another file, or
return to sessions. - No clip: show reason and related available
events. - Metric unavailable: explain missing evidence/calibration. -
Sharing blocked: explain missing consent and how to request approval. -
Processing failed: retry or report issue.

## 7. Demo data design

Keep data normalized and linked by stable IDs.

Example session: - `session_id` - `created_at` - `mode`: singles /
doubles / practice - `status` - `participants[]` - `scoreline` (nullable
and verification status) - `video_metadata` - `processing_coverage` -
`analytics_summary` - `highlight_ids[]` - `consent_snapshot` -
`data_quality_notes[]`

Example rally: - `rally_id` - `session_id` - `start_ms` - `end_ms` -
`shot_count` - `participants[]` - `outcome` - `verification_status` -
`evidence_refs[]` - `tags[]`

Example clip: - `clip_id` - `session_id` - `rally_id` (nullable) -
`start_ms` - `end_ms` - `title` - `event_type` - `participant_ids[]` -
`verification_status` - `share_status` - `thumbnail_ref` - `video_ref`

Example metric: - `metric_id` - `value` - `unit` -
`definition_version` - `sample_size` - `coverage` -
`comparison_baseline` - `comparison_value` - `verification_status` -
`evidence_refs[]`

## 8. Research prototype usability tasks

Ask participants to: 1. Find their best moment. 2. Explain what one
metric means. 3. Find a rally that contributed to a metric. 4. Compare
two sessions. 5. Save a clip without sharing it. 6. Explain who can see
a clip. 7. Change from Relax to Improve. 8. Report a wrong player label.
9. Find the reason a movement metric is unavailable. 10. Find the data
deletion/request option.

Measure task completion, time, misclicks, confidence, and qualitative
feedback. Do not assume that clicking a feature means it is useful.
