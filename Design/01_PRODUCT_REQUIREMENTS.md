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
