# Badminton Analytics Platform --- Complete Product Design & Prototype Specification

Version 1.0 \| Build-ready working specification

This consolidated document combines product requirements, information
architecture, screen-by-screen UX, design system, analytics contracts,
prototype behavior, technical integration, and QA acceptance criteria.
The separate files in the documentation pack are easier to maintain
independently.

------------------------------------------------------------------------

------------------------------------------------------------------------

# DOCUMENT: 00_README_AND_BUILD_ORDER.md

# Badminton Analytics Platform --- Product Documentation Pack

Version: 1.0\
Purpose: Build a complete, coherent product-design prototype from
onboarding through all major analytics pages.

## What this pack is

This is the working product specification for a badminton analytics
platform serving recreational players first, while supporting
improvement-oriented players, competitive athletes, coaches, and clubs.
It translates the product vision into information architecture, user
journeys, screen-level specifications, interactions, data contracts,
analytics definitions, prototype behavior, and acceptance criteria.

The prototype should communicate a believable end-to-end product, not
merely a collection of attractive static dashboards. Where live
computer-vision data is unavailable, use clearly labelled demo data and
preserve realistic loading, processing, uncertainty, empty, error, and
consent states.

## Pack contents

1.  `01_PRODUCT_REQUIREMENTS.md` --- product vision, goals, users,
    scope, principles, requirements.
2.  `02_INFORMATION_ARCHITECTURE_AND_FLOWS.md` --- sitemap, navigation,
    end-to-end journeys, route map.
3.  `03_SCREEN_BY_SCREEN_UX_SPEC.md` --- detailed page-by-page layouts,
    components, states, interactions, responsive behavior.
4.  `04_DESIGN_SYSTEM_AND_CONTENT.md` --- visual system, components,
    accessibility, voice, copy.
5.  `05_ANALYTICS_CATALOGUE_AND_METRIC_DEFINITIONS.md` --- insight
    taxonomy, metric contracts, confidence and evidence rules.
6.  `06_PROTOTYPE_INTERACTIONS_AND_DEMO_DATA.md` --- clickable prototype
    behavior, sample data, simulated workflows.
7.  `07_TECHNICAL_INTEGRATION_AND_DATA_CONTRACTS.md` --- frontend
    architecture, API expectations, canonical entities, processing
    states.
8.  `08_QA_ACCEPTANCE_AND_RELEASE_PLAN.md` --- test cases, acceptance
    gates, roadmap, definition of done.

## Recommended build order

### Step 1 --- Product skeleton

Implement the app shell, responsive navigation, user/profile model,
onboarding flow, session list, and demo-data mode. Ensure every route
has a coherent loading, empty, error, and populated state.

### Step 2 --- Core delight loop

Implement session detail, personal highlight reel, clip playback,
save/favorite, consent-aware sharing, and the recap. This is the core
value moment for recreational users.

### Step 3 --- Evidence-backed analytics

Implement score/rally timelines, shot repertoire, movement/court maps,
personal records, and longitudinal comparisons using deterministic demo
fixtures. Every metric should have a definition, a time window, a
confidence indicator, and an explanation.

### Step 4 --- Singles and doubles

Add match-mode-specific views. Doubles must represent team and
individual contributions without pretending that uncertain tactical
attribution is fact.

### Step 5 --- Player journey and personalization

Add milestones, experience modes, optional challenges, preferences,
privacy controls, and feedback loops.

### Step 6 --- Advanced mode

Add competitive/tactical views, deeper filters, export/report layouts,
and coach/team workflows behind an explicit mode switch. Do not
overwhelm casual users by default.

### Step 7 --- Connect real pipeline

Replace demo fixtures with API responses while keeping the same UI
contracts. Implement processing status, partial results, confidence,
provenance, retries, and failure recovery.

## Global product rules

-   Demo data must be visibly marked as demo data.
-   Never fabricate a highlight, point outcome, shot, personal record,
    or improvement claim.
-   Never equate winning with having played well.
-   Every player should receive a positive verified highlight when the
    evidence supports one; if no reliable highlight is available,
    explain why instead of inventing one.
-   Funny or potentially embarrassing clips are private by default and
    require explicit approval before sharing.
-   Sharing a clip is separate from consenting to analysis, storage, or
    model training.
-   The default comparison is the player's own comparable history, not a
    public leaderboard.
-   The interface must never display a metric without a definition and
    enough context to interpret it.
-   Low-confidence results are omitted, marked as estimates, or shown
    for review; they are not narrated as certain facts.
-   Do not infer emotion, intent, fitness, health, injury, or
    communication from video unless a validated, explicitly consented
    capability supports that inference.
-   No streak-shaming, guilt notifications, forced challenges, or public
    rankings by default.
-   The system should work on desktop for detailed review and on mobile
    for quick recaps, clip viewing, and sharing.

------------------------------------------------------------------------

# DOCUMENT: 01_PRODUCT_REQUIREMENTS.md

# 01 --- Product Requirements Document

## 1. Product definition

**Working product name:** Rally / Badminton Analytics Platform (brand
name TBD)

**Product statement:** A video-powered badminton companion that turns a
match into memorable highlights, understandable personal progress,
useful performance insights, and shared sporting memories.

The product has one evidence core and several experience layers: -
**Enjoy:** highlights, memories, fun moments, social recap. -
**Discover:** shot repertoire, rally stories, personal bests, optional
challenges. - **Improve:** actionable insights, consistency trends,
court coverage, shot outcomes. - **Compete:** tactical patterns,
opponent tendencies, advanced match analysis. - **Coach & team:**
session review, athlete comparisons, training notes, group-level
summaries.

The default experience is Enjoy + Discover. Improve and Compete can be
enabled without changing the underlying evidence model.

## 2. Target users

### Primary: recreational player

Plays for enjoyment, fitness, friendship, routine, or stress relief.
Needs a quick, positive recap and no obligation to learn technical
metrics.

### Secondary: improvement-oriented amateur

Wants to understand what is working, find repeatable strengths, and
select a manageable next focus.

### Secondary: competitive player

Wants detailed rally, shot, placement, serve/return, and tactical
analysis with filters and evidence.

### Secondary: coach or organizer

Wants to review sessions, compare athletes responsibly, organize clips,
and communicate observations.

### Secondary: doubles pair or group

Wants team memories, shared milestones, and a fair view of individual
and pair contributions.

## 3. Jobs to be done

-   After a game, help me relive my best moment without hunting through
    the full recording.
-   Help me see something I did well, even if I lost.
-   Show whether my game is changing across comparable sessions.
-   Let me understand technical metrics in plain language.
-   Let me choose whether I want a relaxed recap or deep performance
    analysis.
-   Help me share the right clip with the right people.
-   Help a doubles pair celebrate teamwork without assigning blame from
    uncertain evidence.
-   Help a coach find relevant moments quickly.
-   Let me correct player attribution, event labels, and mistaken
    claims.
-   Keep my videos, identity, and social moments under my control.

## 4. Product outcomes

### North-star measure

**Meaningful session recap rate:** percentage of completed sessions for
which a player views at least one verified personal highlight or
meaningful insight and rates the recap as useful or enjoyable.

### Supporting measures

-   Recap completion rate.
-   Time to first meaningful moment.
-   Percentage of sessions with a verified positive highlight per
    participant.
-   Clip save/favorite rate.
-   Voluntary return rate at 7 and 28 days.
-   Percentage of players who understand at least one insight.
-   Player correction rate and correction resolution time.
-   Player-attribution and event-label accuracy.
-   Consent comprehension and privacy complaint rate.
-   Analytics processing success and latency.
-   False-highlight and false-record rate.

### Guardrail measures

-   Public sharing without consent: target zero.
-   Fabricated or unsupported claims: target zero.
-   Shame, pressure, or unwanted comparison reports.
-   Excessive notification opt-outs.
-   Misleading health or injury claims.
-   Unresolved identity disputes.

## 5. Product principles

1.  Enjoyment before evaluation.
2.  Progress without pressure.
3.  Personal history before public ranking.
4.  Evidence before narration.
5.  Consent before sharing.
6.  Individual identity and pair identity are distinct.
7.  Uncertainty is a product state, not an implementation detail.
8.  The user can correct the system.
9.  Technical depth is available, not forced.
10. A session is valuable even if the player loses or has a low-activity
    day.

## 6. Scope

### Prototype must include

-   Welcome / value proposition.
-   Sign in / continue as demo.
-   Onboarding and experience preferences.
-   Consent and privacy explanation.
-   Player profile and optional display name/nickname.
-   Home dashboard.
-   Session list and session detail.
-   Processing state.
-   Post-session recap.
-   Highlight reel and individual clip detail.
-   Singles analytics.
-   Doubles analytics.
-   Rally timeline.
-   Shot repertoire and shot outcomes.
-   Court coverage / movement view.
-   Personal progress and records.
-   Player journey / milestones.
-   Challenges (optional).
-   Social/pair memory.
-   Advanced analytics mode.
-   Settings, privacy, consent, export/delete request entry points.
-   Help, metric explanations, feedback/report issue.
-   Responsive states and a realistic demo dataset.

### Out of scope for the first clickable prototype

-   Production-grade computer vision.
-   Real payment flows.
-   Live multi-camera synchronization.
-   Medical-grade fitness or injury prediction.
-   Unreviewed public social feed.
-   Public global leaderboards by default.
-   Automated coaching that claims to diagnose biomechanical problems.
-   Actual upload or deletion of sensitive video unless the backend
    exists.

## 7. Experience modes

### Relax

Default for new players. Shows memories, highlights, session summaries,
and optional activity.

### Explore

Adds personal records, shot repertoire, skill discoveries, and gentle
optional challenges.

### Improve

Adds evidence-backed performance metrics and recommendations.

### Competitive

Adds detailed filters, tactical analysis, and match-level comparisons.

Mode is reversible at any time. Users can mix modules rather than being
locked into a persona.

## 8. Core user journey

1.  User arrives and understands the promise.
2.  User signs in or opens demo mode.
3.  User chooses what they want from badminton analytics.
4.  User sets a display name and singles/doubles interests, optionally.
5.  User reviews analysis, video-storage, and sharing consent
    separately.
6.  User lands on Home with a clear "View demo session" or "Add a
    session" action.
7.  User opens a session and sees processing progress or completed
    recap.
8.  User views their best moment and session story.
9.  User explores deeper analytics if desired.
10. User saves or shares a clip only after confirming its audience and
    permissions.
11. Over time, the player sees personal milestones and
    comparable-session trends.
12. The system asks for feedback in a low-pressure way and adapts the
    experience.

## 9. Requirements by priority

### P0 --- must work in prototype

-   Navigation between all core pages.
-   A complete first-run onboarding.
-   Demo mode and persistent simulated user state during the prototype
    session.
-   A realistic session lifecycle: queued → processing → partial results
    → complete / failed.
-   Session recap with highlights and evidence-backed metrics.
-   Clip playback modal/page with timeline and event metadata.
-   Personal progress charts with comparable-session notes.
-   Metric definition and confidence display.
-   Separate individual and pair/team statistics.
-   Privacy and sharing controls.
-   Responsive design and keyboard-accessible controls.
-   Empty, loading, error, and no-confidence states.

### P1 --- should work

-   Favorite/save clips.
-   Edit display name and experience mode.
-   Filter sessions by date, mode, partner, and status.
-   Compare two comparable sessions.
-   Feedback: useful / not useful / incorrect attribution.
-   Optional challenge selection.
-   Advanced mode switch.
-   Export a summary as a simulated action.
-   Coach view in demo mode.

### P2 --- future

-   Live session monitoring.
-   Multi-camera support.
-   Wearable integrations.
-   Club/team management.
-   Training plans and coach annotations.
-   Community features with robust moderation and consent.

## 10. Content and trust requirements

Each insight must communicate: - What happened. - Why it matters for
this user or chosen mode. - Evidence or sample size. - Confidence /
coverage where relevant. - Comparison baseline and time period. - What
the user can do next, if anything. - A correction or feedback action.

Do not call a change "improvement" if the sessions are not comparable or
sample size is insufficient. Use "observed more often," "new personal
best," or "not enough evidence to compare" as appropriate.

## 11. Definition of success

A first-time recreational player should be able to reach a personal
highlight in no more than a few obvious interactions, understand the
recap without technical knowledge, and leave without being forced into
competition, sharing, or a training plan. An advanced player should be
able to find deeper metrics without the interface becoming a separate
product.

------------------------------------------------------------------------

# DOCUMENT: 02_INFORMATION_ARCHITECTURE_AND_FLOWS.md

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

------------------------------------------------------------------------

# DOCUMENT: 03_SCREEN_BY_SCREEN_UX_SPEC.md

# 03 --- Screen-by-Screen UX Specification

This document defines what the prototype must render and how each major
page behaves. A design implementation may change layout details, but not
the user intent, core content, trust rules, or required states.

## Global app shell

### Desktop layout

-   Left navigation rail or sidebar, approximately 220--260 px.
-   Main content with a readable maximum width; analytics may use wider
    canvas.
-   Top header with page title, optional breadcrumb, session status,
    mode selector, profile.
-   Use generous spacing and clear hierarchy.
-   Avoid putting every metric on the home page.

### Mobile layout

-   Compact header.
-   Bottom navigation for core destinations.
-   Cards stack vertically.
-   Charts have concise labels and a text summary.
-   Filters open in a drawer/sheet.
-   Clip actions have large touch targets.
-   Do not hide consent or confidence information behind inaccessible
    hover states.

## 1. Welcome / landing page (`/welcome`)

**Goal:** explain value quickly and let the user explore before
committing.

Content: - Headline: "Your game. Your moments. Your progress." -
Subhead: "Turn badminton sessions into highlights and insights that make
sense to you." - Three value pillars: Relive moments / Discover progress
/ Celebrate together. - Short "How it works" sequence: Play → Analyze →
Relive. - Privacy reassurance: "Your videos and clips stay under your
control." - Primary CTA: See how it works. - Secondary CTA: Explore
demo. - Tertiary sign-in link.

Interactions: - "Explore demo" opens a sample session with visible "Demo
data" label. - "See how it works" begins onboarding. - No autoplay sound
or surprise camera access.

States: normal; reduced-motion; small-screen.

## 2. Authentication / account entry (`/auth`)

Keep the prototype lightweight. Support demo access and a simulated
sign-in form if no auth provider is connected.

Content: - Continue with account (real only if integrated). - Continue
as demo. - Short explanation of why an account helps: session history
and saved highlights. - Privacy link.

States: - invalid form; - loading; - auth failure; - demo selected.

Do not claim that an account has been created if the flow is simulated.

## 3. Onboarding: goals (`/onboarding/preferences`)

**Goal:** personalize the experience without a long survey.

Components: - Progress indicator: e.g. 1 of 3. - Multi-select goal cards
with icon, title, short explanation. - "You can change this later." -
Continue and Skip actions.

Goal cards: - My best moments. - My personal progress. - Fun with
friends. - Learn my game. - Activity and movement. - Everything.

Behavior: - Selected cards have a visible selected state and accessible
label. - Do not force one answer. - Use selection to reorder Home
modules and recap priorities, not to hide core controls.

## 4. Onboarding: experience mode

Mode cards: - Relax --- "Highlights and memories, without the
pressure." - Explore --- "Discover shots, milestones, and personal
bests." - Improve --- "Understand patterns and find a focus." -
Competitive --- "Detailed match and tactical analysis."

Each card includes "Best for" text. Competitive is selectable but not
recommended as the default for first-time casual users.

CTA: "Use this experience". Secondary: "Decide later".

## 5. Onboarding: player setup

Fields: - Display name/nickname (optional). - Singles / doubles /
both. - Player type (optional self-description). - Optional avatar
upload only if supported.

Validation: - Inline validation; never block the user for optional
fields. - Nickname must be editable later. - If player identity in the
video is uncertain, ask for review rather than silently assigning stats.

## 6. Onboarding: privacy & consent

Present each permission as a separate item with plain-language
consequence: - Analyze this video. - Keep the video for playback. - Save
derived stats to my history. - Share selected clips. - Help improve
models using my data.

Default sharing and model-improvement consent to off. The
model-improvement option is separate and not bundled with essential
analysis. Include "I can change these later."

Buttons: "Save choices" and "Read privacy details".

## 7. Home dashboard (`/home`)

**Goal:** orient the user and surface one meaningful next action.

Top: - Greeting: "Good to see you back" (avoid false assumptions if
first session). - Primary CTA: "View latest recap" if available;
otherwise "Explore sample session" or "Add session". - Small session
status card if processing exists.

Sections, ordered by selected goals: 1. Latest session card with date,
singles/doubles, result if verified, and "View recap". 2. Your moment:
one verified clip thumbnail with event label and confidence state. 3.
Personal journey: one milestone or "Your first session starts your
journey". 4. Progress snapshot: at most 2--3 metrics, only if comparable
data exists. 5. Friends / partner memory, only if enabled and consented.
6. Optional next challenge, dismissible. 7. Recent sessions list.

Do not place a global leaderboard at the top. Do not make all users see
a "performance score".

Empty state: - Explain what the product will provide. - Offer sample
session and add-session CTA. - Do not display fabricated user-specific
metrics.

## 8. Sessions list (`/sessions`)

Content: - Page title "Sessions". - Search/filter by date,
singles/doubles, partner, processing status. - List/grid of session
cards with date, court/session label if available, mode, processing
status, score if verified, highlight count. - Clear "Open session"
action. - New session CTA.

States: - no sessions; - filters yield no results; - processing
sessions; - failed session; - mixed demo and real sessions (must be
visually distinguished).

Session cards must not imply a match result is final if scoring
confidence is low.

## 9. New session (`/sessions/new`)

Steps: 1. Select recording source: upload recording / connect live
capture (only if implemented) / use demo. 2. Select format: singles /
doubles / practice. 3. Add participants or use "Review participants
after processing". 4. Choose video-retention preference and analytics
options. 5. Confirm permission to analyze the footage. 6. Start
processing.

Explain accepted file types and limits only when known from backend. Do
not invent limits. Include cancellation and retry behavior. If upload is
simulated, label it.

## 10. Processing page (`/sessions/:sessionId/processing`)

Content: - Session title/date and status. - Stage list: Video ready →
Court/player detection → Rally and shot analysis → Highlights →
Analytics summary. - Real task progress if backend supplies it;
otherwise stage-based status without fabricated percentages. - Results
available so far. - "Leave page; we'll keep processing" only if
background processing actually persists. - Retry / report issue if
failed.

Partial-result card: - "Some results are ready. We're still checking the
rest." - Mark which modules are incomplete. - Never show final
confidence until the event verification stage is complete.

## 11. Session detail / overview (`/sessions/:sessionId`)

Header: - Session date/time, mode, participants, session status. -
Verified score or "Score needs review". - Actions: View recap, View
analytics, Edit session details, Report issue.

Overview tabs: - Summary. - Highlights. - Analytics. - Participants
(when relevant).

Summary content: - Short factual session summary. - Best verified
moment. - Rally length / shot / activity snapshots where supported. -
Processing confidence/coverage. - Data-source note and "How is this
measured?" link.

## 12. Post-session recap (`/sessions/:sessionId/recap`)

This is the most important casual-player page.

Order: 1. Emotional entry: "Your session, in moments." 2. Hero highlight
with thumbnail, play control, event label, and player attribution. 3.
Personal recognition: one positive verified achievement per player when
evidence allows. 4. Three concise facts, no more. 5. "What stood out"
narrative grounded in verified evidence. 6. Social/team moment if
available and approved. 7. Optional next step: explore progress, save a
moment, or try a challenge. 8. "Was this recap useful?" feedback.

Copy examples: - "You kept this rally alive for 12 shots." - "A new
personal best: your longest verified rally." - "Both partners
contributed to this extended exchange." - "We couldn't reliably identify
a highlight for every player in this recording. Review participant
labels to improve attribution."

Never say "you dominated", "you are bad at defence", or "you clearly
felt confident" unless such language is explicitly supported and
appropriate. Avoid assigning blame.

## 13. Highlights library (`/highlights`)

Content: - Filters: session, player, singles/doubles, type, favorites,
shared/approved. - Grid of clip cards. - Each card: thumbnail, duration
if available, event label, date, participant, confidence/verification
state. - Favorite toggle. - Multi-select only for actions where each
clip's consent allows it.

Tabs: - For you. - Favorites. - Shared with me (only if real sharing
exists). - Team moments.

Empty state: explain how clips are created and offer latest
session/demo.

## 14. Clip detail (`/highlights/:clipId`)

Layout: - Video player / simulated player. - Clip title and event
type. - Session and timestamp. - Participants and attribution
confidence. - Save/favorite. - Share action. - "Open rally analysis". -
"Something looks wrong" correction action. - "How this highlight was
selected" explanation. - Related moments.

Share flow: 1. Choose audience. 2. Preview clip and visible
participants. 3. Confirm all required permissions. 4. Confirm share. 5.
Show truthful success/failure from actual share implementation. Never
create a public link by default.

## 15. Session analytics overview (`/sessions/:sessionId/analytics`)

Use a clear sub-navigation: - Overview. - Rallies. - Shots. -
Movement. - Tactics (Improve/Competitive modes only).

Overview: - Session metadata and data coverage. - Score progression if
verified. - Rally length distribution. - Shot repertoire. - Player
comparison only if requested and contextually fair. - Key observations
with evidence links. - Download/export if implemented.

Each chart must include: - Clear title and unit. - Time window. - Sample
size or coverage. - Explanation and uncertainty. - Accessible text/table
alternative. - Link to relevant rally/clip where possible.

## 16. Rally timeline (`/sessions/:sessionId/analytics/rallies`)

Content: - Rally list with start/end time, shot count, verified outcome
if available, key event tags. - Timeline visualization showing rally
sequence across match time. - Filters: player, point outcome, rally
length, event tag. - Selecting a rally opens a side panel with clip,
event sequence, confidence, and evidence. - Allow sorting by longest,
latest, key moment, or reviewed status.

No point outcome should be presented as final if not verified.

## 17. Shot analytics (`/sessions/:sessionId/analytics/shots`)

Content: - Shot repertoire by player. - Shot count distribution. - Shot
outcomes or continuation rates only when denominators are valid. - Shot
sequence patterns. - Placement map only when court mapping and shuttle
landing confidence support it. - Filters: player, shot type, score
phase, rally outcome. - Each shot type opens representative clips.

Metric labels should be human-readable; technical taxonomy belongs in an
expandable detail panel.

## 18. Movement / court coverage (`/sessions/:sessionId/analytics/movement`)

Content: - Court map with player movement or observed court-region
coverage. - Movement path only when tracking quality is sufficient. -
Coverage by zone. - Rally movement examples. - Calibration and
camera-angle note. - Optional activity duration.

Do not show precise distance or speed unless calibrated and validated.
If not calibrated, use relative movement or zone presence with a visible
limitation note.

## 19. Tactical analysis (`/sessions/:sessionId/analytics/tactics`)

Visible only in Improve/Competitive modes, and only for validated
capabilities.

Potential modules: - Rally-start patterns. - Shot sequence patterns. -
Placement and response tendencies. - Serve/return analysis. -
Pressure-point context, if score is verified. - Opponent tendencies with
sufficient samples. - Evidence clips for every claim.

Every tactical claim must include sample size and a link to examples.
Use "In the observed rallies..." rather than broad claims about a
player's entire ability. If data is insufficient, say so.

## 20. Progress overview (`/progress`)

Content: - Date range and comparison baseline. - Progress cards: rally
length, observed shot repertoire, valid return rate, court-zone
coverage, personal records. - Trend chart with session markers. -
Comparable-session indicator. - "What changed?" list. - Click-through to
evidence clips. - Option to hide metrics not relevant to the user.

If there are fewer than two comparable sessions, show "Your first
session is the baseline" and avoid a trend chart pretending to show
progress.

## 21. Personal records (`/progress/records`)

Content: - Records by category: rally, shot discovery, defence,
placement, participation, doubles partnership. - Record date and source
session. - Replay evidence. - Filters by singles/doubles and date. -
Record verification status.

A record must have an exact definition and reliable source event. Do not
rank incomparable sessions as one record.

## 22. Shot repertoire (`/progress/shot-repertoire`)

Content: - Shot types observed across sessions. - First observed date. -
Most recent verified example. - Count and confidence/coverage. -
Optional player confirmation: "I can do this shot" / "This label seems
wrong".

Distinguish "observed in video" from "mastered". A detected shot is not
proof of mastery.

## 23. Movement progress (`/progress/movement`)

Content: - Comparable movement/zone trends. - Activity-duration history
if available. - Calibration status. - Optional self-reported
energy/readiness. - General educational guidance only.

Do not label this as a medical fitness assessment. Never infer injury
risk from ordinary movement summaries.

## 24. My Journey (`/journey`)

Content: - Personal timeline of verified milestones. - Saved favorite
moments. - Firsts: first saved highlight, first verified shot category,
personal best, first doubles memory. - Session count and participation
milestones. - Player-selected favorite memories. - Optional story
export.

No penalty for inactivity. Returning after a break should be welcomed,
not framed as failure.

## 25. Challenges (`/challenges`)

Content: - Optional challenges based on experience mode. - Each
challenge states goal, difficulty, evidence needed, and why it might be
enjoyable. - Progress can be dismissed. - No challenge should require
unsafe behavior or unnatural play. - Rewards should recognize
participation and personal bests, not only absolute performance.

Example challenges: - Rally Explorer: beat your own longest rally. -
Shot Explorer: discover a new shot type. - Court Explorer: explore
different court zones. - Doubles Duo: save a rally where both partners
contribute. - Just Showed Up: complete a session you chose to play.

## 26. Partners (`/partners`)

Content: - Partner cards with nickname, shared sessions, shared approved
memories. - Add/invite partner only if supported. - Separate private
individual statistics from shared pair statistics. - Partner access
status and consent.

## 27. Partner memory (`/partners/:partnerId`)

Content: - Shared timeline. - Best verified pair rallies. - Joint
personal records. - Approved clips. - Pair-level trends only when sample
sizes support comparison. - Partner permissions and remove/unlink
controls.

Never imply that one partner is responsible for a lost point based on
uncertain attribution.

## 28. Advanced analytics (`/advanced`)

Purpose: give serious players and coaches deeper controls without
overwhelming default users.

Modules: - Session comparison. - Detailed event filters. - Rally
sequence explorer. - Shot and placement matrices. - Export/report
tools. - Confidence/coverage panel. - Coach notes (if implemented).

Show the exact selected sample and filters. Advanced views must not
remove evidence and caveats.

## 29. Coach view (`/coach`) --- prototype/future

Include only as a clearly marked demo unless coach accounts and
permissions exist.

Content: - Athlete/session selector. - Session review. - Annotated
clips. - Training focus notes. - Athlete-approved progress views. - Team
summary with fair comparison rules.

No coach should see a player's private session without permission.

## 30. Profile (`/profile`)

Content: - Display name, avatar, play mode, preferred experience mode. -
Saved highlights. - Player-history summary. - Edit profile. -
Preferences and privacy shortcuts.

## 31. Preferences (`/settings/preferences`)

Controls: - Experience mode. - Home-page modules. - Preferred recap
length. - Metric units where applicable. - Notifications: disabled by
default or clearly opt-in. - Challenge suggestions on/off. - Social
memories on/off. - Accessibility preferences such as reduced motion.

## 32. Privacy & consent (`/settings/privacy`)

Content: - Consent ledger with purpose, status, and date if available. -
Analysis permission. - Video retention. - Derived-metric history. -
Sharing permissions. - Model-improvement permission. - Revoke
controls. - Data deletion/export request entry points. - Plain-language
explanation of what revocation affects.

A frontend-only prototype must say "Request simulated" or "Demo action"
rather than claiming real deletion.

## 33. Data & exports (`/settings/data`)

Options: - Export profile/session summaries (if implemented). - Request
video download (if allowed). - Request data deletion. - View processing
and retention status. - Clear demo data.

Always confirm irreversible actions. Explain what is removed and whether
shared copies may remain with recipients.

## 34. Help & feedback (`/help`, `/feedback`)

Help topics: - How analysis works. - Why some metrics are missing. - How
confidence works. - How to correct a clip. - How privacy and sharing
work. - Troubleshooting recording/camera setup.

Feedback form: - Type: inaccurate event / wrong player / poor highlight
/ confusing metric / privacy concern / other. - Optional description. -
Submit. - Show confirmation and reference only if a real backend returns
one.

## 35. Required reusable states

Every data-driven page must implement: - Loading. - Empty. - Partial
data. - Complete data. - Error. - Low confidence / insufficient
evidence. - Permission denied. - Offline/unavailable. - Demo data. -
Mobile/responsive layout.

## 36. Cross-page interaction requirements

-   Every highlight card opens a clip detail or playback modal.
-   Every metric with an evidence source can open a relevant clip/rally.
-   Every trend chart can show the underlying value and comparison
    period.
-   Every incorrect result has a correction/feedback path.
-   Every share action checks clip-specific consent.
-   Every page has a clear route back to its parent session or
    dashboard.
-   The mode switch updates the level of detail without deleting or
    altering underlying data.

------------------------------------------------------------------------

# DOCUMENT: 04_DESIGN_SYSTEM_AND_CONTENT.md

# 04 --- Design System, Accessibility, and Content Guidelines

## 1. Visual direction

Design for a modern, premium sports product that feels energetic but
calm. It should combine the clarity of a sports dashboard with the
warmth of a personal memory product.

Recommended visual language: - Deep ink / charcoal text. - Warm
off-white or neutral canvas. - One vivid badminton-inspired accent
color. - A secondary cool accent for analytics. - Green reserved for
verified positive status, not generic decoration. - Amber for
uncertainty or attention. - Red only for destructive actions or genuine
errors. - Rounded cards with restrained borders. - High-quality
thumbnails and generous whitespace. - Charts that prioritize readability
over decoration.

Do not use neon gradients everywhere, excessive glassmorphism, or a wall
of cards. Use visual emphasis for one primary action and one main
insight per screen.

## 2. Typography

-   Use a highly readable UI sans-serif.
-   Strong page titles, concise card headings, readable body copy.
-   Numeric values should use tabular figures where possible.
-   Use no more than three typographic levels within a single card.
-   Avoid tiny axis labels and all-caps paragraphs.
-   Do not communicate confidence using color alone.

## 3. Spacing and layout

Use a consistent spacing scale, for example 4 / 8 / 12 / 16 / 24 / 32 /
48 / 64 px. - Standard card padding: 16--24 px. - Form groups: clear
vertical rhythm. - Wide analytics pages may use a 12-column grid. - Keep
reading text at a comfortable line length. - Preserve a clear primary
action at the top of long pages. - On mobile, cards stack; avoid
horizontal scrolling except for intentionally scrollable timelines.

## 4. Core components

### App shell

Sidebar/bottom navigation, page header, mode switch, profile menu,
processing status.

### Button hierarchy

-   Primary: one key action per view.
-   Secondary: alternate action.
-   Tertiary/text: low-emphasis navigation.
-   Destructive: explicit and separated. Buttons must have loading,
    disabled, hover, focus, and pressed states.

### Session card

Thumbnail or sport icon, date, singles/doubles, status, verified score
if available, highlight count, open action.

### Highlight card

Thumbnail, event title, session date, participant, duration if known,
verification/confidence marker, favorite action. Never autoplay video in
a grid.

### Metric card

Metric name, value, unit, baseline/change, sample size, status, info
action, evidence link.

### Confidence badge

Use text such as "Verified", "Estimate", "Needs review", or
"Insufficient evidence". Pair with an icon and explanatory text.

### Chart card

Title, date range, chart, accessible summary, sample size, caveat,
source/evidence link.

### Empty state

Short explanation, one next step, optional illustration. Avoid blaming
the user for having no data.

### Feedback panel

Small, dismissible, non-blocking, with "Useful", "Not useful", and
"Report an issue".

### Consent control

Separate toggle per purpose, a concise explanation, current status, and
link to full details.

### Clip player

Accessible controls, captions/metadata where applicable, keyboard
operation, playback speed only if supported, share/save actions outside
the video canvas.

### Filter bar

Clear current filters, visible active-filter count, sensible defaults,
mobile drawer.

## 5. Data visualization rules

-   Use a chart only when it helps answer a question.
-   Every chart needs a title that states the subject, not "Analytics".
-   Include unit, time range, sample size, and baseline.
-   Provide a text summary and/or accessible table.
-   Do not imply a continuous trend from sparse points.
-   Use zero-based axes for counts unless a clear reason exists
    otherwise.
-   Avoid dual axes unless necessary.
-   Distinguish missing values from zero.
-   Use direct labels where possible.
-   Do not use red/green alone to show good/bad performance.
-   A scoreline and a performance metric must be visually distinct.
-   When confidence is low, avoid a chart that makes the result look
    precise.

## 6. Accessibility

Target WCAG 2.2 AA as an implementation goal. - Keyboard navigation for
all controls. - Visible focus ring. - Semantic heading hierarchy. -
Accessible names for icon-only controls. - Minimum 4.5:1 contrast for
normal text where applicable. - Touch targets ideally at least 44 × 44
CSS pixels. - Captions or text alternatives for important video content
when available. - Respect reduced-motion settings. - Never rely on hover
to expose essential information. - Screen-reader summaries for charts. -
Avoid flashing, rapidly pulsing status, or forced animation. - Form
errors must be associated with fields. - Keep focus predictable after
dialogs close.

## 7. Content voice

Voice: encouraging, clear, respectful, grounded, never patronizing.

Use: - "Here's a moment worth replaying." - "A new personal best in your
observed sessions." - "You kept this rally going for 11 shots." - "This
estimate is based on 8 classifiable rallies." - "We need more comparable
sessions before showing a trend." - "Want to explore this pattern?"

Avoid: - "You are bad at..." - "You failed..." - "Your partner
caused..." - "You are definitely improving" when evidence is weak. -
"You burned exactly X calories" without validated measurement. - "You
looked angry/confident/tired" based only on video. - "You must play
tomorrow to keep your streak."

## 8. Microcopy standards

### Loading

"Preparing your session recap..."\
"Checking player and rally labels..."\
"Some insights are ready while the rest finish processing."

### Empty state

"Your badminton story starts with your first session."\
"Once we have comparable sessions, your progress view will begin to take
shape."

### Low confidence

"We couldn't identify this event reliably enough to include it as a
verified highlight."\
"Review participant labels to improve the accuracy of your recap."

### Correction

"Thanks for flagging this. Your report will help us review the event."\
Only promise correction if the backend actually supports review and
resolution.

### Sharing

"Choose who can see this clip."\
"Sharing this clip does not change your video-analysis or
model-improvement settings."

## 9. Motion and transitions

-   Use motion to clarify hierarchy or state change, not to decorate.
-   Keep transitions short and optional.
-   No confetti for ordinary metrics; use restrained celebration for
    meaningful personal records.
-   Respect reduced-motion.
-   Never animate performance scores in a way that implies false
    precision.

## 10. Responsive behavior

Desktop: - Persistent sidebar. - Wide charts and multi-column layouts. -
Side panel for rally details.

Tablet: - Collapsible sidebar. - Two-column cards where practical. -
Filters remain visible if space allows.

Mobile: - Bottom navigation. - Single-column cards. - Filters in
sheets. - Sticky primary action only when it does not cover content. -
Video player and clip controls sized for touch. - Tables transform into
labeled rows or horizontally scroll only when necessary.

------------------------------------------------------------------------

# DOCUMENT: 05_ANALYTICS_CATALOGUE_AND_METRIC_DEFINITIONS.md

# 05 --- Analytics Catalogue and Metric Contracts

## 1. Metric governance

A metric is not ready for production merely because a model can emit a
number. Each metric must have: - Stable metric ID and display name. - A
plain-language definition. - A formula or deterministic computation
rule. - Required source events. - Inclusion/exclusion rules. - Minimum
sample requirements. - Confidence and coverage logic. - Calibration
assumptions. - Known failure modes. - Comparison eligibility rules. -
Evidence links. - Versioned implementation. - A user-facing
explanation. - A correction/reporting path.

## 2. Evidence levels

Recommended event status: - `verified`: passed defined validation
checks. - `estimated`: useful but relies on approximate measurement. -
`needs_review`: ambiguous identity, event, or outcome. - `rejected`:
failed validation. - `unavailable`: required source evidence does not
exist.

Never silently turn `estimated` or `needs_review` into a verified claim.

## 3. Core event families

### Session events

Session created, upload started, upload complete, processing stage
updated, processing failed, session completed.

### Match events

Match format, game/set, point, score state, server if known, point
outcome, score verification.

### Rally events

Rally start/end, shot count, duration, participants, outcome, key
moments.

### Shot events

Shot type, timestamp, player, side, court region, shuttle
trajectory/landing region, response, confidence.

### Movement events

Player position, court-zone presence, path segment, estimated
speed/distance only when calibrated, coverage and tracking confidence.

### Highlight events

Candidate moment, selection reason, clip range, participants,
verification status, share permissions.

### Social events

Favorite, player-approved celebration clip, pair memory, share action,
consent status. Do not infer private emotion or intent.

## 4. Highlight catalogue

Possible categories: - Best verified rally. - Longest verified rally. -
Best smash / drop / clear / drive / net shot. - Defensive recovery. -
Unexpected successful return. - Cross-court placement. - Rally-saving
shot. - Match-point save (only if score is verified). - Comeback
sequence (only if scoring data supports it). - Shot discovery. -
Personal-best rally. - Doubles teamwork. - Partner rescue. - Coordinated
attack. - Joint defence. - Approved celebration. - Approved funny
moment. - Favorite memory.

Highlight ranking should balance: - Evidence confidence. - Relevance to
the player's chosen goals. - Clip quality and complete context. -
Novelty relative to prior clips. - Variety across players and event
types. - Fairness across winners and losers. - Consent eligibility.

Do not rank only by explosive movement or winning shots; this can
systematically exclude defensive and beginner moments.

## 5. Metric catalogue

### A. Session summary

-   `session_duration`: recording duration or detected playable
    duration; specify which.
-   `active_rally_time`: sum of verified rally intervals; not the same
    as total exercise time.
-   `verified_rally_count`: count of rallies passing segmentation
    checks.
-   `verified_point_count`: count of points with reliable outcome.
-   `scoreline`: only if scoring and game boundaries are sufficiently
    verified.
-   `processing_coverage`: percentage of video/time for which required
    tracking and analysis were available, with method documented.

### B. Rally metrics

-   `rally_shot_count`: number of classifiable shot/contact events in a
    verified rally.
-   `rally_duration`: end timestamp minus start timestamp under a
    defined boundary rule.
-   `long_rally_count`: number of rallies meeting a configurable shot
    threshold.
-   `rally_length_distribution`: distribution of verified rally shot
    counts.
-   `player_rally_participation`: rallies in which a player was observed
    participating, not a rating of contribution quality.
-   `rally_outcome_rate`: outcomes per valid opportunity; must define
    whether denominator is points, rallies, or shots.

### C. Shot metrics

-   `observed_shot_repertoire`: unique shot types detected with
    sufficient confidence.
-   `shot_count_by_type`: classifiable events by shot category.
-   `shot_type_share`: shot-type count divided by all classifiable shot
    events; show the denominator.
-   `valid_return_rate`: successful observed returns divided by
    classifiable eligible return attempts; never use when
    eligibility/outcome is uncertain.
-   `placement_distribution`: verified landing/target regions by court
    zone.
-   `shot_sequence_frequency`: observed consecutive shot-type pairs or
    short sequences.
-   `shot_outcome_association`: descriptive association only; do not
    claim causal effectiveness without a suitable design.

### D. Movement metrics

-   `court_zone_coverage`: distinct or weighted zones visited during
    valid tracking intervals.
-   `movement_path`: observed path under calibrated court mapping and
    validated tracking.
-   `estimated_distance`: only if perspective calibration and scale
    conversion are validated.
-   `estimated_speed`: only if time synchronization, scale, and tracking
    accuracy are validated.
-   `movement_intensity_proxy`: explicitly label as a video-derived
    proxy, not physiological intensity.
-   `active_rally_duration`: not equivalent to calories, cardiovascular
    load, or total exercise duration.

### E. Personal progress

-   `personal_best_rally`: longest verified rally under a consistent
    event definition.
-   `personal_best_shot_count`: maximum valid count for a specified shot
    type, if meaningful.
-   `new_shot_observed`: first verified observation of a shot category
    in the player's available history.
-   `session_to_session_change`: difference or relative change between
    comparable sessions, with baseline and sample sizes.
-   `trend_confidence`: confidence that the observed difference is
    interpretable given data coverage and comparability.

### F. Doubles and partnership

-   `pair_rally_count`: verified rallies involving the pair.
-   `joint_participation_rate`: rallies in which both partners have
    verified contributions, with clear event definition.
-   `partner_support_event`: a validated sequence in which a partner
    returns play after a difficult position; label as event, not intent.
-   `coordinated_attack_event`: verified sequence satisfying an explicit
    tactical pattern definition.
-   `pair_personal_best`: best verified pair event under a stable
    definition.
-   `pair_comparison`: only across comparable partners, format, sample,
    and recording conditions.

### G. Optional activity summaries

-   `detected_playing_time`: time in detected play segments.
-   `session_frequency`: number of recorded sessions in a chosen window.
-   `participation_streak`: avoid as default; if present, make optional
    and never shame absence.
-   `self_reported_energy`: explicitly player-provided, not inferred
    from video.
-   `self_reported_enjoyment`: explicitly player-provided.

## 6. Comparison eligibility

Only compare sessions when the relevant conditions are sufficiently
similar: - Same metric definition/version. - Sufficient event count. -
Comparable singles/doubles format. - Similar camera setup and
calibration for spatial metrics. - Similar recording coverage. -
Reliable player identity. - Relevant filters and score context. - No
unresolved data-quality issue that would reverse the interpretation.

If conditions fail, say "Not directly comparable" and explain why.

## 7. Confidence and coverage UX

Confidence is not a universal percentage unless it is calibrated and
interpretable. Prefer a categorical state with a tooltip: - Verified:
passed the metric's defined checks. - Good coverage: enough valid
observations for the stated purpose. - Estimate: approximate
measurement; treat as directional. - Needs review: one or more key
labels are uncertain. - Insufficient evidence: not enough valid
observations.

If a numeric confidence score is exposed, document calibration, meaning,
and validation. Never present raw model confidence as real-world
probability without calibration.

## 8. AI narration contract

LLM input should be a controlled evidence packet, not unrestricted raw
video or a bag of unverified model outputs. Packet fields: -
Player/session identifiers scoped to permission. - Verified metrics and
definitions. - Approved evidence event IDs. - Comparison baseline and
period. - Sample sizes and coverage. - Confidence/verification states. -
Player-selected tone and experience mode. - Prohibited claims and
privacy restrictions.

The LLM may: - Summarize verified observations. - Explain metric
definitions. - Suggest a supported clip to review. - Offer a gentle
optional next step.

The LLM may not: - Change scores or metric values. - Invent an event,
highlight, or personal record. - Claim causal improvement from
descriptive data. - Diagnose health/injury or infer emotional state. -
Reveal private partner data without permission. - Convert low-confidence
events into certainty. - Make a recommendation that depends on
unavailable evidence.

## 9. Minimum evidence rules

Define metric-specific minimums in implementation. Examples: - A
personal-best label requires a stable definition and enough historical
coverage to know the available baseline. - A trend requires at least two
comparable observations; more may be necessary for a meaningful trend. -
A shot effectiveness rate requires valid eligible attempts and verified
outcomes. - A tactical tendency requires enough examples to avoid
overgeneralizing from a few rallies. - A movement map requires valid
player tracking and court calibration. - A social/celebration highlight
requires event evidence and clip-level consent.

## 10. Analytics page mapping

-   Recap: 1--3 high-value facts, one hero clip, one positive personal
    recognition when supported.
-   Rally timeline: segmentation, shot count, duration, outcome.
-   Shots: repertoire, counts, valid outcomes, sequences, placement.
-   Movement: coverage, calibrated path, optional activity.
-   Progress: comparable-session deltas and records.
-   Journey: verified milestones and saved memories.
-   Doubles: pair and individual views separated.
-   Advanced: filters, evidence tables, exports, model/data quality.

------------------------------------------------------------------------

# DOCUMENT: 06_PROTOTYPE_INTERACTIONS_AND_DEMO_DATA.md

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

------------------------------------------------------------------------

# DOCUMENT: 07_TECHNICAL_INTEGRATION_AND_DATA_CONTRACTS.md

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

------------------------------------------------------------------------

# DOCUMENT: 08_QA_ACCEPTANCE_AND_RELEASE_PLAN.md

# 08 --- QA, Acceptance Criteria, and Release Plan

## 1. Release gates

Do not call the prototype complete because every page exists. It is
complete when the core journeys work, states are credible, the evidence
is understandable, and no major privacy or accessibility failure
remains.

### Gate A --- Product coherence

-   Onboarding choices influence the experience.
-   The app has a consistent navigation model.
-   All core routes are reachable.
-   Empty states guide the user forward.
-   Demo data is clearly identified.

### Gate B --- Core experience

-   A user can open a session, view recap, play a clip, favorite it, and
    return.
-   A user can explore analytics and navigate from metrics to evidence.
-   A user can inspect a personal record and its source session.
-   Doubles pages separate individual and pair-level data.

### Gate C --- Trust and consent

-   Every share action checks clip-level permission.
-   No private clip is made public by default.
-   Consent purposes are separate.
-   Low-confidence claims are marked or omitted.
-   Incorrect labels can be reported.
-   Demo actions do not claim real backend success.

### Gate D --- Accessibility and responsive design

-   Keyboard-only navigation works.
-   Focus is visible and logical.
-   Dialogs are accessible.
-   Mobile navigation and charts remain usable.
-   Essential information is not conveyed only by color.
-   Reduced-motion preferences are respected.

### Gate E --- Data and metric integrity

-   Every displayed metric has a definition.
-   Missing data is not rendered as zero.
-   Trends use comparable sessions only.
-   The denominator is shown for rates.
-   Every evidence-backed insight can link to a source event where
    applicable.
-   Score and result status reflect verification state.

## 2. Acceptance test cases

### Onboarding

1.  New user can reach demo without creating an account.
2.  User can select multiple goals.
3.  User can choose and later change experience mode.
4.  Optional fields can be skipped.
5.  Consent options are separate and default conservatively.
6.  User can return to prior onboarding steps without losing choices.

### Home and sessions

7.  Home with no sessions shows useful next actions and no fake user
    metrics.
8.  Home with sessions surfaces the latest recap.
9.  Session filters change results correctly.
10. Processing and failed states are understandable.
11. Demo and real sessions are visually distinguished.

### Recap and highlights

12. Recap presents a verified highlight or explains why none is
    available.
13. Losing player can still receive a verified positive highlight.
14. Clip attribution displays its verification status.
15. Favorite state persists during the prototype session.
16. Sharing requires explicit audience and permission confirmation.
17. Funny clip cannot be shared without approval.
18. "Report issue" accepts a category and shows honest confirmation.

### Analytics

19. Rally timeline filters work.
20. Opening a rally reveals its event sequence and evidence.
21. Shot analytics distinguishes observed shots from mastered skills.
22. Movement analytics shows calibration/coverage limitations.
23. Rates display denominators and sample sizes.
24. Progress trend is suppressed when data is insufficient.
25. Non-comparable sessions produce a clear explanation.
26. Advanced tactical claims link to supporting examples.

### Doubles and partners

27. Individual and pair metrics are visually distinct.
28. Pair memory respects access/consent.
29. Uncertain attribution is marked needs-review.
30. No partner blame statement is generated from uncertain evidence.

### Privacy and settings

31. Revoking share permission blocks future share action.
32. Model-improvement consent is separate from analysis consent.
33. Demo deletion/export actions are labeled simulated.
34. Destructive actions require confirmation.
35. Settings clearly explain consequences.

### Accessibility

36. All controls work with keyboard.
37. All icon buttons have accessible labels.
38. Charts have text summaries.
39. Focus returns to the invoking control after closing a dialog.
40. Mobile layouts do not obscure key actions.

## 3. Manual usability test plan

Recruit a mix of: - casual players who play for social enjoyment; - new
or infrequent players; - improvement-oriented amateurs; - regular
doubles players; - competitive players/coaches for advanced-mode review.

Do not assume a single user represents "the amateur player."

Ask participants to complete: - Find your best moment. - Explain one
metric in their own words. - Find the rally behind a metric. - Save a
clip without sharing. - Change experience mode. - Compare sessions and
explain the caveat. - Find privacy controls. - Correct a wrong
attribution.

Record: - completion rate; - time on task; - wrong turns; -
interpretation accuracy; - perceived pressure or embarrassment; -
usefulness and enjoyment; - trust in the result; - accessibility
barriers.

## 4. Product experiments

Test hypotheses, not vanity metrics: - Does a concise recap create more
value than a dense dashboard? - Do personal records increase perceived
progress without creating pressure? - Do users prefer automatic clip
curation or manual control? - Does optional challenge content increase
voluntary return without increasing guilt? - Does showing confidence
improve trust and comprehension? - Do doubles pair memories create value
for both partners? - Which onboarding questions improve relevance enough
to justify their cost?

Use suitable comparison groups or staged rollouts. Measure sustained
behavior beyond initial novelty. Do not equate more screen time with a
better product.

## 5. Suggested implementation roadmap

### Milestone 1 --- Design-complete prototype

App shell, onboarding, home, sessions, recap, highlights, settings, demo
data, responsive states.

### Milestone 2 --- Analytics prototype

Rallies, shots, movement, progress, records, metric definitions,
evidence links.

### Milestone 3 --- Social and journey

Partners, pair memory, journey timeline, optional challenges,
feedback/correction UX.

### Milestone 4 --- Advanced mode

Tactical analytics, filters, coach demo, export layouts.

### Milestone 5 --- Backend integration

API client, auth, consent enforcement, real processing status, analytics
data, media access.

### Milestone 6 --- Validation and release hardening

Metric validation, accessibility audit, security review, privacy review,
usability studies, performance and reliability testing.

## 6. Definition of done for a screen

A screen is done only when: - Its purpose and primary action are
clear. - It matches the information architecture. - It has populated,
empty, loading, error, partial, and permission states as relevant. - It
works on desktop and mobile. - All visible controls work. - Data is
sourced from typed fixtures or actual API responses. - Metric
definitions and confidence are accessible. - Privacy and consent are
respected. - Keyboard and screen-reader basics are tested. - At least
one acceptance test covers its primary journey. - No fabricated data is
presented as real.
