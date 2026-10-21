# 07 --- Technical Integration and Data Contracts

## 1. Architecture boundary

Frontend responsibilities: - Navigation, onboarding, preferences,
consent presentation. - Rendering session state and evidence-backed
analytics. - Filtering, sorting, local interaction state. - Clip
playback and share UX. - User feedback and correction requests. -
Displaying confidence, coverage, provenance, and limitations.

Backend / analytics responsibilities: - Video ingestion and
processing. - Player/court/shuttle tracking. - Event detection and rally
segmentation. - Scoring and event verification. - Metrics computation. -
Highlight candidate selection and clip generation. - Consent enforcement
and access control. - Persistent player/session history. - AI narration
from controlled evidence packets. - Export/deletion workflows and audit
logs.

Do not implement critical permissions or privacy enforcement only in the
frontend. The backend must enforce access and consent.

## 2. Suggested frontend architecture

Use the stack already chosen by the implementation team. If using
React/Next.js: - Route-level pages for major destinations. - Shared app
shell. - Design-system component layer. - Feature modules: onboarding,
sessions, highlights, analytics, progress, partners, settings. - Typed
API client. - Query/cache layer for server state. - Local state only for
transient UI state and prototype simulation. - Runtime validation for
API payloads. - Error boundary and route-level loading/error states.

Suggested module organization: - `app/` or `routes/` -
`components/ui/` - `components/navigation/` - `features/onboarding/` -
`features/sessions/` - `features/highlights/` - `features/analytics/` -
`features/progress/` - `features/partners/` - `features/settings/` -
`lib/api/` - `lib/schemas/` - `lib/demo-data/` -
`lib/analytics-formatters/` - `lib/permissions/` - `tests/`

## 3. API surface (illustrative contracts)

Exact paths must align with the actual backend inventory. Do not assume
these endpoints already exist.

### Profile and preferences

-   `GET /api/me`
-   `PATCH /api/me`
-   `GET /api/me/preferences`
-   `PATCH /api/me/preferences`

### Consent

-   `GET /api/me/consents`
-   `PUT /api/me/consents`
-   `POST /api/me/data-export-requests`
-   `POST /api/me/data-deletion-requests`

### Sessions

-   `GET /api/sessions`
-   `POST /api/sessions`
-   `GET /api/sessions/{session_id}`
-   `POST /api/sessions/{session_id}/upload`
-   `POST /api/sessions/{session_id}/process`
-   `GET /api/sessions/{session_id}/status`
-   `POST /api/sessions/{session_id}/retry`

### Analytics

-   `GET /api/sessions/{session_id}/summary`
-   `GET /api/sessions/{session_id}/rallies`
-   `GET /api/sessions/{session_id}/shots`
-   `GET /api/sessions/{session_id}/movement`
-   `GET /api/sessions/{session_id}/tactics`
-   `GET /api/players/{player_id}/progress`
-   `GET /api/players/{player_id}/records`
-   `GET /api/players/{player_id}/journey`

### Highlights

-   `GET /api/highlights`
-   `GET /api/highlights/{clip_id}`
-   `PUT /api/highlights/{clip_id}/favorite`
-   `POST /api/highlights/{clip_id}/share-requests`
-   `POST /api/highlights/{clip_id}/corrections`

### Partners and teams

-   `GET /api/partners`
-   `GET /api/partners/{partner_id}/memories`
-   `POST /api/partners/invitations`

### Feedback

-   `POST /api/feedback`

These are design placeholders. Before integration, verify actual backend
routes, schemas, auth rules, and ownership checks.

## 4. API response principles

Every analytics response should include: - schema version; - session and
player scope; - generation timestamp; - metric/event definitions or
stable IDs; - verification status; - data coverage; - sample size; -
provenance/evidence references; - warnings/limitations; - processing
state where relevant.

Avoid a response that returns only `{ "value": 0.83 }` without unit,
denominator, baseline, or evidence context.

## 5. Canonical entities

### Player

-   `player_id`
-   `display_name`
-   `avatar_ref` (optional)
-   `experience_mode`
-   `preferences`
-   `consent_summary`
-   `created_at`

### Session

-   `session_id`
-   `owner_id`
-   `format`
-   `status`
-   `created_at`
-   `recording_metadata`
-   `participants`
-   `score_state`
-   `processing_coverage`
-   `data_quality_notes`

### Participant

-   `participant_id`
-   `session_player_id` or stable player reference
-   `display_label`
-   `identity_status`
-   `consent_scope`

### Event

-   `event_id`
-   `session_id`
-   `event_type`
-   `start_ms`
-   `end_ms`
-   `player_id` nullable
-   `team_id` nullable
-   `verification_status`
-   `confidence_metadata`
-   `evidence_refs`
-   `definition_version`
-   `created_at`

### Metric

-   `metric_id`
-   `scope`: session / player / pair
-   `value`
-   `unit`
-   `definition_version`
-   `sample_size`
-   `coverage`
-   `baseline`
-   `comparison`
-   `verification_status`
-   `evidence_refs`
-   `limitations`

### Highlight

-   `clip_id`
-   `session_id`
-   `rally_id`
-   `start_ms`
-   `end_ms`
-   `event_type`
-   `participant_ids`
-   `verification_status`
-   `share_permissions`
-   `storage_ref`
-   `thumbnail_ref`

### Consent record

-   `consent_id`
-   `subject_id`
-   `purpose`
-   `status`
-   `captured_at`
-   `policy_version`
-   `revoked_at` nullable
-   `scope`

## 6. Processing orchestration and partial results

The UI should consume a normalized status model: - `queued` -
`running` - `partial` - `complete` - `needs_review` - `failed` -
`cancelled`

Each stage may expose: - `stage_id` - `status` - `started_at` -
`completed_at` - `result_count` - `error_code` safe for users -
`retryable`

Do not leak internal stack traces or infrastructure details to end
users. Log diagnostic details server-side.

## 7. Performance requirements

Set budgets with the engineering team and validate on target devices.
Suggested UX targets: - App shell should render quickly from
cached/static UI. - Page navigation should not wait for unrelated heavy
analytics. - Recap summary should load independently of advanced
tactics. - Charts should use pre-aggregated summaries where possible. -
Clip thumbnails should be lazy-loaded. - Video should not autoplay in a
gallery. - Long histories should be paginated or virtualized. - Heavy
processing should be asynchronous. - Cache keys must include
user/session scope and relevant filters. - Never serve another user's
private video or analytics from a shared cache.

## 8. Security and privacy

-   Authentication and authorization enforced server-side.
-   Object-level access checks for every session, clip, and partner
    route.
-   Signed/expiring media URLs if applicable.
-   Least-privilege access.
-   Consent ledger and auditable permission changes.
-   Separate analysis, retention, sharing, and model-improvement
    purposes.
-   Deletion and export jobs should have clear status.
-   Avoid logging raw video, secrets, or sensitive identifiers.
-   Rate-limit uploads, processing, and sharing requests.
-   Protect against IDOR, unsafe file uploads, and URL guessing.
-   Use secure defaults for media storage.
-   Do not expose raw model traces or internal prompts in the UI.

## 9. AI service boundary

AI narration receives a constrained evidence packet, not unrestricted
access to all user data. The response should contain: - concise
narrative; - referenced evidence IDs; - claim types; - caveats; -
optional action suggestions.

Validate every referenced event/metric ID against the packet. Reject
unsupported numbers or claims. The UI should render the deterministic
value separately from AI-written text so the model cannot silently alter
the metric.

## 10. Observability

Track: - route and API errors; - processing duration by stage; -
percentage of sessions with partial/failure status; - highlight
generation and review outcomes; - correction reports; - consent denials
and blocked share attempts; - latency for recap, clips, and analytics; -
client-side performance; - metric definition/version used.

Avoid collecting unnecessary behavioral data. Analytics instrumentation
itself must respect privacy choices and applicable policy.
