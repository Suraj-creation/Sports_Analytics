# 09 — Copy and Voice

**Status:** Build spec for every string a player reads. Decisions cited as **D#** (file 00). Components named per file 07; tokens per file 08.
**Governing principle:** the words are part of the evidence layer. They describe *what the footage shows*, never what the player *is*; they are as certain as the data and no more; and they never pressure.

Copy ids (`onb.value.headline`) are the i18n keys. Strings in `{braces}` are slots filled from typed data — a string whose slot has no value **must not render** (the component falls back or hides the block).

---

## 1. Voice principles

### 1.1 The voice

**A friend who filmed your game, watched it with you, and only says what they can show you.** Encouraging, plain, grounded, never patronising.

| Principle | Means | Example (good → bad) |
|---|---|---|
| **Plain** | Everyday words; short sentences; one idea each. Reading level ≈ grade 6–8 | "You kept this rally going for 12 shots." → "Sustained rally duration exceeded your baseline." |
| **Grounded** | Every factual clause is true of *this* footage and links to it ("Watch this") | "We found 14 rallies." → "You played brilliantly." |
| **Specific** | Names the moment, the count and the denominator | "6 of 9 long rallies" → "often" |
| **Task, not trait** | Describe a *situation* in the video, not the person | "These rallies ended after a short return." → "You're weak at defence." |
| **Observation before interpretation** | Fact first, meaning second and conditional | "Several rallies ended at the net. That may mean…" → "You lose at the net because…" |
| **Encouraging without inflating** | Praise only verified, specific things; no praise for results | "A new personal best: 14 shots." → "Amazing! You're becoming elite!" |
| **Never patronising** | No baby talk, no fake cheer, no gamer slang | "Here's a moment worth replaying." → "Woohoo, awesome job champ!!" |
| **Honest about limits** | "We couldn't tell" is a normal sentence | "We couldn't name every shot in this video." → silence, or a guess |
| **Calm** | No urgency, no exclamation marks except in a user-chosen fun context | "Your recap is ready." → "Don't miss out!" |
| **Player in control** | Options, not orders: "If it helps…", "You could…" | "If it helps: try one lift to the back." → "You must practise lifts." |

### 1.2 The four epistemic layers (always verbally distinct)

From Blueprint §9. A sentence belongs to exactly one layer, and the UI separates layers visually (`InsightCard` blocks).

| Layer | What it is | Signal words | Example |
|---|---|---|---|
| **Measurement** | A recorded or computed quantity under a stated definition | counts, "we followed", "n of m" | "This recap covers 31 of 36 rallies." |
| **Model classification** | An algorithm's label, which can be wrong | "classified as", "looks like", "we think" | "These shots look like cross-court net shots." |
| **Interpretation** | A possible meaning of a pattern | may, might, could, "one reading is" | "This may be leaving you fewer options at the net." |
| **Recommendation** | A proposed action, conditional on the player's goal | "If it helps", "you could", "one idea" | "If it helps: try a lift to the back corner next game." |

**Rules**
- Never cause from description: "associated with", "appeared alongside", "changed after" — **never** "because", "caused", "led to" (unless a `hypothesis` claim explicitly shows alternatives).
- A lost rally after a shot does not show the shot caused it. A shorter longest rally does not show the player got worse.
- Layers are never merged into one sentence ("You hit weak lifts so you lost" is banned).

### 1.3 Person and perspective

- Second person ("you") is the default; `me` (from `PickYourself`) is the anchor (D8). The opponent is a **nickname or "the other player"**, never "P2".
- "We" is the system, used sparingly and only for what *the analysis* did ("We followed 31 rallies"). Never "we think you…".
- The system never says "I".

---

## 2. Tone setting — Direct · Balanced · Coach-guided

The player chooses a tone (default **Balanced**). Tone changes **wording and ordering only**; evidence, limits and facts are identical (Blueprint §9.3). "Direct" is not "harsh"; "Coach-guided" is not "bossy".

| Tone | Character | Ordering |
|---|---|---|
| **Direct** | short, plain, no softeners; limits stated flatly | finding → evidence |
| **Balanced** (default) | warm, conditional, one soft opener | story → finding → evidence → option |
| **Coach-guided** | asks a question first; invites reflection; offers one idea | question → clip → finding → idea |

**The same sentence in all three tones (12 situations)**

| # | Situation | Direct | Balanced | Coach-guided |
|---|---|---|---|---|
| 1 | Longest rally | "Longest rally: 14 shots." | "You kept this rally going for 14 shots — your longest in a match so far." | "Watch how this rally built. What helped you keep it alive for 14 shots?" |
| 2 | A pattern to look at | "6 of 9 long rallies ended after a short return." | "In 6 of 9 long rallies we could follow, the rally ended after a short return. Worth a look?" | "Before you read on — what do you notice at the end of these 3 rallies?" |
| 3 | Strength | "Strength: you returned 7 of 9 deep clears." | "You returned 7 of 9 deep clears we could follow. That's a solid part of your game." | "Where did you feel steady today? Here's one place it showed: 7 of 9 deep clears." |
| 4 | Low evidence | "Too few shots to say." | "We don't have enough examples yet to say anything about this." | "There's too little here to draw a conclusion. Want to look at the clips anyway?" |
| 5 | Preview shot names | "Shot names are a preview." | "Shot names are a preview — they can be wrong, so tap a rally to check." | "Shot names are still a preview. Does this one match what you remember?" |
| 6 | After a loss (checked score only) | "The long rally is ready to watch." | "Here is a rally you might want to keep. The score is in Match story if you want it." | "How did that rally feel? Watch it whenever you want, or leave the recap here." |
| 7 | Personal best | "New personal best: 14 shots." | "A new personal best — 14 shots, up from 11." | "You beat your own 11-shot record. What was different this time?" |
| 8 | First | "First spotted: cross-court net shot." | "We spotted a cross-court net shot for the first time. Take a look and tell us if it's right." | "Is this your first cross-court net shot? Watch it and tell us." |
| 9 | Fix prompt | "Check this rally's winner." | "Quick check: is this who won the rally?" | "Does the winner here match what you remember?" |
| 10 | Return after a break | "Last match: 3 weeks ago. Add one to start fresh." | "Good to see you. Add a match whenever you like — we'll start a fresh comparison." | "Welcome back. Want to start with one match, just to see where you are now?" |
| 11 | Partial analysis | "31 of 36 rallies analysed." | "We followed 31 of 36 rallies. The rest weren't visible to us." | "We could follow most of this match. Which part do you most want to look at?" |
| 12 | No improvement detected | "No clear change across 4 matches." | "Across 4 matches like this, we can't see a clear change yet." | "Nothing stands out across these 4 matches. Is this still the thing you want to work on?" |

**Tone rules:** never "Direct" = rude ("Your defence is bad" is banned in all tones). Coach-guided questions are always **skippable** and never block content. The tone setting never changes whether a limit is shown.

---

## 3. Claim templates

Every displayed claim is generated from a typed `Claim` (file 07 §3.1). Templates fill slots from data; an LLM may **paraphrase** only when every number it writes exists in the packet (validator as `bai_agents.validate`); on mismatch the deterministic template renders.

### 3.1 Slot dictionary

| Slot | Source | Rules |
|---|---|---|
| `{n}` | `claim.n` | integer, with a unit noun: "6 rallies" |
| `{m}` | `claim.denominator` | "of {m}" always paired with `{n}` for rates |
| `{unit}` | metric registry | `rallies`, `shots`, `matches`, `minutes` — pluralised by ICU |
| `{window}` | comparison window | "your last 4 matches like this one" |
| `{baseline}` | previous value | with date: "11 shots on 12 Oct" |
| `{followed}` / `{total}` | `coverage` | "We followed {followed} of {total} {unit}" |
| `{situation}` | claim title | a *situation*, never a trait: "long rallies", "returns from the back corner" |
| `{rallyNo}` | rally number | "rally 14" (never "R14") |
| `{clock}` | m:ss | "0:42" |
| `{check}` | `CheckState` | selects the hedge (see below) |
| `{shotName}` | ontology label | lower-case in sentences: "cross-court net shot" (Preview) |
| `{me}` / `{other}` | nicknames | "you" for `me` |

**Hedge by `{check}`:** `checked` → no hedge · `looks_right` → no hedge · `worth_a_look` → prefix "We think" · `not_enough` → claim not rendered.

### 3.2 `descriptive`

| Template | Example |
|---|---|
| "{situation}: {n} {unit}." | "Rallies of 10+ shots: 3." |
| "You kept this rally going for {n} shots." | "You kept this rally going for 14 shots." |
| "We followed {followed} of {total} {unit}." | "We followed 31 of 36 rallies." |
| "Most of the shots you played were {shotName}s ({n} of {m} we could name)." | "Most of the shots you played were clears (14 of 38 we could name)." |
| "You were in play for about {n} minutes." (active play, not exercise time) | "The shuttle was in play for about 12 minutes." |

### 3.3 `comparison`

| Template | Example |
|---|---|
| "Compared with {window}: {current} {unit}, up from {baseline}." | "Compared with your last 4 matches like this one: 14 shots, up from 11." |
| "{situation} appeared in {n} of {m} rallies this time, and {n0} of {m0} last time." | "Long rallies appeared in 5 of 14 this time, and 3 of 12 last time." |
| "Not directly comparable: {reason}." (when `ComparabilityResult.ok = false`) | "Not directly comparable: a different camera angle." |
| Decrease (neutral): "A shorter longest rally this time: {current} {unit} (was {baseline})." | "A shorter longest rally this time: 9 shots (was 14)." |

Rules: a comparison always names the window and the sample; "improved" is used only when the metric is defined as better-when-higher *and* the comparison is eligible *and* `n` meets the minimum — otherwise "appeared more often" / "changed".

### 3.4 `hypothesis`

| Template | Example |
|---|---|
| "{situation} {pattern}. This may {meaning}." | "In long rallies, you often returned to the middle after a back-corner shot. This may leave you fewer options at the net." |
| "One reading is {meaning}. Other things could explain it: {alt1}, {alt2}." | "One reading is that you were rushed. Other things could explain it: a strong opponent shot, or tiredness late in the game." |
| "We saw this in {n} of {m} {unit}. That's {sampleWord} — treat it as an early signal." | "We saw this in 3 of 4 rallies. That's a small number — treat it as an early signal." |

**Always** list ≥ 1 alternative explanation (opponent pressure, score, fatigue, chance, a labelling error) from the candidate table in Blueprint §9.4; the card shows them under "Other things that could explain it".

### 3.5 `recommendation`

| Template | Example |
|---|---|
| "If it helps: {action}." | "If it helps: try one lift to the back corner when you're rushed." |
| "You could {action} and watch {whatToNotice}." | "You could play a high, deep lift and watch where the shuttle lands." |
| "One idea for your next game: {action}. Skip it if it doesn't fit." | "One idea for your next game: reset with a lift. Skip it if it doesn't fit." |

Rules: one action; feasible; never a physical-load prescription; never "you must/should/need to"; offers **Pick as my focus / Not now**; if the pattern has `check = worth_a_look`, no recommendation is generated at all.

### 3.6 Closed set of Moment titles (HeroMoment / MomentCard)

Built from facts only. "Your longest in a match so far" appears only when the personal-best definition holds and is Checked.

| Kind | Title | Subtitle |
|---|---|---|
| long rally | "A {n}-shot rally" | "Rally {rallyNo} · {clock}" |
| personal best | "Your longest rally in a match" | "{n} shots · was {baseline}" |
| defence | "A save from the back corner" | "You kept the rally alive" |
| net | "A long exchange at the net" | "{n} shots close to the net" |
| close point | "A tight moment — {score}" | only when the score is Checked (scored matches) |
| comeback | "Back level after trailing" | only when score data is Checked |
| chosen | "Your pick" | "{title or note}" |
| fun | "One for the memory book" | visible only with the player's opt-in |

No superlatives beyond the definitions ("best", "epic", "amazing" are banned — §12).

---

## 4. Situation sets: win · loss · personal best · first match · return after a break

> The recap's emotional tone never depends on the scoreline (D6). The **same structure** appears after a win and a loss; only facts differ.

### 4.1 After a win (scored match)

| Slot | Copy |
|---|---|
| Header | "Your match, in moments." (never "Victory!") |
| Score chip (small, optional) | "Score 21–17" |
| Opening | "Here are three moments from your match." |
| Strength | "You returned 7 of 9 deep clears we could follow." |
| Note | "A win doesn't tell us how each rally went — the clips do. Start with the long one." *(optional, Coach-guided only)* |
| Next | NextStepRow: Keep this moment · Look at a pattern · Try something next · Done for now |

No confetti, no "You dominated", no crown.

### 4.2 After a loss

| Slot | Copy |
|---|---|
| Entry choice (Blueprint §3.4) | "How would you like to look at this?" **Quick recap · Look closer · Later** |
| Header | "Your match, in moments." (identical to a win) |
| Opening | "There are 12 moments here worth keeping. Start with the longest rally." |
| Strength | "You kept 4 rallies going past 10 shots." (if true) |
| If no strength is reliable | "We couldn't pick out a clear strength with enough evidence this time. The moments are still yours." |
| Pattern (optional, never forced) | "If you want to look at one thing: …" |
| Never | "Better luck next time", "You lost because…", "Your weak spot…", deficit-only lists |

### 4.3 Personal best

| Slot | Copy |
|---|---|
| Card label | "Personal best" (outline star) |
| Title | "Your longest rally in a match" |
| Body | "14 shots — up from 11 on 12 Oct." |
| Definition line | "Counted as: shots in a rally we checked." |
| Chip | "Checked" or "Looks right" |
| Context | "Based on 4 matches like this one." |
| After a Fix removes it | "This record changed after your fix. It's now 11 shots." |
| Never | "New record!!!", "You're unstoppable", auto-escalated target ("Next: 16!") |

### 4.4 First (a shot type or milestone spotted)

| Slot | Copy |
|---|---|
| Pill | "First · Cross-court net shot" |
| Body | "We spotted a cross-court net shot in your video for the first time." |
| Preview note | "Shot names are a preview — tell us if this one's right." |
| Uncertain | "Maybe a first — take a look." (excluded from My story until Checked) |
| Never | "Unlocked!", "Earned!", "You've mastered…" ("spotted" ≠ "mastered") |
| Persistent line (grid) | "Spotted means we saw it in your video. It doesn't mean it's finished or mastered." |

### 4.5 First match

| Surface | Copy |
|---|---|
| Processing | "Getting your first match ready. You can watch it as soon as the first seconds are ready." |
| Recap header | "Your first match." |
| Opening | "This is your starting point — there's nothing to compare with yet, and that's fine." |
| Progress | "Your first match is your starting point." |
| Journey entry | "First match saved" |
| Never | "Welcome to the journey!!", "Level 1" |

### 4.6 Return after a break (≥ 14 days since the last match, or the player's own "I'm back")

| Surface | Copy |
|---|---|
| Home greeting | "Good to see you." (no day counts) |
| Primary card | "Pick up where you left off — or add a new match." |
| Progress | "It's been a few weeks. Want to start a fresh comparison from your next match? Your history stays as it is." **[Start fresh] [Keep comparing]** |
| First new recap | "Welcome back. Here's one match to start with." |
| Journey (only if the player enabled participation milestones) | "Back on court after 3 weeks" |
| Never | "You've been away for 21 days", "You broke your streak", "You're falling behind", regression alarms, comparisons with an "old peak" |
| Notifications | none by default (§11.4) |

### 4.7 Match types (D12)

| Type | Copy adaptations |
|---|---|
| **Match** (scored) | score chip allowed once winners are Checked; "rallies" and "points" both used carefully ("point" only for a scored rally) |
| **Social game** | never mentions score, winner, game or deuce; "rallies", "moments", "time in play". Header: "Your game, in moments." |
| **Practice** | "drill", "session"; no score; moments labelled "Reps" are **not** used (no counts of attempts without eligibility); copy focuses on "what you kept going" |

---

## 5. Onboarding and capture microcopy

### 5.1 Landing and sample (ids `onb.*`)

| Id | Copy |
|---|---|
| `onb.value.headline` | Your game. Your moments. Your progress. |
| `onb.value.sub` | Turn badminton matches into moments you'll want to replay, and into things you can actually understand. |
| `onb.value.cta` | See an example |
| `onb.value.cta2` | Analyse my match |
| `onb.value.signin` | I already have an account |
| `onb.value.pillars` | Relive your best rallies · See your own progress · Share what you choose |
| `onb.how.title` | How it works |
| `onb.how.steps` | Play · Upload · Check what we found · Choose what to do — or nothing |
| `onb.limits.title` | What we can and can't analyse yet |
| `onb.limits.body` | Today we work best on **singles** filmed from behind one end of the court, with the whole court in view. Doubles, side-on views and some shot names are still a preview or not ready. |
| `onb.privacy.line` | Private by default. Sharing is always your choice. |
| `onb.sample.badge` | Sample — not a real match |
| `onb.sample.cta` | Try it with your own match |

### 5.2 Purpose and preset questions

| Id | Copy |
|---|---|
| `onb.purpose.title` | What would be useful today? |
| `onb.purpose.hint` | Pick up to two. You can change this any time. |
| `onb.purpose.moments` | Keep the moments |
| `onb.purpose.understand` | Understand my game |
| `onb.purpose.practise` | Choose something to practise |
| `onb.purpose.compete` | Prepare to compete |
| `onb.purpose.discuss` | Discuss with someone |
| `onb.purpose.justplay` | Just play |
| `onb.purpose.notsure` | Not sure yet |
| `onb.purpose.skip` | Skip for now |
| `onb.preset.title` | How much do you want to see? |
| `onb.preset.relax` | **Relax** — Highlights and memories, without the pressure. |
| `onb.preset.explore` | **Explore** — Discover shots, firsts and personal bests. |
| `onb.preset.improve` | **Improve** — Understand a pattern and pick something to try. |
| `onb.preset.compete` | **Compete** — Detailed match analysis, with filters and tables. |
| `onb.preset.change` | You can change this at any time. It only changes what you see, never your data. |
| `onb.preset.bestfor` | Best for: {who} |

### 5.3 Record guide and framing

| Id | Copy |
|---|---|
| `rec.title` | Filming your match |
| `rec.step1` | **Place the phone** behind one end of the court, as high as you safely can, and keep it still. |
| `rec.step2` | **Get the whole court in view** — all the lines, and both players at all times. |
| `rec.step3` | **Check the light.** Even light works best. Avoid pointing at windows. |
| `rec.consent` | Tell the people on court you're filming. Some venues have rules about filming — check yours. |
| `rec.limits` | Right now we follow **singles**. Doubles and side-on views are still on the way. |
| `rec.check.lines` | I can see all the court lines |
| `rec.check.players` | Both players stay in the picture |
| `rec.check.still` | The phone won't move |
| `rec.check.light` | The light is even |
| `rec.test.cta` | Test a 10-second clip first |
| `rec.test.why` | A short test shows problems before you film a whole match. |
| `rec.skip` | I already have a video — upload it |

### 5.4 Suitability results (`SuitabilityResult`)

| Id | Copy |
|---|---|
| `suit.ok.title` | Looks good |
| `suit.ok.body` | We can follow this video. |
| `suit.limits.title` | Usable, with limits |
| `suit.limits.body` | We can follow rallies and pick moments. We won't be able to show: {list}. |
| `suit.limits.item.shots` | shot names |
| `suit.limits.item.court` | the court map |
| `suit.limits.item.score` | the score |
| `suit.no.title` | We can't follow this one |
| `suit.no.body` | {why} |
| `suit.no.why.angle` | The camera is too far to the side to see the court lines. |
| `suit.no.why.court` | We couldn't find the court lines in the video. |
| `suit.no.why.players` | We couldn't see two players clearly. |
| `suit.no.why.res` | The video is too small or too dark to follow. |
| `suit.no.fix` | **What to try:** {fix} |
| `suit.no.fix.angle` | Film from behind one end of the court. |
| `suit.no.fix.court` | Step back until all the lines are in view. |
| `suit.no.keep` | Keep it as clips only |
| `suit.no.manual` | Show us where the court is |

### 5.5 Pick yourself, who's who

| Id | Copy |
|---|---|
| `me.title` | Which one is you? |
| `me.hint` | Tap yourself in the picture. |
| `me.near` | The player nearest the camera |
| `me.far` | The player furthest from the camera |
| `me.none` | I'm not in this video |
| `me.unsure` | Not sure — show me another moment |
| `me.other.label` | What should we call the other player? (optional) |
| `me.other.ph` | e.g. Aditi |
| `me.doubles` | This looks like doubles. We can follow singles for now. |
| `me.confirm` | You — {nickname} |
| `me.undo` | That's not me |

### 5.6 Place your court

| Id | Copy |
|---|---|
| `court.detecting` | Finding the court lines… |
| `court.confirm.title` | Does this match your court? |
| `court.confirm.yes` | Yes, that's it |
| `court.confirm.adjust` | Adjust |
| `court.fit.good` | Good fit |
| `court.fit.ok` | Okay fit |
| `court.fit.low` | We're not sure about this one |
| `court.manual.title` | Show us where the court is |
| `court.manual.hint` | Drag each dot to a corner. Use arrow keys to nudge. |
| `court.manual.corner.nl` | Bottom-left corner of the court |
| `court.manual.corner.nr` | Bottom-right corner of the court |
| `court.manual.corner.fr` | Top-right corner of the court |
| `court.manual.corner.fl` | Top-left corner of the court |
| `court.notfound.title` | We couldn't find the court lines |
| `court.notfound.body` | The lines may be hidden, faint or too far away. |
| `court.notfound.tip` | Film from behind one end, high up, with all the lines in view. |
| `court.moves` | We follow the lines through the video, even when the camera moves. |
| `court.othercam` | Other camera angles aren't followed. |

---

## 6. Upload, processing, partial, failed

### 6.1 Upload

| Id | Copy |
|---|---|
| `up.drop` | Drop a video here, or **choose a file** |
| `up.types` | MP4, MOV, MKV or WebM · up to {maxMb} MB |
| `up.toobig` | That file is {size} GB. This server takes files up to {maxMb} MB. Try a shorter clip or a lower-quality export. |
| `up.progress` | Uploading {pct}% |
| `up.checking` | Checking the video |
| `up.cancel` | Cancel |
| `up.interrupted` | The upload stopped. {resumeLine} |
| `up.interrupted.resume` | Start again and we'll pick it up from the beginning. |
| `up.interrupted.noresume` | Your connection dropped. Nothing was saved yet — start the upload again. |
| `up.title.label` | Name this match (optional) |
| `up.leave` | Once upload says "Received", follow the server-confirmed processing status. Keep this tab open unless it says processing will continue. |

> `up.interrupted.resume` ("pick up from where it stopped") must only be used when resumable upload exists (G-12). Until then use `.noresume`.

### 6.2 Processing stages (`ProcessingStages`)

| Id | Copy |
|---|---|
| `proc.title` | Getting your match ready |
| `proc.s1` | Video received |
| `proc.s2` | Video prepared |
| `proc.s3` | You can watch now |
| `proc.s4` | Following the players and shuttle |
| `proc.s5` | Finding rallies and moments |
| `proc.s6` | Ready |
| `proc.pct` | {pct}% |
| `proc.eta` | About {minutes} minutes left |
| `proc.eta.none` | We'll let you know when it's ready. *(no estimate yet)* |
| `proc.leave` | You can close this page — we'll keep working. |
| `proc.leave.notify` | You can close this page. We'll tell you when it's ready. |
| `proc.watch` | Watch while it works |
| `proc.ready.sofar` | Ready so far: {n} rallies found |
| `proc.degraded` | Part of this video is a different camera angle. We skip those parts. |
| `proc.warming` | Warming up… |
| `proc.catchup` | The analysis is catching up — playback will carry on by itself. |

### 6.3 Status chips (`MatchStatusChip`)

| Engine | Copy |
|---|---|
| `created` | In the queue |
| `ingesting` | Getting ready |
| `ready_to_play` | You can watch now |
| `analysing` | Analysing |
| `analysed` | Ready |
| `failed` | Didn't work |

### 6.4 Complete

| Id | Copy |
|---|---|
| `proc.done.title` | Your recap is ready |
| `proc.done.body` | Start with the moments whenever you like. |
| `proc.done.notify` | Your recap is ready. Start with the moments you saved whenever you like. |

---

## 7. Recap, moments, review and fix

### 7.1 Recap structure (ids `recap.*`)

| Id | Copy |
|---|---|
| `recap.entry` | How would you like to look at this? |
| `recap.entry.quick` | Quick recap |
| `recap.entry.deep` | Look closer |
| `recap.entry.later` | Later |
| `recap.moments.title` | Moments |
| `recap.game.title` | My game |
| `recap.together.title` | Together |
| `recap.together.empty` | This was a singles match, so there's nothing to share between partners here. |
| `recap.shownbecause` | Shown because you chose {purposes}. |
| `recap.change` | Change |
| `recap.reset` | Reset |
| `recap.showall` | Show everything |
| `recap.facts.rallies` | {n} rallies followed |
| `recap.facts.longest` | Longest rally: {n} shots |
| `recap.facts.play` | About {n} minutes with the shuttle in play |
| `recap.facts.note` | The shuttle in play isn't the same as time on court. |
| `recap.story.lead` | {opening} |
| `recap.note.add` | Add a note |
| `recap.note.ph` | Anything you want to remember about this match? |
| `recap.feedback.q` | Was this recap useful? |
| `recap.feedback.yes` | Useful |
| `recap.feedback.no` | Not useful |
| `recap.feedback.report` | Report something |
| `recap.feedback.thanks` | Thanks. |
| `recap.feedback.demo` | Noted on this device (demo). |
| `recap.noMoment.title` | We couldn't pick a moment we're sure about |
| `recap.noMoment.body` | The video didn't give us a clear enough rally. You can choose one yourself. |
| `recap.noMoment.cta` | Choose a rally |

### 7.2 Moments and clips

| Id | Copy |
|---|---|
| `mom.watch` | Watch |
| `mom.save` | Save |
| `mom.saved` | Saved |
| `mom.share` | Share… |
| `mom.why` | Why this moment? |
| `mom.why.long` | It was one of your longest rallies. |
| `mom.why.defence` | You kept the rally alive from the back of the court. |
| `mom.why.net` | A long exchange close to the net. |
| `mom.why.variety` | You played a mix of different shots. |
| `mom.why.close` | A tight moment in the score. |
| `mom.why.chosen` | You picked this one. |
| `mom.private` | Private |
| `mom.fun.lock` | Private — needs your OK to share |
| `mom.empty` | Your moments will appear here after your first match. |
| `mom.watchagain` | Watch again |
| `mom.openMatch` | Open the full match |
| `mom.openRally` | Open this rally in Deep dive |
| `mom.preview.q` | Preview quality |
| `clip.loading` | Getting your clip ready… |
| `clip.preparing` | Preparing the video — you can watch as soon as the first seconds are ready. |
| `clip.error` | This browser can't play the video. Try a recent Chrome, Edge, Safari or Firefox. |
| `clip.notanalysed` | Not analysed yet |
| `clip.caption.prefix` | What happens in this clip: |

### 7.3 Review & fix (`ReviewBanner`, `FixSheet`, `ChangeSummaryBanner`)

| Id | Copy |
|---|---|
| `fix.banner` | {n} things in this recap are worth a quick check. It takes about a minute. |
| `fix.banner.cta` | Check them |
| `fix.banner.dismiss` | Not now |
| `fix.title` | Is this right? |
| `fix.position` | {i} of {n} |
| `fix.q.winner` | Who won this rally? |
| `fix.q.winner.you` | You |
| `fix.q.winner.skip` | Not sure |
| `fix.q.official` | Is this part of the game? |
| `fix.q.official.yes` | Yes |
| `fix.q.official.no` | No — it was a warm-up or a break |
| `fix.q.start` | The match starts here |
| `fix.more` | Something else is wrong |
| `fix.more.player` | It's the wrong player |
| `fix.more.shot` | The shot name is wrong |
| `fix.more.clip` | The clip is cut badly |
| `fix.more.other` | Something else |
| `fix.warn.score` | Changing the winner updates the score from this rally on. |
| `fix.save` | Save fix |
| `fix.ok` | I checked this rally |
| `fix.skip` | Skip |
| `fix.saved.same` | Thanks — that matches what we found. |
| `fix.saved.changed` | Thanks. Affected findings will update. |
| `fix.feedback` | Thanks — noted. This won't change your numbers yet. |
| `fix.offline` | You're offline. We'll save this when you're back. |
| `fix.error` | We couldn't save that. Your choices are still here — try again. |
| `chg.title` | Updated after your fix |
| `chg.score` | Score after rally {n}: {before} → {after} |
| `chg.moments` | {n} moments re-checked |
| `chg.removed` | One moment was removed because it depended on that rally. |
| `chg.see` | See what changed |
| `chg.undo` | Undo |
| `chg.progress` | This changes your comparison for {date}. |

### 7.4 Deep dive (labels and hints)

| Id | Copy |
|---|---|
| `dd.title` | Deep dive |
| `dd.nav.story` | Story |
| `dd.nav.rallies` | Rallies |
| `dd.nav.shots` | Shots |
| `dd.nav.court` | Court |
| `dd.nav.compare` | Compare |
| `dd.nav.ask` | Ask |
| `dd.rallies.count` | {n} rallies |
| `dd.rallies.filter` | Only rallies worth a look |
| `dd.rally.notcounted` | Not counted — {reason} |
| `dd.rally.count` | Count this rally |
| `dd.rally.won.you` | You won this one |
| `dd.rally.won.other` | {name} won |
| `dd.rally.unclear` | Winner unclear |
| `dd.rally.why` | How it ended: {reason} |
| `dd.out` | the shuttle landed out |
| `dd.net` | the shuttle went into the net |
| `dd.in` | the shuttle landed in |
| `dd.unknown` | we couldn't tell how it ended |
| `dd.shots.title` | Shots you played |
| `dd.shots.unnamed` | {n} shots we couldn't name |
| `dd.shots.preview` | Shot names are a preview — they can be wrong. Tap a rally to check. |
| `dd.shots.spotted` | Spotted {date} |
| `dd.shots.notyet` | Not spotted yet |
| `dd.shots.note` | Spotted means we saw it in your video. It doesn't mean mastered. |
| `dd.court.kind.presence` | Where I stood |
| `dd.court.kind.movement` | Where I moved |
| `dd.court.kind.origin` | Where I hit from |
| `dd.court.kind.landing` | Where my shots were played back from |
| `dd.court.kind.targeting` | Where I aimed |
| `dd.court.hint.presence` | Where you stood while the shuttle was in play. |
| `dd.court.hint.movement` | The areas you moved through most. |
| `dd.court.hint.origin` | The spots you hit from. |
| `dd.court.hint.landing` | Where the other player returned your shot from — an estimate of where it landed. |
| `dd.court.hint.targeting` | Areas of their side of the court you aimed at. |
| `dd.court.legend.far` | Far end — the other player's side |
| `dd.court.legend.near` | Near end — your side |
| `dd.court.scale` | fewer visits → more visits |
| `dd.court.hatched` | Hatched = not enough to say |
| `dd.court.table` | Table view |
| `dd.court.uncal` | We need to find your court first. |
| `dd.court.cta` | Place your court |
| `dd.story.score` | The score, in a sentence |
| `dd.story.momentum` | Rally-by-rally lead |
| `dd.compare.title` | Compare two matches |
| `dd.compare.disabled` | Different camera angle — court positions aren't comparable. |
| `dd.side.title` | Side by side |
| `dd.side.out` | Shots that went out |
| `dd.side.net` | Shots into the net |

### 7.5 Ask about this match

| Id | Copy |
|---|---|
| `ask.title` | Ask about this match |
| `ask.intro` | Answers point to the rallies they're based on. Tap a number to watch that moment. |
| `ask.ph` | Ask about rallies, shots, patterns… |
| `ask.s1` | What was my longest rally? |
| `ask.s2` | Show me the rallies at the net |
| `ask.s3` | Which rallies were close? |
| `ask.s4` | What went well for me? |
| `ask.s5` | What could I try next game? |
| `ask.thinking` | Looking through the match… |
| `ask.grounded` | Every fact above links to its moment. |
| `ask.ungrounded` | Some statements couldn't be linked to your match. |
| `ask.nolm` | Written answers need a language model on this server. You'll still get facts from your match. |
| `ask.refuse` | We can't tell that from the video. {why} |
| `ask.refuse.why.emotion` | We can't tell how a player feels from footage. |
| `ask.refuse.why.health` | We can't give health or injury advice from video. |
| `ask.refuse.why.cause` | We can show what happened in the rally, not prove why it happened. |

### 7.6 Export ("Take it with you")

| Id | Copy |
|---|---|
| `exp.title` | Take it with you |
| `exp.pdf` | **Match story (PDF)** — a short, printable summary with your best moments. |
| `exp.csv` | **Rallies (spreadsheet)** — one row per rally. |
| `exp.clip` | **Clip (video)** — one rally as a video file. |
| `exp.events` | **Event log** — every event with its evidence (for analysts). |
| `exp.json` | **Summary (data)** — the final numbers as JSON. |
| `exp.legacy` | **Classic CSV** — the older 8-column format. |
| `exp.partial` | Analysis is still running — exports include everything analysed so far. |

---

## 8. States

### 8.1 Empty states per screen (one next step each)

| Screen / id | Title | Body | Action |
|---|---|---|---|
| Home `empty.home` | Your badminton story starts here | Add a match, or look at an example first. | **Add a match** · See an example |
| Matches `empty.matches` | No matches yet | When you add a match, it'll show up here. | **Add a match** |
| Moments `empty.moments` | Your moments will appear here | We pick them from your matches. | **Add a match** |
| Recap (no moments) `empty.recap` | Nothing to show yet | We're still working on this match. | Watch while it works |
| Rallies `empty.rallies` | No rallies yet | Rallies appear here as soon as they finish. | — |
| Shots `empty.shots` | No shots named yet | We name shots after rallies finish. Names are a preview. | — |
| Court `empty.court` | We need to find your court first | Then we can show where you moved. | **Place your court** |
| Progress `empty.progress` | Your first match is your starting point | After a few matches like this, you'll see how things change. | **Add a match** |
| Records `empty.records` | No personal bests yet | They appear when we can check a match against your own history. | — |
| Shot Explorer `empty.firsts` | Nothing spotted yet | We'll show shots we see in your video. | — |
| My story `empty.story` | Your story starts with your first match | It fills in as you play. There's no hurry. | **Add a match** |
| Explore `empty.explore` | No challenges right now | Challenges are optional and show up when they fit your play. | — |
| Together `empty.together` | Nothing to share yet | Pair features come with doubles. We'll tell you when they're ready. | — |
| Notifications `empty.notif` | Nothing yet | You can choose what we tell you about. | Notification settings |
| Library search `empty.search` | Nothing matches those filters | Try removing a filter. | Clear filters |
| Export `empty.export` | Nothing to export yet | Analyse a match first. | **Add a match** |

### 8.2 Loading

| Id | Copy |
|---|---|
| `load.page` | *(skeleton — no text)* |
| `load.recap` | Preparing your recap… |
| `load.checking` | Checking player and rally labels… |
| `load.partial` | Some insights are ready while the rest finish. |
| `load.save` | Saving… |

### 8.3 Partial, low coverage, unsupported footage

| State | Title | Body | Actions |
|---|---|---|---|
| `PartialAnalysisNote` | Some results are ready | We're still checking the rest. Unfinished parts show a skeleton. | Watch now |
| `LowCoverageState` | We could only follow part of this match | We followed {followed} of {total} rallies, so we've left out {lost}. {usable} | Place your court · Filming tips · Keep moments only |
| `UnsupportedFootageState` | We can't follow this video | {why} {fix} | Show us the court · Filming guide · Keep the footage |
| Court not found (match running) | We couldn't find your court | Positions, heat maps and in/out calls will be off until we do. | Place your court — about a minute |
| Degraded | Reduced analysis | Part of the analysis couldn't run: {stage}. The rest is fine. | Details |

`{lost}` is a plain list ("shot names and the court map"); `{usable}` is "Your {n} moments are still here."

### 8.4 Failed, offline, permission

| State | Title | Body | Actions |
|---|---|---|---|
| `FailedState` | This didn't work | {cause in plain words}. Your video is safe. | Analyse again · Report · Keep the video |
| Cause examples | — | "We couldn't read the video file." · "The server stopped while working." · "The video was too long for this server." | — |
| `OfflineState` | You're offline | Saved items still work. We'll catch up when you're back. | Retry |
| Reconnecting | Reconnecting | — | — |
| `PermissionRevokedState` | You no longer have access | {who} stopped sharing this on {date}. | Ask for a new link · Go to Matches |
| Link expired | This link has expired | It was set to expire on {date}. | Ask for a new link |

### 8.5 Not enough to say (by reason)

`NotEnoughToSay` takes one of five reasons; each has a headline, a body and a next action.

| `reason` | Headline | Body | Next |
|---|---|---|---|
| `too_few` | Not enough to say yet | We have {n} examples. We'd want at least {min} before we say anything about this. | Watch the {n} clips |
| `low_label_reliability` | We couldn't tell reliably | We weren't sure enough about these {n} {things} to include them. | Take a look |
| `not_comparable` | Not directly comparable | {reason}. Comparing them would be misleading. | Choose different matches |
| `no_footage` | Nothing to look at here | That part of the match wasn't analysed. | See what was analysed |
| `capability_not_yet` | Not ready yet | We can't do this reliably yet: {why}. | Back to your recap |

**Also:** "There aren't enough comparable matches to describe a trend yet. Here are the clips." · "Nothing stands out as a clear opportunity here." · "No clear strength can be shown reliably yet." · "We couldn't name every shot in this video, so the shot breakdown is incomplete."

### 8.6 Tooltips

| Control | Tooltip |
|---|---|
| `PreviewTag` | "Preview — this works, with limits. {reason}" Typical reasons: "Shot names can be wrong." · "Positions are estimates." · "We couldn't confirm the court fit." |
| `CheckChip` Checked | "You or a reviewer confirmed this." |
| `CheckChip` Looks right | "This type of finding has been tested on footage like yours. No person checked this one." |
| `CheckChip` Worth a look | "Our analysis isn't sure. Take a quick look." |
| `CheckChip` Not enough | "We couldn't tell reliably, so we left it out of your recap." |
| `CoverageBar` | "What we could see: the parts of the match we followed." |
| `MetricPopover` header | "What this is · How we count it · What we left out · Limits" |
| Court-fit chip | "Good fit means the court lines lined up well with the video." |
| Sample | "Sample data — nothing here is a real match." |

---

## 9. Doubles copy rules (**Not yet** in the engine; copy is ready so the design is complete)

1. **"Both of you."** Pair achievements credit both players equally unless the data attributes a *specific* contribution.
2. **No partner blame, ever.** Never "your partner missed", "you left him/her/them alone", "{name} lost the point". Aggregate outcomes are never assigned to one partner.
3. **Observation, not intent.** "Both of you were in this rally." Not "great communication" — we cannot hear or infer intent.
4. **Roles are descriptive.** "Front" and "back", "serving" and "receiving" — never "weak side", "carrying".
5. **Consent first.** Pair memories show only when both players' sharing allows; wording: "Saved to your pair memory with {partner}."
6. **Identity uncertain → ask.** "We aren't sure which of you is which in these clips. Can you check?" (never silently assign).
7. **Separate individual and pair.** Section headings: "You", "{partner}" (only if shared), "The two of you".
8. **Pronouns.** Use names and "you"; never guess pronouns for a partner or opponent — use the nickname or "they".
9. **Occlusion honesty.** "Two players on one side can hide each other, so we're less sure about doubles." — shown with a Preview tag.

| Situation | Copy |
|---|---|
| Shared rally | "Both of you were in this 12-shot rally." |
| Rescue (descriptive) | "A long return from the back corner kept this rally alive." *(no attribution to a partner's mistake)* |
| Coordinated attack | "A back-court shot, then a front-court follow-up — in the same rally." |
| Pair record | "Your longest rally together: 16 shots." |
| Unsure | "We're less sure about this one in doubles. Worth a look?" |
| Never | "Aditi lost you that point", "You carried the game", "Your partner is the weak link" |

---

## 10. Progress, records, journey, focus, challenges

| Surface | Copy |
|---|---|
| Progress headline | "Based on {n} matches like this one." |
| Progress card | "Longest rally in a match: {current} shots · was {baseline}." |
| One / two matches | "Your first match is your starting point." · "Two matches isn't enough to call it a trend. Here are the two clips." |
| Non-comparable | "Not directly comparable: {reason}." (`reason` ∈ different camera angle · singles vs doubles · too few rallies we could follow · a changed court fit) |
| Decrease | "A shorter longest rally this time: {current} shots (was {baseline})." (never on Home) |
| Noise note | "These move around from match to match, so a small change isn't a signal." |
| No improvement detected | "Across {n} matches like this, we can't see a clear change yet. That's normal — it can take a while." |
| Fresh baseline | "Start a fresh comparison from your next match?" **[Start fresh] [Keep comparing]** |
| Records page | "Personal bests are measured against your own matches only." |
| Journey | `story.first` "First match saved" · `story.pb` "Personal best: {title}" · `story.first.shot` "First: {shot}" · `story.saved` "Saved: {title}" · `story.return` "Back on court after {weeks} weeks" |
| Journey gap | *(no label)* |
| Focus title | "My focus" |
| Focus reason | "I chose this because…" |
| Focus plan | "At the start of my next game, I'll…" |
| Focus cue | "What to notice:" |
| Focus ladder | "Reviewed → Practised → Shown in a later match" |
| Focus barrier | "What got in the way?" **No court · No partner · No time · Not a priority now** |
| Focus retire | "Retire this focus" / "Replace it…" |
| Reflection (pre) | "What felt important in this match?" |
| Reflection (post feedback) | "Does this fit what you noticed?" |
| Reflection (post practice) | "What changed?" |
| Reflection skip | "Skip" |
| Challenge | "{title} — optional. {why}" · **Try it · Not now** |
| Challenge done | "Done. No rush on the next one." |
| Challenge not offered | *(no copy — not shown)* |

---

## 11. Consent, privacy, sharing, deletion, notifications

### 11.1 Consent cards (`ConsentCards`, `ConsentLedger`)

| Id | Label | Description | Consequence if turned off |
|---|---|---|---|
| `con.analyse` | Analyse this video | We study the video to find rallies and moments. | We can't make your recap. |
| `con.store` | Keep the video so I can watch it again | We store the video for you. | We delete it after analysis; clips can't be played later. |
| `con.history` | Add the results to my history | Your progress and story use these results. | This match won't count in progress or your story. |
| `con.share` | Let me share chosen moments with people I pick | You always approve each clip before it's shared. | Existing links stop working. |
| `con.train` | Help improve the product with this video | Used to make the analysis better. **Off unless you turn it on.** | Nothing changes for you. |

| Id | Copy |
|---|---|
| `con.title` | Your choices |
| `con.line` | Private by default. Sharing is always your choice. |
| `con.sep` | Each of these is separate. Saying yes to one never turns on another. |
| `con.change` | You can change these any time in Privacy. |
| `con.details` | Read the details |
| `con.people` | People who appear in your video: you decide what is shared. |
| `con.saved` | Saved. |
| `con.revoked` | Sharing is now off. Existing links will stop working. |
| `con.demo` | Demo — nothing is stored. |
| `con.ledger.cols` | Permission · Status · Last changed |

### 11.2 Share dialog

| Id | Copy |
|---|---|
| `sh.title` | Share this moment |
| `sh.who` | Who can see it? |
| `sh.who.link` | Only people I send the link to |
| `sh.who.named` | A named person |
| `sh.who.public` | Anyone with the link |
| `sh.who.public.warn` | Anyone who gets this link can watch it. Are you sure? |
| `sh.include` | What's included |
| `sh.inc.clip` | The clip |
| `sh.inc.score` | The score |
| `sh.inc.names` | Names (otherwise nicknames) |
| `sh.inc.analytics` | Court map and numbers |
| `sh.people` | People in this clip: {list} |
| `sh.consent` | I have the OK of the people in this clip. |
| `sh.blur` | Blur other people |
| `sh.blur.na` | Blurring isn't available yet. |
| `sh.expiry` | How long? |
| `sh.exp.7` | 7 days |
| `sh.exp.30` | 30 days |
| `sh.exp.never` | No end date |
| `sh.dl` | Allow download |
| `sh.recall` | Once sent, a copy someone saves can't be taken back. |
| `sh.funny` | This one's a bit silly. Share it anyway? |
| `sh.create` | Create private link |
| `sh.created` | Link created. It works until {date}. |
| `sh.copy` | Copy link |
| `sh.copied` | Copied. |
| `sh.stop` | Stop sharing |
| `sh.blocked` | Sharing is off in your privacy settings. |
| `sh.blocked.cta` | Turn on sharing |
| `sh.demo` | Demo only — no link was created. |
| `sh.error` | We couldn't create the link. Your choices are still here. |

### 11.3 Deletion and export

| Id | Copy |
|---|---|
| `del.match.title` | Delete "{title}"? |
| `del.match.body` | This removes the analysis, your fixes and your moments for this match. {video} Copies you've shared or downloaded stay with the people who have them. |
| `del.video.opt` | Also delete the video |
| `del.keep` | Keep it |
| `del.do` | Delete match |
| `del.account.title` | Delete your account? |
| `del.account.body` | This removes your matches, moments and history. This can't be undone. |
| `del.account.confirm` | Type DELETE to confirm |
| `del.done` | Deleted. |
| `del.demo` | Request simulated — nothing was deleted. |
| `exp.req.title` | Export your data |
| `exp.req.body` | We'll prepare a download of your summaries, clips and event log. |
| `exp.req.status` | Requested {date} · Ready |
| `exp.limits` | Backups are cleared within {days} days. Copies already shared or downloaded stay with the people who have them. |

### 11.4 Notifications

Allowed triggers only (Blueprint §11.3). Defaults off unless needed to deliver what was requested.

| Id | Label | Copy when sent |
|---|---|---|
| `nt.ready` | My recap is ready | "Your recap is ready. Start with the moments you saved whenever you like." |
| `nt.coach` | A coach commented | "{name} left a note on {match}." |
| `nt.remind` | My own reminder | (the player's own text, e.g. "Look at my focus before Saturday") |
| `nt.trend` | Enough matches to revisit a goal *(separate opt-in)* | "You now have {n} matches like this one. Want to look at how {metric} changed?" |
| UI | "Pause all" · "Quiet hours" · "Digest" · "Turn off" | — |

**There is no inactivity trigger.** There is no "come back", "we miss you", "you're falling behind", streak, countdown, rank or FOMO notification in the product, and none may be added (D7).

### 11.5 Accessibility and preference copy

`acc.motion` "Keep animations off" · `acc.text` "Text size" · `acc.contrast` "High contrast" · `acc.captions` "Show captions on clips" · `acc.lowdata` "Use lighter video previews" · `acc.theme` "Appearance: System · Light · Dark".

---

## 12. Banned phrases and patterns

**Rule:** a string matching a banned pattern fails CI unless it carries a `// copy-lint-allow(<rule>): reason` annotation approved by the design lead.

| Category | Banned | Use instead |
|---|---|---|
| **Trait language** | "you are weak/bad/poor at…", "your weakness", "you lack…", "you're lazy", "clumsy", "your defence is terrible" | "These rallies show a recurring situation worth reviewing." |
| **Weakness** | weakness, weak spot, flaw, failing | recurring situation, something to look at |
| **Fix (of the player)** | "fix your…", "you need to fix" | "worth reviewing", "something to look at" (the **button** "Fix this" for correcting our *analysis* is allowed) |
| **Must / should** | "you must", "you should", "you need to", "you have to" | "you could", "if it helps", "one idea" |
| **Absolutes** | always, never, every time, constantly, perfect, flawless | counts with denominators: "in 6 of 9 rallies" |
| **Status inflation** | elite, pro-level, world-class, mastered, master, unstoppable, dominate/dominated, crushed, destroyed, beast, legend (outside an explicit opt-in fun label), insane, god-tier | the specific fact |
| **Hype** | amazing, awesome, epic, incredible, fantastic, brilliant, "great job!!", "nailed it" | "A new personal best: 14 shots." |
| **Causal** | "because you…", "you lost because", "caused", "led to", "that's why you lost" | "associated with", "appeared alongside", "changed after" |
| **Loss framing** | "better luck next time", "unlucky", "you were beaten", "loser", "defeat" | neutral facts + moments |
| **Streak / guilt / FOMO** | streak, "don't break", "keep it up!", "days in a row", "you haven't played in", "falling behind", "last chance", "only today", "don't miss out", "we miss you" | nothing — these mechanics do not exist |
| **Fitness/health** | calories, "burned", "fat", cardio score, "fitness level", "injury risk", "recovery score", "you're tired/fatigued/in pain" | "time in play" and the player's own optional notes |
| **Emotion inference** | "you looked angry/frustrated/nervous/confident/tired", "you seemed", "your confidence" | ask: "How did it feel out there?" (optional) |
| **AI authority** | "AI says", "our AI coach", "AI thinks", "the algorithm knows", "100% accurate" | "Our analysis found…", "We think…" |
| **Raw confidence** | "{n}% confident", "{n}% sure", "confidence score", "probability" | `CheckChip` words |
| **Engine words** | P1, P2, provisional, band, softmax, event id, rally_end, frontier, homography, reprojection | nicknames, "Looks right", "Place your court" |
| **Score as verdict** | "winner/loser" as labels for people, "victory", "defeat", "you won the match!" with celebration | "Score 21–17" as a plain fact (Match type, Checked winners) |
| **Comparison to others** | "better than most players", "top X%", "ranked", "leaderboard", "beat {name}" | comparison with the player's own history only |
| **Pressure** | "last chance", "hurry", "now", countdown timers, exclamation marks in default tone | calm, optional |
| **Over-claim on shots** | "perfect smash", "your best shot" without a verified definition; speed numbers | "a smash we spotted" + Preview |

**Allowed with care:** "personal best" (defined), "first" (spotted, with Preview), "moment", "strength" (specific, with n), "something to look at".

---

## 13. Numbers, capitalisation, punctuation, dates

### 13.1 Numbers

| Case | Rule | Example |
|---|---|---|
| Counts | digits for ≥ 10 and for every measured value; words for 1–9 only in running prose that isn't a measurement | "9 rallies", "one idea" |
| Rates | **`n of m`** first; percentage only as a secondary label | "6 of 9 long rallies (about two thirds)" |
| Rounding | round to the precision the data supports; use "about" for estimates; never show more than 0 decimals for counts or 1 for averages | "average rally: 8.4 shots" |
| Ranges | en dash, unit once | "9–14 shots" |
| Comparisons | signed difference + unit | "+3 shots" |
| Time of clips | `m:ss` | "0:42" |
| Totals of time | words | "about 12 minutes" |
| Score | en dash, plain | "21–17" |
| Denominators | always visible for rates; in compact UI they live in the `MetricPopover` and the accessible name | `aria-label="6 of 9 long rallies"` |
| Missing | `—` with reason in `aria-label`; never 0 | "—" |
| Large numbers | thin separators only ≥ 10,000 | "12,075 frames" (Advanced only) |
| Units | metres only in Advanced and only when calibrated; never speed (km/h) | — |
| Plurals | ICU: `{n, plural, one {# rally} other {# rallies}}` | "1 rally" |

### 13.2 Capitalisation and punctuation

- **Sentence case** for everything (titles, buttons, labels): "Watch this", "Add a match". Proper nouns only.
- No ALL CAPS paragraphs; ALL CAPS never for emphasis. Section labels in small caps are not used.
- Buttons are verbs; no trailing full stop; no exclamation marks (default tone).
- Body text uses full stops; headings don't.
- Em dash for aside (— with spaces in English), en dash for ranges and scores.
- Straight quotes avoided in UI: use typographic quotes “ ” and ’.
- "OK" (not "Ok", "okay") in consent text where used; prefer "yes".
- Ellipsis `…` only for loading ("Finding the court lines…") and for actions that open a dialog ("Share…").
- Names: nicknames as the player typed them; never title-case or shorten automatically.

### 13.3 Dates and times

| Case | Format | Example |
|---|---|---|
| Recent | relative | "Today", "Yesterday", "Saturday" |
| Within a year | `d MMM` | "12 Oct" |
| Older | `d MMM yyyy` | "12 Oct 2025" |
| Time | local 12-h with am/pm by locale; never 24-h unless the locale uses it | "6:42 pm" |
| Durations | `m:ss` for media, words for totals | "0:19", "12 minutes" |
| "Ago" | only up to 6 weeks, in whole weeks/days; never in an emotional context | "3 weeks ago" is allowed in a neutral Return note only |

---

## 14. Lint-able rules (implement as a unit test)

A pure function `copyLint(text, { surface, depth })` returns violations. Strings come from the message catalogue (`messages/en.json`) and from rendered text in component tests.

### 14.1 Rule list

| Id | Severity | Regex (case-insensitive unless noted) | Applies to |
|---|---|---|---|
| `trait` | error | `\byou(?:'re| are)\s+(?:so\s+)?(?:weak|bad|poor|lazy|slow|clumsy|terrible|useless)\b` · `\byour (?:weakness|weak spot|flaw)\b` · `\byou lack\b` | all |
| `weakness` | error | `\b(?:weakness|weak spot|flaw)\b` | all |
| `fix-player` | error | `\bfix your\b` | all (allow the label "Fix this") |
| `must` | error | `\byou (?:must|should|need to|have to|ought to)\b` | all |
| `absolute` | warn | `\b(?:always|never|every time|constantly|perfect(?:ly)?|flawless)\b` | recap, insight, notification |
| `inflation` | error | `\b(?:elite|pro-level|world-class|master(?:ed|y)?|unstoppable|dominat(?:e|ed|ing)|crush(?:ed|ing)?|destroy(?:ed|ing)?|beast|insane|god-tier)\b` | all |
| `hype` | error | `\b(?:amazing|awesome|epic|incredible|fantastic|brilliant|nailed it|great job)\b` | all (except an explicit fun-opt-in surface) |
| `causal` | error | `\b(?:because you|you lost because|caused|that'?s why you|led to)\b` | recap, insight (allow in `hypothesis` with alternatives) |
| `loss` | error | `\b(?:better luck|unlucky|you were beaten|loser|defeat(?:ed)?)\b` | all |
| `streak` | error | `\b(?:streak|don'?t break|keep it up|days in a row|falling behind|last chance|don'?t miss out|we miss you|only today)\b` | all |
| `health` | error | `\b(?:calories?|burn(?:ed|t)|cardio|fitness level|injury risk|recovery score|you(?:'re| are) (?:tired|fatigued|in pain))\b` | all |
| `emotion` | error | `\byou (?:looked|seemed|appeared) (?:angry|frustrated|nervous|anxious|confident|tired|upset)\b` · `\byour confidence\b` | all |
| `ai-authority` | error | `\b(?:AI says|our AI coach|AI thinks|the algorithm knows|100\s?% accurate)\b` | all (case-sensitive `AI`) |
| `raw-confidence` | error | `\b\d{1,3}\s?%\s?(?:confident|confidence|sure|certain)\b` · `\bconfidence score\b` · `\bprobability\b` | player surfaces |
| `engine-words` | error | `\b(?:P1|P2|provisional|softmax|event[_ ]id|rally_end|frontier|homography|reprojection)\b` | non-Advanced surfaces (case-sensitive) |
| `verdict` | error | `\b(?:victory|winner of the match)\b` · `\byou won the match!` | all |
| `compare-others` | error | `\b(?:top \d+\s?%|better than most|leaderboard|ranked)\b` | all |
| `exclaim` | warn | `!` | default tone surfaces (allowed in a user-chosen fun context) |
| `percent-alone` | warn | `\b\d{1,3}\s?%` not preceded by `of ` / followed by ` of ` and not accompanied by `n of m` | rate strings |
| `sentence-length` | warn | > **22 words** in one sentence (> 30 error) | all |
| `headline-length` | warn | > **12 words** | titles |
| `reading-level` | warn | Flesch–Kincaid grade > **8** on paragraphs ≥ 2 sentences | recap, onboarding, privacy |
| `slot-missing` | error | any unresolved `{slot}` in rendered output | all |
| `number-no-unit` | warn | a bare number followed by neither a unit noun, `of`, `%`, `–`, nor punctuation in a metric string | metric strings |

### 14.2 Test sketch (Vitest)

```ts
// apps/web/src/lib/copyLint.ts
export interface Violation { rule: string; severity: "error" | "warn"; match: string }
const RULES: { id: string; severity: "error" | "warn"; re: RegExp; skip?: (ctx: Ctx) => boolean }[] = [
  { id: "must", severity: "error", re: /\byou (?:must|should|need to|have to|ought to)\b/i },
  { id: "inflation", severity: "error", re: /\b(?:elite|pro-level|world-class|master(?:ed|y)?|unstoppable|dominat(?:e|ed|ing)|crush(?:ed|ing)?|destroy(?:ed|ing)?|beast|insane|god-tier)\b/i },
  { id: "causal", severity: "error", re: /\b(?:because you|you lost because|that'?s why you|led to)\b/i },
  { id: "raw-confidence", severity: "error", re: /\b\d{1,3}\s?%\s?(?:confident|confidence|sure|certain)\b|\bconfidence score\b/i },
  { id: "engine-words", severity: "error", re: /\b(?:P1|P2|provisional|softmax|rally_end|frontier|homography)\b/, skip: (c) => c.depth === "advanced" },
  { id: "streak", severity: "error", re: /\b(?:streak|don'?t break|falling behind|we miss you|don'?t miss out)\b/i },
  { id: "health", severity: "error", re: /\b(?:calories?|burn(?:ed|t)|injury risk|recovery score)\b/i },
  { id: "slot-missing", severity: "error", re: /\{[a-zA-Z0-9_.]+\}/ },
  // …remaining rules from §14.1
];
export function copyLint(text: string, ctx: Ctx = { depth: "guided", surface: "recap" }): Violation[] {
  const out: Violation[] = [];
  for (const r of RULES) { if (r.skip?.(ctx)) continue; const m = r.re.exec(text); if (m) out.push({ rule: r.id, severity: r.severity, match: m[0] }); }
  for (const s of text.split(/(?<=[.!?])\s+/)) { const w = s.trim().split(/\s+/).length; if (w > 22) out.push({ rule: "sentence-length", severity: w > 30 ? "error" : "warn", match: s.slice(0, 40) }); }
  return out;
}
// messages.test.ts: every string in messages/en.json (and every tone variant) must produce zero `error` violations.
// components.test.tsx: render each component × state × tone with fixtures; run copyLint on container.textContent.
```

**Where it runs:** (1) over the message catalogue in CI, (2) over rendered text in component tests (file 07 §13.7), (3) as a PR check on any string added to `messages/`. A **golden test** asserts that all 12 situations in §2 render in all 3 tones with identical numbers and identical limit sentences.

---

## 15. Accessibility of copy

- **Reading level** about grade 6–8 for onboarding, recap, privacy and consent; Advanced may use terminology, always with the definition one tap away (`MetricPopover`).
- **No idioms or sport slang** in core feedback ("on fire", "in the zone", "bread and butter").
- **Links and buttons** describe the destination/action out of context ("Watch this: rally 14", not "Click here").
- **Errors** say what happened and what to do, in words — never colour only, never a code.
- **Every chart** has an alt text that states the *question and the answer*; **every clip** has a caption/description that states what happens and when.

### 15.1 Example alt texts (charts and maps)

| Component | Alt text / summary |
|---|---|
| `CourtMap` (presence) | "Court map showing where you stood while the shuttle was in play. You were most often near the middle of your half, slightly towards the back. Based on 31 rallies." |
| `CourtMap` (rally path) | "Court map of rally 14. The rally went back and forth 12 times, mostly between the back corners, ending near the net on your side." |
| `RallyTimeline` | "Timeline of 36 rallies. Rallies 9, 14 and 27 are marked as moments. Rally 14 is the longest at 12 shots." |
| `ShotMix` | "Shots you played, by type: clears 14, lifts 9, drops 6, net shots 5. 12 shots could not be named. Shot names are a preview." |
| `TrendSmallMultiples` (longest rally) | "Longest rally in a match across three matches: 9, 11 and 14 shots." |
| `CoverageBar` | "We followed 31 of 36 rallies. 3 were filmed from another camera and 2 weren't visible." |
| `MomentumChart` | "Rally-by-rally lead for both players. The lead changed hands 4 times; the longest run was 5 rallies by you." |
| `ScoreStory` | "You led most of game 1. It tightened after 14–14 and finished 21–19." |
| `ShotRepertoireGrid` | "Shots spotted: 7 of 12. Not spotted yet: push, rush, block, cross-court net shot, long serve. Spotted means seen in your video, not mastered." |
| `JourneyTimeline` | "Your story: 4 entries — first match on 12 Oct, a first cross-court net shot on 19 Oct, a personal best on 26 Oct, a saved moment on 22 Nov." |

### 15.2 Example clip captions (text description for non-visual users)

| Clip | Caption |
|---|---|
| Long rally | "A 12-shot rally. Both of you stay near the back for the first eight shots, then you move forward and the rally ends near the net at 0:15." |
| Defence | "You are pushed to the back right corner and return a high shot, keeping the rally alive. The other player's next shot goes out." |
| Net exchange | "Six quick shots close to the net. The rally ends when the shuttle drops just over the net on your side." |
| Close point | "A tight point at 20–20. The rally lasts 9 shots and ends with a shot into the net." |
| Fun (opt-in) | "A lucky return — the shuttle clips the top of the net and drops over. Both players laugh." *(only if the player added this; we don't describe emotions we infer)* |

---

## 16. Localisation guidance (**hypotheses to validate with players**)

> Do not assume a language mix. Research first (file 12): which language players use for sport, WhatsApp and apps; which terms they use for shots; whether they prefer English with local-language support.

1. **Hinglish/Hindi and other regional languages.** Many Indian recreational players probably say *smash, drop, clear, net, rally, shuttle* in English even when speaking Hindi or another language (**hypothesis**). Plan for **English shot names with a short gloss** and test whether a full translation helps or confuses. Validate with at least Hindi, Tamil, Telugu, Kannada, Marathi, Bengali speakers before choosing a launch set.
2. **Text expansion.** Reserve **+30 %** width for most translations; **+50 %** for narrow controls (chips, tabs, bottom-bar labels); Devanagari and Dravidian scripts need more line-height (≥ 1.6) and larger minimum sizes. These are planning figures to confirm with real translations, not facts.
3. **No concatenation.** Whole sentences with ICU placeholders and plural rules (`{n, plural, …}`); never build "You played " + n + " rallies". Gendered languages: avoid addressing the player by gender; use constructions that don't need it; never guess a partner's or opponent's gender (use the nickname).
4. **No idioms, no wordplay, no sports slang** in core feedback; keep sentences short enough to translate well (§14 limit applies).
5. **Numerals and dates:** respect locale (Latin vs native numerals as the user prefers, `d MMM`), but keep scores in Latin digits for readability; time formats follow locale.
6. **Right-to-left** (e.g. Urdu): not in scope at launch; the layout uses logical CSS properties (`margin-inline`, `inset-inline`) now so RTL is possible later.
7. **Tone transfers poorly:** the *Direct / Balanced / Coach-guided* distinction must be re-validated per language — directness norms differ; have native-speaking coaches review each tone.
8. **Voice and audio** (spoken recap) is out of scope; if added, every spoken line has the same evidence rules and a transcript.
9. **Privacy and consent text** is legally sensitive: translate with legal review, not machine translation alone.
10. **Process:** messages live in `messages/{locale}.json` keyed by the ids in this file; English is the source; translators receive screenshots from the dev gallery (file 07 §13.6) and the claim templates with slot descriptions.

---

## 17. Button and label glossary

| Concept | Label | Never |
|---|---|---|
| Start a new analysis | **Add a match** | "Analyse video", "Upload" as the primary label |
| See footage for a claim | **Watch this** | "Evidence", "Source", "Citation" |
| Play a clip | **Watch** | "Play now!!" |
| Keep a moment | **Save** / Saved | "Like", "Favourite" (♡ is the icon; the word is Save) |
| Share | **Share…** (opens a dialog) | "Post", "Publish", "Send to everyone" |
| Correct our analysis | **Fix this** | "Report error", "That's wrong" |
| Confirm our analysis | **Looks right already** | "Verify", "Approve" |
| Skip a step | **Skip** / **Not now** | "Maybe later!" |
| Leave without choosing | **Done for now** | "Close", "No thanks" |
| Pick a focus | **Pick as my focus** | "Set goal" |
| Compare matches | **Compare** | "Versus" |
| Open detailed analysis | **Deep dive** | "Advanced analytics" |
| Court setup | **Place your court** | "Calibrate" |
| Whose are these | **You** / nickname | "Player 1" |
| Show more detail | **Look closer** | "Expert mode" |
| Delete | **Delete match** (danger) / **Keep it** (safe) | "Remove", "Cancel" for the safe option |
| Download | **Take it with you** (section) · **Download PDF** | "Export data" in player areas |
| Ask the assistant | **Ask about this match** | "Chat with AI coach" |
| Change depth | **Quick · Guided · Advanced** | "Beginner · Pro" |
| Change preset | **Relax · Explore · Improve · Compete** | "Casual · Hardcore" |
| Certainty | **Checked · Looks right · Worth a look** | "Verified · High/Medium/Low confidence" |
| Missing data | **Not enough to say** | "N/A", "0", "Error" |
| Capability | **Preview** | "Beta", "Experimental" (unless in settings) |

Section names (final): **Home · Matches · Moments · Progress · Together · Explore**; inside a match: **Moments · My game · Together · Deep dive**; inside Deep dive: **Story · Rallies · Shots · Court · Compare · Ask**; account: **Profile · Preferences · Privacy · Notifications · Accessibility · Help**.

---

## 18. Copy QA checklist (before a string ships)

1. **Whose voice?** Reads like a friend who watched with you; no hype, no scolding.
2. **Which layer?** Measurement / classification / interpretation / recommendation — and only one.
3. **Is it about the situation, not the person?** Search for "you are", "your weakness", "you lack".
4. **Is every number sourced and does it have a unit and a denominator?** No percent without `n of m`.
5. **Can the player open the footage behind it** ("Watch this"), or has the claim been withheld?
6. **Is certainty stated in words** (Checked · Looks right · Worth a look) — never a percentage?
7. **Is there an honest limit** where the data is thin (Preview, coverage, sample)?
8. **Is the interpretation conditional** (may / might / could) and are alternatives shown?
9. **Is any recommendation optional, single and feasible** ("If it helps…")? No "must/should".
10. **After a loss or low coverage, is it still kind and useful?** Walk it through §4.2.
11. **Does it work in all three tones** with identical facts (§2)?
12. **No streak, guilt, FOMO, comparison with others, calories, injury or emotion inference.**
13. **Plain words:** grade 6–8, ≤ 22 words per sentence, no idioms, sentence case.
14. **Buttons are verbs and match the glossary** (§17).
15. **Demo/sample strings are labelled as sample** and demo actions say "Demo only".
16. **Slots resolve** — a string with a missing slot does not render.
17. **Accessible:** link text makes sense alone; errors say what happened and what to do; alt text states question + answer.
18. **Translatable:** whole sentence with ICU plurals; no concatenation.
19. **Lint passes** (§14) with zero errors; warnings reviewed.
20. **Pilot check:** at least one real player has read it and could say, unprompted, what it means and what it does *not* mean.
