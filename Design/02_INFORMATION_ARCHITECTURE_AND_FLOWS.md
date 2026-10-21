# 02 --- Information Architecture, Routes, and User Flows

## 1. Navigation model

Use a persistent app shell with: - Brand / home link. - Primary
navigation. - Current session or upload status when relevant. - Search
(optional for prototype). - Notifications only if user-enabled. -
Profile/avatar menu. - Experience-mode switch: Relax / Explore / Improve
/ Competitive.

Desktop primary navigation: 1. Home 2. Sessions 3. Highlights 4.
Progress 5. My Journey 6. Partners 7. Advanced Analytics (visible when
enabled)

Secondary items under profile/settings: - Profile - Preferences -
Privacy & consent - Data & exports - Help & feedback

Mobile navigation should prioritize Home, Sessions, Highlights,
Progress, and Profile. Put less-used routes in a "More" menu. Avoid an
overcrowded bottom bar.

## 2. Sitemap and suggested routes

-   `/welcome`
-   `/auth`
-   `/onboarding`
-   `/onboarding/preferences`
-   `/onboarding/consent`
-   `/home`
-   `/sessions`
-   `/sessions/new`
-   `/sessions/:sessionId`
-   `/sessions/:sessionId/processing`
-   `/sessions/:sessionId/recap`
-   `/sessions/:sessionId/highlights`
-   `/sessions/:sessionId/analytics`
-   `/sessions/:sessionId/analytics/rallies`
-   `/sessions/:sessionId/analytics/shots`
-   `/sessions/:sessionId/analytics/movement`
-   `/sessions/:sessionId/analytics/tactics`
-   `/highlights`
-   `/highlights/:clipId`
-   `/progress`
-   `/progress/records`
-   `/progress/shot-repertoire`
-   `/progress/movement`
-   `/journey`
-   `/challenges`
-   `/partners`
-   `/partners/:partnerId`
-   `/advanced`
-   `/coach` (demo/future)
-   `/profile`
-   `/settings/preferences`
-   `/settings/privacy`
-   `/settings/data`
-   `/help`
-   `/feedback`

Route names may change during implementation, but preserve the
conceptual destinations and their relationships.

## 3. First-run onboarding flow

### Step 1 --- Welcome

Purpose: establish the value in plain language. Primary CTA: "See how it
works". Secondary CTA: "Explore demo". Avoid demanding account creation
before showing value.

### Step 2 --- Choose your reason

Options: - Relive great moments. - Discover what I can do. - See my
personal progress. - Celebrate with friends. - Understand my activity. -
Explore everything. Allow multiple selections; default to "Relive great
moments" if the user skips.

### Step 3 --- Choose experience depth

-   Relax: keep it light.
-   Explore: show milestones and personal bests.
-   Improve: show performance insights.
-   Competitive: show detailed match analysis. Explain that this can be
    changed anytime.

### Step 4 --- Player setup

Optional fields: - Display name or nickname. - Preferred play mode:
singles, doubles, both. - Dominant hand (optional, only if needed by a
validated analysis). - Playing level self-description: new, casual,
regular, competitive, coach/other. Do not ask for sensitive or
unnecessary data.

### Step 5 --- Consent choices

Separate toggles and explanations: - Analyze session video. - Store
session video for later playback. - Save derived statistics to player
history. - Share selected clips with named people. - Use data to improve
models (off by default; separate explicit opt-in). Consent to analysis
is not consent to sharing or model training.

### Step 6 --- First value

Offer: - "View sample session" (best default). - "Add my first session"
(if supported). - "Finish setup". Show a short sample recap before
asking the user to configure advanced settings.

## 4. Session lifecycle flow

`New session → Select mode → Confirm participants/permissions → Upload/connect recording → Processing status → Partial results → Recap ready → Highlights → Analytics → Save/share/feedback`

States: - Draft: user has not started processing. - Uploading: progress
and cancel. - Queued: waiting for processing. - Processing: current
stage and honest ETA only if available. - Partial: highlights or score
are available but some analytics remain pending. - Complete: results
available. - Needs review: uncertain player attribution or event
labels. - Failed: explain what failed, preserve uploaded data according
to policy, offer retry or support. - Cancelled: show what was cancelled
and what remains stored.

Never display a fake percentage that is not based on real task progress.
In demo mode, label the progression as simulated.

## 5. Core journeys

### Journey A --- casual player wants a great clip

Home → Recent session → Recap → Best moment → Clip detail → Save or
share → Back to recap.

Success: player sees a relevant moment quickly and can keep it private
or share it intentionally.

### Journey B --- player wants to know whether they are improving

Home → Progress → Choose metric → Compare comparable sessions → Open
evidence clip → Read explanation → Optional next focus.

Success: player understands the comparison and its limits.

### Journey C --- doubles pair wants shared memories

Sessions → Doubles session → Team recap → Partnership highlight →
Partner memory → Invite/approve partner → Share selected clip.

Success: pair-level achievements are celebrated without obscuring
individual contribution or bypassing consent.

### Journey D --- competitive player wants tactical detail

Switch to Competitive → Session analytics → Rally timeline → Filter by
score/shot/player → Open rally → Inspect sequence and placement → Export
report.

Success: advanced information is findable, filterable, and traceable to
source events.

### Journey E --- user finds an incorrect event

Open clip/metric → "Something looks wrong" → choose issue (wrong player,
wrong shot, wrong score, poor clip, other) → optional correction →
submit → show confirmation and review status.

Success: user can challenge the system without having to contact support
first.

### Journey F --- user wants privacy control

Profile → Privacy & consent → inspect each permission → revoke future
use or request deletion/export → clear explanation of consequences and
processing time.

Success: the user understands what is stored, what changes immediately,
and what may require a backend deletion job.

## 6. Navigation and state rules

-   Back navigation should preserve the prior filters and scroll
    position when reasonable.
-   Opening a clip from a chart should preserve the analytics context
    and offer "Return to analysis".
-   Filter changes must update visible results and URL/query state where
    practical.
-   Empty states must offer a next step, not a dead end.
-   Users can browse sample data without granting camera/video
    permissions.
-   When a user has no historical sessions, replace trend claims with
    first-session guidance.
-   A profile with no partner data should show an invitation or "Add
    partner" explanation, not fake history.
-   In mobile layouts, charts must remain readable; provide summary
    cards and accessible tabular values.
