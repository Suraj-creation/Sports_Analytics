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
