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
