# 10 — Engagement, Social and Privacy

**Status:** Behaviour-safe engagement, sharing and privacy specification.
**Depends on:** `00_README_DECISIONS_AND_CONTRACT.md` — especially **D7** (no XP/levels/streaks/leaderboards), **D15** (private by default; analyse ≠ store ≠ share ≠ train), **D16** (every claim opens its evidence), **D17** (every player gets a verified positive moment or an honest "why not"), **D6** (loss is not failure).
**Related:** `03` (consent at upload, invite flow), `04` (permissions, share URLs), `05c` (Together, Share, Settings screens), `07` (`SharePreviewDialog`, `ShareAudiencePicker`, `ConsentLedger`, `NotificationPrefs`), `09` (copy), `11` (consent ledger, share entities).

> **Governing test (Blueprint §11):** every mechanic must have **(1)** a user-value theory, **(2)** a harm test, **(3)** an opt-in path and **(4)** a sporting reason. If it fails any of the four it does not ship. Evidence for gamification is *modest and fades* (a 16-trial meta-analysis found small-to-moderate effects that shrink at follow-up; a badge-and-leaderboard course study found *lower* motivation) — so nothing here is assumed to work; each item is an experiment with a kill criterion (Doc 12).

---

## 1. Principles

1. **Sport first, app second.** A player who watches one Moment, closes the app and has a great Tuesday has received full value. *Successful non-use is legitimate* (v2 principle 12, Blueprint §6).
2. **Return should be pulled by the sport, not pushed by the product.** The reasons to come back are: *the next time I play*, *a Moment I want to show someone*, *a question after a game*. Nothing else is engineered.
3. **Private by default; sharing is a deliberate act with a preview.** Analysing a video does not imply keeping it, sharing it or training on it (D15).
4. **Self-reference before social comparison.** The default baseline is the player's own comparable history (D2/Blueprint §11.2).
5. **No guilt, no scarcity, no shame, no surprise.** No streak loss, no countdowns, no "you're falling behind", no rank-drop alerts, no public weakness reports (Blueprint §13.6).
6. **Correctable and reversible.** Every preference, consent, notification and share can be inspected, changed and revoked in one place.
7. **Humans stay accountable.** The system never infers emotion, motivation, fitness, health, age or ability from video (D15; v2 §7.4).
8. **Every number stays honest.** No celebration is attached to an unverified or low-coverage claim (D5, D16).

---

## 2. Mechanics decision table

Each mechanic considered across the three Design documents **and the user's pasted brief**. Decision codes: **Build** · **Build, optional** · **Test later** · **Do not build**.

### 2.1 Recognition, memory and identity

| Mechanic | Value theory (why it helps) | Harm test (how it could hurt) | Opt-in path | Sporting reason | Decision | Gate / kill criterion |
|---|---|---|---|---|---|---|
| **My Moments** (personal highlight identity — the pasted brief's "signature moments": first successful smash, longest rally, best recovery, favourite partner combination) | Relatedness to one's own sport story; competence from replayable *own* examples (SDT; self-efficacy via credible mastery experiences) | Cherry-picked glory misreads ability; embarrassing clips surface; false "firsts" | Saving is a tap; **nothing is auto-posted anywhere**; fun/bloopers need explicit per-clip approval | Replaying real execution; coach/partner conversation | **Build** (core) | Kill/disable a lens if its false-moment rate (clip mislabelled as the kind it claims) exceeds the agreed threshold (Doc 12 §metrics) |
| **Personal best** (e.g. "your longest rally in a match") | Competence; self-referenced progress; shown with its definition | One lucky rally treated as skill; sets an escalating target | Always visible but quiet; never auto-sets the next target | Concrete reference for "what I've done" | **Build** (scoped definition + comparable matches only) | Never on a first match (baseline). Disable if users read it as a "level" (usability) |
| **Firsts** ("First cross-court net shot *spotted*") | Discovery; autonomy in exploring shots | "Observed" read as "mastered"; **shot labels are Preview** | Optional tab; copy says *spotted*, never *mastered* | Widening repertoire | **Build, optional** — **Preview** until shot classifier validated | Suppress if classifier precision on amateur footage is below the release gate |
| **Personal story / My story** timeline | Identity continuity without a leaderboard | Fabricated milestones to fill a timeline | A tab in Progress; only verified events; player-added notes allowed | Memory | **Build** | Every entry needs a verifiable event or explicit player confirmation (v2 §5.1) |
| **Partnership memory / Pair memory** (pasted brief) | Relatedness; shared achievement without ranking | Blame from uncertain attribution; exposure of a partner who didn't consent | Both partners must accept "Link as partners"; per-clip consent | Doubles is social | **Not yet** (doubles is Not yet) — design now, ship with doubles | Both partners' consent ledgers must allow it; no pair statistic that implies one partner's fault |
| **Awards** (Smash King, Net Ninja, Rally Champion — optional labels from v2 §5.4) | Light fun; named recognition | Only winners/strong players get recognised; hierarchy of "good players" | Off by default; opt-in per player | — | **Test later**, *optional*, never the only recognition (v2) | If displayed, every player can earn at least one non-power award; drop if users report comparison pressure |
| **Badges** | Marks a verified milestone | Badge economy; reward replaces value | Rare; tied to a verified milestone with its definition shown | — | **Build rarely** (a "First" *is* the badge; no separate economy) | Do not add badges that don't represent a verifiable event (Blueprint §11.1) |
| **Points / XP / levels / universal rating** | None that outlasts novelty | Rewards activity, not value; "badminton IQ" claims; ability labelling | — | None | **Do not build** (D7) | — |
| **Daily or weekly streaks** | Habit formation (median ~66 days, wide variation) | Guilt; mismatch with weekly play; punishes injury/travel | If ever tested: opt-in, **weekly or event-based**, forgiving (missing one does not reset), easy to disable | Habit supports regular play only if the player wants it | **Do not build at launch** (D7) — *Test later* only as above | Stop immediately if opt-outs, pressure reports or churn after a miss exceed baseline |
| **Leaderboards** | Social comparison motivates *some* in *some* contexts | Discourages most; public ranking of amateurs; incomparable matches | Opt-in, bounded peer group with explained matching and sample size | — | **Do not build** by default; *Test later* (phase 4) opt-in only | Never default-on; never global; never ranks across incomparable cameras/formats |
| **Loot / random rewards / mystery drops** | None | Casino mechanics; manipulates | — | None | **Do not build** | — |

### 2.2 Challenges and play modes

| Mechanic | Value theory | Harm test | Opt-in path | Sporting reason | Decision | Gate / kill criterion |
|---|---|---|---|---|---|---|
| **Rally Explorer** ("keep a rally alive for 8 shots, then 12 — beat your own best") | Process goal, self-referenced, mastery | Pushes players to play unnaturally / avoid attacking; escalation pressure | Optional card in Explore; dismissible; pauseable | Rally length is observable (Available) | **Build, optional** | Never auto-escalate difficulty after a success (v2 §3.2). Pause challenge if the player dismisses twice |
| **Shot Explorer** ("try three different shots in a session") | Autonomy, novelty | Encourages risky shots in friendly games; relies on **Preview** classification | Optional | Widen repertoire | **Build, optional**, labelled Preview; only counted when classification is reliable | Hide until shot labels pass the release gate |
| **Court Explorer** ("experiment with placement across zones") | Variety of placement | Needs reliable landing — **landing is currently the receiver's feet** (ROADMAP #12) | Optional | Spatial variety | **Test later** — **Not yet** until true landing point exists | Do not show or score without a validated landing estimate |
| **Doubles Duo** ("rally where both partners contribute") | Relatedness | Blame; attribution uncertainty; doubles Not yet | Optional, both partners | Cooperation | **Not yet** | Ship only with doubles + identity validation |
| **Defence Hero** ("difficult return") | Recognises resilience; fairness to the loser | "Difficult" is subjective | Optional | Defence is under-celebrated | **Test later**; needs a defined *difficult-position* rule from geometry | Without a validated rule, do not show |
| **Just Showed Up** ("complete a session you chose to play") | Participation without performance judgement | Becomes a de-facto streak if repeated daily | Quiet recognition; no reminders; no rewards for frequency | Showing up is the sport | **Build, optional, once** (a single First: "First match added") — not a recurring mechanic | If it creates frequency pressure (survey), remove |
| **Personal Best challenge** | Mastery | Escalation | Opt-in | — | Folded into *Personal best*; **no auto next target** | — |
| **Calm Review** ("review later or not at all") | Self-regulation after a loss | None | A first-class choice in the Recap entry: **Quick recap · Deep review · Review later** | Respect emotion without diagnosing it | **Build** | — |

### 2.3 Modes, summaries and notifications

| Mechanic | Value theory | Harm test | Opt-in path | Sporting reason | Decision | Gate / kill criterion |
|---|---|---|---|---|---|---|
| **Relax / Explore / Friendly-competition modes** (pasted brief) | Autonomy: player chooses the experience | Mode becomes identity ("I'm a Relax player"); competitive mode exposes people to ranking | Presets are *shortcuts*, editable per match; friendly competition = opt-in head-to-head only between two consenting players | Different jobs on different days | **Build** as **Presets** Relax / Explore / Improve / Compete (D3); *friendly head-to-head* → **Test later**, doubles/second-account dependent | Presets never labelled as the player's identity (AC-ONB-12) |
| **Personalised weekly recap** (pasted brief) | Reflection; a reason to review once, not daily | Obligation; weekly cadence mismatch with irregular play; pressure after a poor week | **Opt-in**, off by default; sent *only if the player played that week*; one-tap pause | Summarises *their* sessions | **Test later** (digest, Doc 12 X-experiments) | Stop if "digest fatigue" or opt-out rate exceeds baseline; never "you didn't play this week" |
| **Practice Focus** (one editable focus) | Process goals outperform outcome goals (27 studies, heterogeneous) | Generic advice; over-trust; drills from uncertain evidence | Suggested, never forced; accept/edit/ask-coach/decline | Turns a pattern into one controllable experiment | **Build, optional** (Improve preset) | Withhold when evidence is weak (never invent a drill) |
| **Reflection prompt** ("What changed?") | Calibrates reliance; learning | Burden | Single, skippable, no guilt copy | Compare perception to evidence | **Test later** (burden vs benefit A/B) | Drop if it lowers completion |
| **Shared playlists with a coach** | Shared understanding | Evidence becoming surveillance | Athlete-owned, scoped, expiring, revocable | Coaching conversation | **Not yet** (coach role designed, not built) | Never permanent access to future footage |
| **Club challenges / team views** | Group belonging | Low performers disengage; surveillance | Opt-in; tied to participation or learning | Club life | **Test later** (phase 4) | Include disengaging/low-ranked users in evaluation; stop if they leave |
| **Social feed / public profile / public rankings** | — | Public exposure; unconsented participants; bullying | — | — | **Do not build** | — |

---

## 3. The return model

### 3.1 Why a recreational player comes back (hypotheses to validate)

| Pull | What it looks like | What the product provides |
|---|---|---|
| **The next time they play** | A casual player films a game on Saturday; the product matters again the following Saturday | A *quiet* "Resume with one match" and the player's own *user-set* reminder (opt-in). No inferred schedule |
| **A Moment worth showing** | After a great rally someone says "send me that" | Private share link with preview (§5); a Moment ready within minutes |
| **A question after a game** | "Did I really lose most points on serve?" "Was that rally really 14 shots?" | **Ask** (grounded) and the evidence-linked Recap |
| **Curiosity about their own history** | "Have I done that shot before?" | Shot Explorer (*Preview*), My story, Personal bests |
| **Coach/partner conversation** | Review together | Share a Moment with one question (coach role **Not yet**; works with a friend/opponent today) |

### 3.2 The five "not returning" states — distinguish before any outreach (Blueprint §6)

| # | State | How we know (carefully) | What the product does | What it must **NOT** do |
|---|---|---|---|---|
| 1 | **Didn't play** | No new upload; the player has not told us otherwise | **Nothing.** Silence. On next open: "Good to see you." | Send "we miss you"; infer disengagement from inactivity |
| 2 | **Played but didn't record** | Only learnable by *asking lightly* (an optional, one-time, in-product question after a long gap: "Did something get in the way? [No camera] [Too much effort] [Not playing] [Just here for moments]") | Offer the Record guide and a one-tap quick-upload path | Guilt; compulsory survey; push notification |
| 3 | **Recorded but couldn't upload** | `upload_interrupted` / `upload_cancelled` with no completion | In-product banner on next open: "Your upload stopped at 48 %. Resume?" (resumable when built) | Re-prompt repeatedly; show it on other channels |
| 4 | **Got a report without value** | Opened Recap, no Moment saved, `recap_useful: no`, or a correction with no follow-up | Offer: "What would have been more useful? [A better Moment] [Fewer numbers] [More detail] [Something was wrong]" → routes to preset/Fix/feedback | Auto-escalate features; send "improve your game" prompts |
| 5 | **Found value and has no reason to return yet** | Saved a Moment; no further need | **Respect it.** Export / "Keep my moments" light mode counted as *success* | Churn-prevention nudges; discount-pressure after a bad session |

**Rule:** the product never infers a state from inactivity alone. If it asks, the question is optional, one-time, and its answer only changes in-product help (Blueprint §11.4: "ask lightly whether the reason was burden, unreliable data, changed circumstances or having learned enough").

### 3.3 Lapse and exit design

| Situation | Design |
|---|---|
| Returns after weeks | "Resume with one match." History intact; **fresh baseline offered**; no lost-streak, no regression alarm (doc 03 §11.2) |
| Views old info without recording | Allowed; no new data collected |
| Injury / season end / no camera | Pause gracefully (Settings → Pause); no deficiency framing |
| Goal achieved / "learned enough" | Offer export and a light *Keep my moments* mode; counted as success |
| Wants to leave | Export, delete, cancel in **two** clear steps; no guilt screens |
| Subscription decisions (future) | Transparent value; no fear-based upsell after a poor performance |

---

## 4. Notification policy

**Default: nothing.** All notifications are opt-in except *delivering something the player explicitly requested*. Permission (push or email channel) is requested **only** when a notification has a clear reason (D9, Blueprint §11.3).

### 4.1 Allowed triggers

| Trigger | Purpose | Default | Control | Guardrail |
|---|---|---|---|---|
| **Analysis ready** (the player tapped "Tell me when it's ready") | Deliver what was requested | **On for that match only** | Channel chosen at that moment; per-match | No urgency; no repeat; one message |
| **User-set review/practice time** | Enact their own intention | Off | The player sets the time; snooze/disable | No guilt after a miss; never auto-created |
| **Planned practice** (a Focus the player accepted) | Retrieve a chosen focus | Off until they plan one | Explicit opt-in tied to that plan | Don't invent a schedule |
| **Enough comparable evidence to revisit a goal** | Alert to a *supported* change | Off | **Separate** opt-in; explains why it is noteworthy | Never for noise or every metric movement |
| **Coach comment / review request** (future) | Collaboration | Off | Per-coach control; quiet hours | — |
| **Shared moment received / someone left a reply** | Social exchange the player invited | Off | Per-person/per-link | One notification per link per day max |
| **Share link expiring / access revoked on a link I created** | Control | On (account email) | Can disable | Informational only |
| **Pending reflection** | Resume a voluntary task | **In-product only** | Never push | No escalation |
| **Inactivity** | — | **None by default** | — | Ask about pausing only respectfully and only on user request |

### 4.2 Forbidden notifications
"Come back", "You haven't played in X days", streak or rank alerts, "N people viewed your clip", countdowns, "last chance", competitive nudges ("Sam just beat your longest rally"), repeated alerts after dismissal, anything during quiet hours, anything that uses a loss or a poor performance as the hook.

### 4.3 `NotificationPrefs` panel

| Control | Detail |
|---|---|
| Global pause | One switch; "Pause everything for 1 week / until I turn it on" |
| Per-trigger switches | The table above, each with an example of exactly what would be sent |
| Quiet hours | Default 21:30–07:30 local (editable); respected by everything |
| Frequency limit | Max 1 non-requested message per 24 h |
| Digest mode | Group non-urgent into one weekly message **only if the player played that week** |
| Channels | In-app · email · (messaging channels — see §4.4). Push is never requested at onboarding |
| One-tap unsubscribe | In every message; works without signing in |

### 4.4 Messaging channels and weekly digest — **hypothesis for India, validate**
- **Assumption (not a fact):** a large share of recreational players coordinate games and share clips in **WhatsApp-style groups**. This could make **share links** (not notifications) the primary growth channel. **Validate** in interviews and a share-flow prototype (Doc 12) before building any channel integration.
- **Design implications if validated:** (a) *share* sheets must hand off cleanly to the system share intent and generate **safe previews** (§5.7); (b) a messaging-channel notification would need explicit opt-in per channel and each provider's policy compliance; do **not** add a channel to "increase open rate"; (c) the weekly digest, if tested, is plain text + one Moment link, sent only after a week the player played, with a one-tap "stop".
- **Hypotheses H-ENG-3/4** below test digest value and share-link pull.

### 4.5 Copy examples (Doc 09 owns the full set)

| Situation | Use | Never |
|---|---|---|
| Analysis ready | "Your review is ready. Start with the moments you saved whenever you want." | "Your results are waiting! Don't miss out." |
| Shared moment received | "{Name} shared a moment with you." | "{Name} is waiting for your reply." |
| After a break (in-product) | "Welcome back. Resume with one match?" | "You broke your streak." |
| Comparable-trend alert (opt-in) | "You now have 3 comparable matches. Want to look at your rally lengths?" | "You're improving 23 %!" |
| Link expiring | "Your link to 'Sunday rally' expires in 2 days. Extend or let it end." | "Your link is about to expire — act now!" |

---

## 5. The sharing system

**Goal:** make sharing *delightful* for the thing worth sharing and *safe* for everyone in the frame. Sharing is never an engagement lever, never a default, and never a way to expose someone's mistake.

### 5.1 Preconditions (checked before the dialog opens; each failure has a truthful message)

| Check | If it fails |
|---|---|
| Player has an account (not a guest) | "To share safely we need to know it's yours — add an email." |
| "Share selected moments" consent is on | "Sharing is off. Turn it on in Privacy." (one tap, deep-linked) |
| The clip's own sharing state allows it | "This clip is private. Approve it for sharing?" |
| Clip is **Checked** or **Looks right** (not "Worth a look") | "We're not sure about this moment. Check it first, or share anyway as a rough cut." |
| Clip is flagged **fun/blooper** | **Explicit per-clip approval** — copy: "This might be embarrassing for someone. Share it only if everyone in it would be happy." Default: **blocked** until approved |
| Clip contains another identifiable person | See §7 (opponents/bystanders) |

### 5.2 `ShareAudiencePicker`

| Audience | What it creates | Default expiry | Download | Notes |
|---|---|---|---|---|
| **Only me** (default) | Nothing leaves the account | — | n/a | The resting state of everything |
| **One person I played** | Tokenised private link bound to *that link*, not to an identity | 14 days | Off | The invite flow of doc 03 §12 |
| **A few named people** | One link per person (revocable individually) | 14 days | Off | Names are the owner's own labels, never shown to others |
| **A group chat / club** | One link with a **visible warning**: "Anyone with this link can view it until it expires" | 7 days | Off | Not equivalent to private; explained once |
| **Public** | **Not offered** in the prototype (D15; out of scope — no public feed) | — | — | If ever added: separate, deliberate, re-confirmed |

### 5.3 `SharePreviewDialog` — what the player sees *before* anything is created (Blueprint §8.12)

```
┌──────────────────────────────────────┐
│ Share this moment                    │
│ ┌──────── what they'll see ───────┐  │
│ │ ▶ A 12-shot rally   (preview)   │  │
│ └─────────────────────────────────┘  │
│ Includes                             │
│  ✓ The 14-second clip                │
│  ✓ Your nickname: Alex   [Hide]      │
│  ☐ Score                  [Include]  │
│  ☐ Match name / date      [Include]  │
│  ✗ Your stats, other matches, history│
│ Who                                  │
│  ( ) Just me  (•) One person  ( ) A  │
│  few people  ( ) A group             │
│ Link lasts   [ 14 days ▾ ]           │
│ Download     [ Off ▾ ]               │
│ People in this clip                  │
│  You · Opponent  (ask them first?)   │
│                                      │
│ ⓘ Once someone has watched or saved  │
│   it, we can't take it back from     │
│   their device. You can stop the link│
│   any time.                          │
│ [ Create private link ]  Cancel      │
└──────────────────────────────────────┘
```

| Rule | Detail |
|---|---|
| **Exactly what is included** | Footage, **identifiable people and names**, recipients, duration, whether download is allowed — all shown; **hidden analytics are stripped by default** |
| **Strip options** | Hide score · Hide nicknames · Hide match name/date · Face/bystander blur (where feasible; labelled "when available" until validated) |
| **Opponent/teammate prompts** | "The other player is in this clip. Have you told them?" with a one-tap *copy a note* ("I'm sharing a rally from our game — OK?") — not a verification, a prompt (§7) |
| **Revocation language** | Honest: "You can stop the link any time. We can't recall copies already downloaded or screenshotted." |
| **Success state** | Created link with **Copy** and **Share via…**; truthful ("Link created. Only people with this link can watch it until 28 Jun.") — never displays success unless the server returned it |
| **Demo/Sample** | Disabled with "This is a sample — try it with your own video" |

### 5.4 `InviteLink` management (Privacy Centre and Moment detail)

| Column | Detail |
|---|---|
| What | Moment/match title |
| Audience | One person / named / group |
| Created / expires | Dates in the viewer's locale |
| Download allowed | Yes/No |
| Actions | **Stop sharing** (revoke immediately) · **Extend** · **Copy** |
| Views | **Not shown by default** (no vanity counts). Optional "Was this opened?" yes/no per link for the owner who asks |

### 5.5 What the *recipient* gets (view-only first)
View-only clip; "Are you in this? That's me / Not me"; **Report / Remove me** in one tap (§7.3); "Make your own moments" → guest start. No account needed to view; no tracking pixel, no recipient identity captured unless they choose to claim "That's me"; Open Graph preview is generic (doc 04 §13).

### 5.6 What cannot be recalled after export (disclosed at export and share time)
Downloaded `clip.mp4`, PDF reports, CSV/JSONL exports, screenshots, copies saved by recipients, and link previews cached by third-party apps. The UI says so at the moment of export (`DataExportRequest`, Download button tooltip) — *"A hidden name or map in one product does not protect every downstream copy"* (Blueprint §13.3, Strava lesson).

### 5.7 Safe previews in messaging apps
Open Graph/Twitter cards for `/s/$token`: generic title ("A moment from a Rally match"), no player names, **no thumbnail by default** (owner may choose "Show a preview image"), `noindex, nofollow`, no description derived from the clip. Without this, chat apps will render the exact detail the player chose to keep private. *(Validate how target messaging apps cache previews.)*

### 5.8 Acceptance
- **AC-ENG-1** No share link, clip or analysis is public by default or exists in a public listing.
- **AC-ENG-2** `SharePreviewDialog` always lists footage, names, recipients and expiry before creating a link; hidden analytics are stripped by default.
- **AC-ENG-3** A clip flagged fun/blooper cannot be shared without per-clip explicit approval.
- **AC-ENG-4** Revoking a link makes it fail on the next request; no cached video is served.
- **AC-ENG-5** The dialog states what cannot be recalled after export/share; the claim "only you can see this" is never shown for group links.
- **AC-ENG-6** Share previews in chat apps contain no personal names and no frame thumbnail by default.

---

## 6. Social comparison, pairs and clubs

### 6.1 Comparison rules (Blueprint §11.2; v2 §3.8)

| Rule | Detail |
|---|---|
| **Default reference = the player's own comparable history** | "Compared with your last 3 comparable matches (same camera setup, singles)." A match with different geometry or discipline is **"Not directly comparable"** with the reason |
| **Reference picker** (later) | *My past self (default) · A similar peer group · An expert example · Nothing* |
| **Peer groups are opt-in and bounded** | Both sides consent; the reference group, metric definition and sample size are shown; **never** a global ranking; never imply an unadjusted ranking measures skill |
| **Never surface others' weaknesses** | Upward/downward comparison is the player's choice; opponents' stats are never shown to the player without the opponent's consent |
| **Show a learning question beside any gap** | "What does this player do differently in the same situation?" — only for an opted-in comparison |
| **Hide anytime** | A single "Hide comparisons" setting |

### 6.2 Sequencing (Blueprint §11.5: private first)

| Order | Feature | Depends on | Status |
|---|---|---|---|
| 1 | **Private share** to a person I played (view-only link) | Account, consent ledger, share entity | Build (prototype) |
| 2 | **Private collections / My Moments** | — | Build |
| 3 | **Coach/partner private review** with *one question* | Coach role, annotations, audit log | **Not yet** |
| 4 | **Pair memory** (consent from both) | Doubles, identity validation, pairing flow | **Not yet** |
| 5 | **Opt-in bounded peer cohorts** | Enough comparable users, matching rule, ethics review | **Test later** |
| 6 | **Club challenges** tied to participation or learning | Club entity, moderation, measured harm | **Test later** (phase 4) |
| ✗ | Public feed, public rankings, public weakness reports | — | **Do not build** |

### 6.3 Pair memory rules (when it exists)
Both partners accept an explicit "Link as partners" prompt; each keeps their **own** consent for each clip; the pair view shows *pair-level* facts ("12-shot rally, both partners contributed") and **never** one partner's error; pair stats appear only when sample sizes support comparison (v1 §27); either partner can **unlink** and remove their appearance; unlinking removes shared pair memory for both without deleting each person's private records.

### 6.4 Club considerations
Clubs can both support belonging and constrain (in-group effects). Study real clubs, not isolated users. A club feature must (a) default to participation/learning, not winning, (b) be moderated, (c) allow any member to opt out without social cost, (d) never expose a member's stats to others without that member's per-stat consent.

---

## 7. People in the frame: opponents, bystanders and venue rules

The player is the data subject who *uploads*; **other people appear without having chosen to be analysed.** This section governs them.

### 7.1 Principles
- **Consent to analyse is the uploader's; consent to share a person's image is not theirs to give for others.** The product therefore never turns an opponent into a shareable subject without a prompt and a removal path.
- The opponent is, by default, analysed as **"Opponent"** — a track — **not identified by name or face**. We do not match faces and we do **not** store face embeddings or biometric identity features (Blueprint §13.3; v2 §9.2).
- **Opponent statistics are never shown as a profile** and never accumulate across matches or accounts (no public opponent dossiers, Blueprint §1.5).

### 7.2 What the uploader sees and agrees to
At upload (doc 03 §6.2) and at share time: "Everyone in the frame should know you're filming, and the venue should allow it." Not a checkbox substituting for a policy; a **specific prompt** and a copyable note to send ("Hey — I'm filming our game to review my own play. OK?").

### 7.3 Removal and requests (one tap)

| Who | How | What happens |
|---|---|---|
| Person on a shared link | **Remove me** on `/s/$token` | Clip becomes **blurred/blocked for that recipient's report** and the owner is notified "Someone in this clip asked to be removed"; the owner decides to re-cut, blur or delete the share. The link is paused pending the owner's decision for removal requests flagged *"this is me"* |
| Bystander not on a link | **Report an issue → "I appear in someone's video"** form; no account required | Escalated per policy; platform may disable the share and remove the person from derived clips under its control |
| Opponent who is also a user | Pair/partner link flow (when available) | Their ledger controls what is shown of them |

### 7.4 Bystander handling
More than two people on court → doubles/bystander message (doc 03 §7.6). Non-participants detected near the court are **excluded from analysis outputs** (track whitelist, **G-ONB-5**) and **excluded from shared clips by default**; blur options where feasible (*"when available"* until validated). Never name or label them.

### 7.5 Venue rules
Some venues prohibit filming or require staff permission. The Record guide and consent step state: "Check the venue allows filming." The product does not attempt to enforce it but never **hides** it; no recording in changing rooms or sensitive locations (Blueprint §13.4).

### 7.6 Minors
**Adult-only pilot (D15).** An unobtrusive "Rally is for people 18 and over" at consent; no DOB form. If a minor appears in a frame (e.g. at an academy), the uploader attests they have appropriate permission; shareable output blurs or suppresses non-consenting participants by default. A youth product requires a **separate reviewed workflow** (checklist §8.5) before it exists.

---

## 8. Consent model

### 8.1 Four permissions + one separate opt-in (D15; Blueprint §13.2; v2 §9.1)

| # | Permission | What it allows | Default | Required to use the product |
|---|---|---|---|---|
| 1 | **Analyse** | Process this video to find rallies, shots, moments | On | **Yes** |
| 2 | **Keep** | Store the video privately so Moments can play | On | Yes (to watch clips); can choose "delete after analysis" |
| 3 | **Save to my history** | Keep derived stats for Progress/Journey/Records | **Off** | No |
| 4 | **Share selected moments** | Allow creating share links per clip | **Off** | No |
| 5 | **Help improve the product** (model improvement) | Use footage or derived data to improve models | **Off** — and **separate**, never bundled | No |

Consent to one purpose is **not** consent to another. Every consent record stores: `purpose`, `status`, `captured_at`, `policy_version`, `revoked_at`, `scope` (global or per match), and `surface` (where it was changed) — v1 consent record entity.

### 8.2 Scope: global default vs per-match
First-run choices become **defaults** that pre-fill the next upload as "Same choices as last time — Change". A revoked choice is **never** re-enabled silently.

### 8.3 Revocation — what changes now vs later (stated in the UI next to each toggle)

| Revoking… | Immediately | Later / job | Not affected |
|---|---|---|---|
| **Analyse** (future matches) | No new analysis | — | Existing analysed matches (delete them separately) |
| **Keep** | New uploads are deleted after analysis; existing Moments keep playing until the player chooses "Delete videos" | Deletion job removes stored video, clips, thumbnails, HLS/proxy, sprites (status shown) | Derived stats (separate toggle) |
| **Save to my history** | New matches excluded from Progress/Journey; existing matches stay unless "Remove from history" | Recompute personal bests/progress without them | The matches themselves |
| **Share selected moments** | All share links are **paused/revoked**; the Share button disables with a reason | — | Copies already downloaded |
| **Improve** | Excluded from future training sets | Removal from *pending* datasets; **already-trained models cannot be un-trained** (stated honestly) | Everything else |

### 8.4 Bundling prohibitions
- No "Accept all" button on the consent step.
- No pre-ticked optional card.
- Model improvement is **never** a condition of service.
- A player may use the product with **only** Analyse + Keep on and nothing else.

### 8.5 Safeguarding checklist (adult-only pilot and any future youth product — Blueprint §13.4)
- [ ] Adult-only pilot with an age line, no date-of-birth collection.
- [ ] No recording in changing rooms/sensitive locations stated at consent.
- [ ] No sharing of minors' footage; non-consenting participants suppressed.
- [ ] **Before any youth workflow:** guardian and participant permissions; club/school authorisation; authorised devices only; accommodation if someone doesn't consent; restricted sharing; identity minimisation; retention rules; incident handling; legal review per jurisdiction.

### 8.6 Legal note
Consent is not the only legal basis for every activity, and rules differ by jurisdiction (data protection, children, biometric data, recording laws). **Obtain jurisdiction-specific legal advice** before launch; this document fixes product behaviour, not legal conclusions.

---

## 9. Privacy Centre (`/settings/privacy`, `/settings/data`)

### 9.1 Screen contents (top → bottom)

```
┌──────────────────────────────────────┐
│ Privacy                              │
│ Four choices. You're in control.     │
│                                      │
│ Your choices                         │
│ ┌ Analyse my videos        ON   ⓘ ┐  │
│ ┌ Keep my videos           ON   ⓘ ┐  │
│ ┌ Save results to history  OFF  ⓘ ┐  │
│ ┌ Share selected moments   OFF  ⓘ ┐  │
│ ┌ Help improve the product OFF  ⓘ ┐  │   ← separate section
│                                      │
│ Active links (2)             Manage ▸│
│ Who has seen what                    │
│ My data                              │
│  Export my data  ·  Delete my data   │
│ History of my choices (ledger)  ▸    │
│ Read the full privacy policy  ▸      │
└──────────────────────────────────────┘
```

### 9.2 `ConsentLedger`

| Purpose | Status | Changed | Where | Policy version | Effect if turned off |
|---|---|---|---|---|---|
| Analyse | On | 12 Jun 2026 | Upload | v1.0 | See §8.3 |
| Keep video | On | 12 Jun 2026 | Upload | v1.0 | … |
| Save to history | Off | 12 Jun 2026 | Upload | v1.0 | … |
| Share | Off | 12 Jun 2026 | Upload | v1.0 | … |
| Improve | Off | 12 Jun 2026 | Upload | v1.0 | … |

Append-only: changes add a row; nothing is overwritten (auditable). Per-match overrides appear in an expandable section.

### 9.3 Retention (stated before accepting footage; Blueprint §13.3)

| Data | Default retention | Controls |
|---|---|---|
| Original video | Until the player deletes it, or **auto-delete after N days** (player-selectable; default to be decided with legal — *never indefinite by default*) | "Delete after analysis" at upload; per-match delete |
| Prepared proxy/HLS/sprites/clips | Tied to the original; deleted with it | — |
| Derived events/stats | While "save to my history" is on, else deleted with the match | Per-match "remove from history" |
| Track data (positions) | Tied to the match | Deleted with the match |
| Corrections/labels | Tied to the match; included in export | — |
| Reports/exports generated | Ephemeral download; not retained server-side after N days | — |
| Share links | Until expiry or revoke | Revoke any time |
| Telemetry | Minimised, no names/frames/file names; retention per policy | Opt-out of non-essential |
| Backups/logs | Disclosed with explicit time bounds | Honest limit stated |
| Guest data | Auto-deletes after the stated guest window if not claimed | — |

### 9.4 Export flow (`DataExportRequest`)
1. Player taps **Export my data**; choose scope: *everything* / a match / only Moments.
2. Choose contents: derived summaries (`summary.json`, `rallies.csv`, `events.jsonl`), the PDF report, the videos (large; "request download").
3. Show the **honest limit** before download: "Once exported, we can't control copies."
4. Status shown (`requested → preparing → ready → expires`); email only if the player opted in.
Prototype rule: until the backend exists, the action is labelled **"Request simulated"** (v1 §32).

### 9.5 Delete flow (`DeleteConfirmDialog`)
Two-step, plainly worded, separated by scope:

| Scope | What is removed | Confirmation |
|---|---|---|
| **A match** | Video, prepared proxy/HLS/sprites, clips and thumbnails, tracks, events, corrections, derived stats, its share links (immediately revoked) | Type nothing; one clear confirm ("Delete match") with the exact list |
| **All my videos** | All originals and prepared media; derived stats remain if "history" is on | Confirm + list |
| **My data (account)** | Everything above + profile, preferences, consent ledger entries older than the legal minimum, history, journey, pair links (the partner keeps their own private records) | Re-authenticate; 7-day grace period (hypothesis) |
| **A share link** | The link only | Immediate |

**What deletion removes:** the video and prepared media; derived clips, thumbnails and posters; track data; events and corrections; derived stats and records; embeddings or learned indexes **under the platform's control**; generated exports under the platform's control; share links.
**Honest limits** (shown, not hidden): downloaded exports and screenshots; copies saved by recipients; third-party link-preview caches; **backups and logs for their disclosed retention window**; models already trained on opted-in data cannot be un-trained.
**Demo/Sample data:** a separate **Clear sample data** action; never confused with real deletion.

### 9.6 Other panels
`/settings/profile` (nickname, optional display name, avatar only if supported; no sensitive data); `/preferences` (Preset, Purpose, Depth defaults, recap length, challenge suggestions on/off, social memories on/off — all off or neutral by default); `/notifications` (§4.3); `/accessibility` (§12); *Metric definitions* and *Corrections history* (with affected findings and model versions) as in Blueprint §7.15.

### 9.7 Acceptance
- **AC-ENG-7** The five permissions are separate toggles with plain consequences; the improvement toggle is in its own section and off by default.
- **AC-ENG-8** The ledger is append-only and shows purpose, status, date, surface and policy version.
- **AC-ENG-9** Revoking sharing blocks future share attempts immediately and pauses existing links.
- **AC-ENG-10** Delete names exactly what is removed and what cannot be; destructive actions require confirmation.
- **AC-ENG-11** Demo/prototype data and actions are labelled "Request simulated"/"Demo action"; no simulated action claims real deletion or export.

---

## 10. Data minimisation

| Principle | Implementation |
|---|---|
| **Collect only what the next screen uses** | Onboarding has no age, gender, phone, photo, skill rating or health questions |
| **No biometric identity** | No face recognition or face embeddings; "Opponent" is a track; player identity is *tap-to-claim* per match |
| **No raw video in logs/telemetry** | Telemetry carries event names and coarse context only (doc 03 §16.1) |
| **Separate stores** | Raw footage · derived events/metrics · shared clips are different stores with different access and retention (v2 §9.2) |
| **Thumbnails** | Court-replay silhouette by default; real frames inside the private player only |
| **Minimise names** | Nicknames; opponent labels private to the owner |
| **Server-side enforcement** | Object-level access on every session, clip and share route; signed expiring media URLs; rate-limited uploads, processing and sharing; no IDOR; secure media defaults (v1 §8) |
| **Encrypt** | In transit and at rest; audit sensitive access; coach access (future) is logged |
| **Cache hygiene** | Cache keys include user/session scope; never serve one user's private video from a shared cache (v1 §7) |
| **Do not use health/demographic data to manipulate** | No persuasion targeting vulnerable moments (v2 §7.4) |

---

## 11. Harm register

Each row: **harm → who → mitigation (design) → detection metric → kill criterion**. A feature is delayed if the team cannot explain what happens when its detection is wrong (v2 §9.3).

| # | Harm | Who | Mitigation (design) | Detection | Kill / rollback criterion |
|---|---|---|---|---|---|
| H1 | **Shame / embarrassment** from seeing oneself or a mistake highlighted | New/returning players | Private by default; user-selected clips; observation language, clip first; no "weakness" card forced; fun clips opt-in per clip; loss path = *Quick recap · Deep review · Review later* | In-product "this felt…" optional chip; interview probes; `harm_signal` events; share-removal rate | Any feature with shame reports above the pre-agreed threshold is disabled and redesigned |
| H2 | **Unwanted exposure** of the player or others | Opponents, bystanders, minors | Four separated permissions; share preview; strip options; removal in one tap; adult-only pilot; bystander suppression; safe link previews | Removal requests, privacy complaints, blocked share attempts, consent-comprehension tests | Any public/default exposure incident → stop sharing launch; zero tolerance target |
| H3 | **Overtraining / playing through pain** | Anyone; older players | No load/readiness/injury claims; no calories; no "play more" nudges; self-reported energy only; no escalation after discomfort; no streak | Support/feedback terms ("pain", "injured"), reminder-dismissal patterns | Disable any activity-related surface that correlates with harm reports |
| H4 | **False praise** (confident wrong highlight, false PB/First) | All; erodes trust | Evidence-gated: verified events only; coverage + `CheckChip` visible; no PB on first match; "Preview" label on shot-level; abstain when unsure | **False-highlight and false-record rate** (v1 KPI), correction rate, seeded-error detection | Exceeding the false-claim threshold → downgrade to Preview/hide that lens |
| H5 | **Unhealthy comparison** | Beginners; lower-ranked | Self-reference default; opt-in bounded peers only; no leaderboards; never show others' weaknesses | Comparison-opt-out rate, qualitative pressure reports | Any comparison feature with net-negative well-being → remove; include low-ranked users in evaluation |
| H6 | **Identity errors** (wrong player attributed) | All | "Pick yourself" per match; swap/fix; nothing attributed until "me" chosen; identity-flip detection → "Worth a look" and exclusion from "you" metrics | Switch rate after analysis, `pick_yourself_switched`, identity disputes unresolved | Unresolved-identity rate above threshold → block personal bests |
| H7 | **Privacy loss via downstream copies** (exports, previews, screenshots) | Owners and people in the frame | Honest "cannot be recalled" copy; generic OG previews; download off by default; short expiries; watermark-optional on exports | Complaints, incident reports | Disable downloads/exports if incidents exceed threshold |
| H8 | **Over-reliance on automated claims** (amateurs trust device numbers more than elite athletes do) | Amateurs | Simplify explanation, never hide uncertainty; evidence one tap away; correction easy; seeded-error tests | Teach-back accuracy; correction rate; trust calibration (accept correct, question wrong) | Features that raise trust without raising correct-rejection → redesign |
| H9 | **Guilt / pressure from engagement** | Irregular players | No streaks, no inactivity notices, quiet hours, global pause, *Calm Review* | Opt-out rate, pressure survey, post-miss churn | Any engagement experiment that raises engagement but worsens pressure/understanding/privacy is **rejected** (Blueprint §16.3) |
| H10 | **Exclusion** (older/adaptive/low-tech players) | Players with varied ability | Plain language, large targets, captions, reduced motion, no age assumptions; test with diverse participants | Task completion/error rates across access needs | Fix before launch; not a post-launch nicety |
| H11 | **Doubles/attribution blame** | Pairs | Pair facts only; describe observation, not intent; "Not yet" until validated | Pair complaints; disputed attribution | Don't ship pair stats that imply fault |
| H12 | **Data hoarding by default** | All | Auto-delete options, deletion honesty, guest auto-expiry, no indefinite retention by default | Retention audit | Fail release if indefinite default exists |

---

## 12. Inclusive design

| Principle | Design response |
|---|---|
| **Age is not a proxy for ability or motivation** (cross-cultural older-adult studies show varied motives — health, stress reduction, recognition, social) | Never infer age, skill, fitness, health or disability from appearance or behaviour; Preset is the player's choice; no "senior mode" stereotypes |
| **Older players** | Larger text option, high contrast, generous targets, plain language, no required gestures; social features gentle; do not gate recognition behind advanced skill; access to facilities is a real barrier, so the product does not assume a tripod, premium phone or smartwatch |
| **Beginners** | "Your first match is your baseline"; observation language; no jargon (definitions on tap); recognition independent of winning; no embarrassment-prone defaults |
| **Adaptive/para players** | The pipeline was trained on a specific movement context — **do not assume it generalises**; mark analysis as **Preview** for adaptive footage until validated; include adaptive players in research; allow turning off metrics that don't apply; no "normal movement" comparisons |
| **Low-tech confidence** | One primary action per card; undo everywhere; no timed interactions; consistent patterns |
| **Language and locale** | Externalised strings, expansion room, non-idiomatic claims, native-player validation (doc 03 §15) |
| **Sensory** | Captions or text descriptions for key video events; no flashing; reduced motion respected; no sound-only alerts; haptics optional |
| **Motor** | Keyboard operation; large drag handles with arrow-key alternatives; no precision gestures required; shortcuts can be disabled |
| **Cognitive load** | Progressive disclosure (Summary → Evidence → Workspace); one priority per screen; plain definitions |
| **Bandwidth/devices** | Data-saver; low-res previews labelled as preview; offline reading |
| **Compliance target** | WCAG 2.2 AA with manual and assistive-technology testing (an automated scan alone is not conformance, Blueprint §13.1) |

---

## 13. Wellbeing guardrails

| Rule | Implementation |
|---|---|
| **No playing-through-pain messaging** | No copy that encourages continuing when tired/sore; if a player reports discomfort or asks for fewer prompts, **no activity escalation** and prompts reduce (v2 §3.9) |
| **No medical or fitness claims from video** | **No calories, VO₂, heart-rate zones, fatigue, readiness, injury risk, "fitness score"** derived from video alone (D10, 00 §7: *Activity/fitness estimates: Not yet — and never from video alone*) |
| **Active play time is labelled for what it is** | "Time the shuttle was in play" (sum of segmented rally durations) — **not** time on court, exercise time or effort (match analytics definition) |
| **Self-reported only** | Energy, tiredness, enjoyment, discomfort are **player-entered and optional**, stored as such, never inferred |
| **Distance and speed** | **Not yet**: ungated foot jitter inflates metres (ROADMAP #7); show relative movement only, labelled |
| **Warm-up** | General, optional, age-neutral warm-up education, not personalised by inferred attributes; never prescriptive exercise based on video analytics |
| **Celebrate sustainable activity, not exhaustion** | Recognition for showing up and enjoyment, not volume; no recommendation to play more |
| **Emotions** | Never auto-label frustrated/anxious/confident from posture, expression, loss or celebration; ask neutral optional questions only |
| **After a loss** | Same choices as after a win; the match result is separate from learning value; no consolation or celebratory animation tied to the outcome (D6) |
| **Reminders** | No reminders by default; user-set only; no shame after a miss; "Pause all" always present |
| **Handling disclosures** | If a player writes about injury/distress in free text (feedback/Ask), the UI replies neutrally and points to appropriate professional help; it does not give medical advice (Ask is grounded in match data only) |

---

## 14. Experiments and measures for this domain

| ID | Hypothesis | Comparison | Primary outcome | Guardrail |
|---|---|---|---|---|
| **H-ENG-1** | A short Moment-first recap produces more voluntary return than a metric-heavy report | Moment-first vs stats-first | Voluntary 7- and 28-day return; recap usefulness | Comprehension, pressure |
| **H-ENG-2** | Optional challenges increase return **without** guilt | Opt-in challenge vs none | Participation + enjoyment | Dismissals, pressure reports, negative feedback |
| **H-ENG-3** | An opt-in weekly digest (only after weeks played) adds value vs none | Digest vs none | Meaningful return (review/save), opt-out rate | Digest fatigue, pressure |
| **H-ENG-4** *(India hypothesis)* | Share links are a stronger pull than notifications | Share-flow prototype vs notification-only | Approved shares; new guest starts from links | Privacy comfort, removal requests |
| **H-ENG-5** | Private individual Moments vs consent-based shared Moments | Private vs shared | Perceived value, privacy comfort | Removals, complaints |
| **H-ENG-6** | "Resume with one match" beats progress-loss framing | Neutral vs loss | Return to meaningful action | Guilt/pressure |
| **H-ENG-7** | Showing a "can't be recalled" statement at share time reduces regret without reducing sharing | With vs without | Share completion + post-share regret | Over-friction |
| **H-ENG-8** | A reflection prompt improves discrimination of supported vs unsupported findings | Prompt vs none | Teach-back discrimination | Burden |

Method: appropriate randomisation, pre-registered primary outcomes where practical, cluster-aware for clubs/coaches, enough follow-up to separate novelty from sustained value, and **correlation is never presented as causation** (Blueprint §14.4). Stop any experiment that raises engagement while worsening understanding, pressure or privacy.

### 14.1 KPI families (never one blended score; Blueprint §14.1, v1 §4)
- **Value:** % of matches where the player saves a Moment or correctly states a finding.
- **Trust:** event accuracy, identity errors, correction rate, **false-highlight and false-record rate**.
- **Return:** voluntary 7- and 28-day return, sessions per active player (opportunity-adjusted).
- **Social:** approved shares, shared Moments viewed, removal requests, privacy complaints (target zero public exposure).
- **Wellbeing/guardrails:** pressure/shame reports, opt-out and pause rates, notification fatigue.
- **Do not optimise** daily active use, time in app, badges issued or notification open rate as standalone goals.

---

## 15. Acceptance criteria (domain summary)

| ID | Criterion |
|---|---|
| AC-ENG-1…6 | Sharing: never public by default; full preview; fun clips need approval; revocation works; honest recall limits; safe previews |
| AC-ENG-7…11 | Privacy Centre: five separate permissions; append-only ledger; revocation effects; precise delete; simulated actions labelled |
| AC-ENG-12 | No streak, level, XP, leaderboard, loot or inactivity notice exists in the product (D7) |
| AC-ENG-13 | All notification triggers are opt-in except requested deliveries; global pause and quiet hours work; one-tap unsubscribe works unauthenticated |
| AC-ENG-14 | No notification is sent for inactivity or after a poor performance |
| AC-ENG-15 | Opponent/bystander names, faces and statistics are never stored as profiles or shown without that person's consent |
| AC-ENG-16 | "Remove me" is one tap for any person on a shared link and reaches the owner |
| AC-ENG-17 | No calorie, fitness, readiness, injury or emotion claim is derived from video anywhere |
| AC-ENG-18 | No comparison to others appears unless the player chose it, with reference group and sample size shown |
| AC-ENG-19 | Every harm-register row has an owner, a detection metric and a kill criterion before its feature ships |
| AC-ENG-20 | The product remains fully usable with only Analyse + Keep enabled |
