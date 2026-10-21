# Badminton Analytics for Amateur Players

## Product, Sports Science, Experience Design, and Engineering Blueprint

**Version:** 2.0 --- Integrated product blueprint\
**Status:** Product strategy and implementation specification\
**Audience:** Product designers, frontend/backend engineers,
computer-vision and ML engineers, sports scientists, badminton coaches,
researchers, and evaluators

------------------------------------------------------------------------

## Executive Summary

Build a player-controlled badminton experience platform that uses
reliable sports-video evidence to help people **enjoy playing, remember
meaningful moments, understand their own game, and choose whether they
want to improve**. It should serve recreational players first without
limiting the shared analytics foundation needed by club, competitive,
and professional players.

The product is not a statistics dashboard with badges attached. It is
not an automated coach that claims to know why every rally was won or
lost. It is not a medical device. It is a trustworthy companion that
turns badminton footage into inspectable evidence, understandable
meaning, and optional next actions.

The core loop is:

**Chosen purpose → trustworthy evidence → understandable meaning →
optional next action → later reflection.**

The primary product promise is:

> Every player should be able to find something meaningful in their
> session---whether that is a memorable rally, a personal best, a shared
> moment, or a useful observation---without needing to win, train
> seriously, or become a technical analyst.

This blueprint unifies recreational experience design with the existing
badminton analytics pipeline: shuttle and player tracking, court
mapping, pose and racket-related cues, stroke recognition, rally
segmentation, scoring, highlight generation, and agent orchestration.
The recommended architecture is a **shared deterministic evidence core
with multiple experience layers**: recreational, improvement-oriented,
competitive, professional, and coach/team.

### Product decisions at a glance

1.  **Sport first, app second.** A short useful review is better than
    prolonged engagement.
2.  **Value before configuration.** Show a sample and ask at most one or
    two skippable purpose questions.
3.  **Evidence before authority.** Every important claim can be
    inspected in its source clip and metric definition.
4.  **Self-reference by default.** Compare a player with their own
    comparable history before comparing them with others.
5.  **No universal player score.** Keep enjoyment, technical success,
    learning process, sporting outcome, and well-being separate.
6.  **No forced streaks or guilt mechanics.** Breaks are normal;
    returning should feel welcoming.
7.  **Confidence must be earned.** No fabricated highlights, unsupported
    causal explanations, or uncalibrated probability displays.
8.  **Private by default.** Analyzing a video does not imply permission
    to share it or train models on it.
9.  **Correctability is infrastructure.** Players and coaches can flag
    errors; corrections visibly propagate.
10. **Progress is a hypothesis supported by repeated evidence.** A
    single match does not prove improvement.
11. **Personalization changes order and language, not truth.** The
    evidence standard is the same in every mode.
12. **Successful non-use is legitimate.** A player may save a clip,
    enjoy the match, close the app, and have received full value.

------------------------------------------------------------------------

# 1. Product Foundation

## 1.1 Product definition

A player-controlled badminton performance and experience companion that
converts video into understandable, inspectable evidence; helps players
decide what is worth noticing and what to do next, if anything; and
preserves their sports memories. The product should be useful for a
person who plays once a month for fun as well as for a serious athlete
reviewing tactical patterns.

It has four product roles, in priority order:

1.  **Trustworthy mirror:** shows what happened and what the system can
    support.
2.  **Memory keeper:** preserves the rallies, achievements, and shared
    moments the player values.
3.  **Contextual learning companion:** connects a recurring pattern to
    an optional, testable practice idea.
4.  **Performance workspace:** supports deeper event analysis, coach
    collaboration, and tactical preparation for users who want it.

The system must never become an authority on a player's worth,
personality, emotional state, medical condition, or future sporting
potential.

## 1.2 The real job to be done

Different players arrive with different jobs. The product should support
these jobs as session-level choices rather than permanent identity
labels.

  -----------------------------------------------------------------------
  Player job              What the player may be  Product response
                          asking                  
  ----------------------- ----------------------- -----------------------
  Enjoy and remember      "What was the best      Short reel, saved
                          part?"                  rally, personalized
                                                  story

  Feel welcome            "Did I do anything      One verified positive
                          well?"                  moment, plain language,
                                                  no grading

  Understand my game      "What actually          Match story, rally
                          happened?"              timeline,
                                                  evidence-linked
                                                  observations

  Notice progress         "Am I getting better?"  Comparable-session
                                                  trend with sample size
                                                  and limitations

  Explore skills          "What can I try?"       Optional challenge or
                                                  shot exploration

  Practice with purpose   "What should I work     One editable, feasible
                          on?"                    experiment grounded in
                                                  recurring evidence

  Compete                 "Which patterns affect  Tactical sequences,
                          outcomes?"              scoring context,
                                                  opportunity-adjusted
                                                  metrics

  Collaborate             "Can my coach or        Permissioned playlists,
                          partner review this?"   annotations,
                                                  disagreement and
                                                  correction

  Be active               "How much did I move?"  Carefully qualified
                                                  activity estimates, not
                                                  medical conclusions

  Simply play             "Can I use this without Recording, saving, and
                          analysis?"              sharing controls
                                                  without forced reports
  -----------------------------------------------------------------------

"Just keep the moments" is a valid successful outcome. The product
should not pressure every recreational user to become
improvement-oriented.

## 1.3 North-star measure and activation

**North-star proposal:** the percentage of completed sessions in which a
player receives and understands one credible, personally relevant value
outcome: a meaningful clip, a verified insight, or a useful personal
milestone.

This is a product hypothesis to validate, not an established industry
metric.

**Activation proposal:** after the first usable session, the player can
correctly identify one finding from its evidence, or save a clip they
personally value. Account creation, onboarding completion, upload
completion, and dashboard views are not activation by themselves.

**Value model (a conceptual design aid, not a validated equation):**

`Perceived value = credible evidence × personal relevance × usefulness − capture effort − interpretation effort − emotional cost − privacy risk`

If reliability or relevance approaches zero, more charts and more
engagement mechanics will not repair the experience.

## 1.4 Keep outcome layers separate

  -----------------------------------------------------------------------
  Layer                   Example                 Does not prove
  ----------------------- ----------------------- -----------------------
  Technical processing    Video decoded and       Events are correct
                          analyzed                

  Event validity          Rally boundary and      The interpretation is
                          player identity         meaningful
                          verified                

  Product value           Player saves a clip or  The player improved
                          understands an insight  

  Learning process        Player chooses and      The focus caused
                          revisits a focus        improvement

  Sporting outcome        A metric changes across Analytics caused the
                          comparable matches      change

  Well-being and          Player reports          More app usage is
  participation           enjoyment and           inherently good
                          voluntarily returns     
  -----------------------------------------------------------------------

Never collapse these layers into a single "improvement score,"
"badminton IQ," or "player potential" number.

## 1.5 Non-goals

Do not ship features that imply:

-   Injury diagnosis, medical advice, or medical-grade fitness
    measurement.
-   Automatic inference of anxiety, confidence, motivation, personality,
    intent, or enjoyment from facial expression or body posture.
-   Certified line calling or officiating from ordinary camera footage.
-   Guaranteed shuttle speed, calories burned, or biomechanical
    correctness from arbitrary footage.
-   A universal skill ranking that is valid across ages, abilities,
    cameras, opponents, and playing conditions.
-   Causal explanations for a lost rally without enough evidence.
-   Public opponent dossiers or covert player surveillance.
-   Automatic public posting of clips.
-   Real-time tactical instructions during official competition unless
    explicitly designed and permitted for that context.
-   "Improvement" claims based on one unusually good or bad session.

------------------------------------------------------------------------

# 2. Player Segments, Purpose, and Depth

## 2.1 Treat purpose as a changing session preference

Purpose, skill level, context, desired effort, accessibility needs, and
coaching access are separate dimensions. A person can be recreational
today and competitive tomorrow. Store preferences as editable defaults,
not fixed identity labels.

### Working segments (hypotheses to validate)

  -------------------------------------------------------------------------------------
  Segment                 Main job       Default depth   First value    Main risk
  ----------------------- -------------- --------------- -------------- ---------------
  Recreational/social     Enjoy and      Quick           Best moments   Turning leisure
                          remember play                  and short      into evaluation
                                                         recap          

  New/restarting          Feel welcome   Quick           One positive   Embarrassment
                          and see                        observation    or jargon
                          something                      and selected   
                          achievable                     rally          

  Improvement-oriented    Understand one Guided          One strength   Generic advice
  amateur                 thing to try                   and one        or overtrust
                                                         opportunity    

  Club/competitive        Review tactics Advanced        Rally          Incorrect
                          and scoring                    sequences and  tagging
                          patterns                       context        destroys trust

  Professional/advanced   Add evidence   Advanced        Auditable      Opaque
                          to expert                      events,        aggregation and
                          analysis                       filters,       loss of control
                                                         exports        

  Coach/training partner  Have a         Collaborative   Shared         Evidence
                          grounded                       annotated      becoming
                          conversation                   playlist       surveillance

  Returning after a break Resume without Quick--Guided   Fresh baseline Punitive
                          shame                          and relevant   comparison with
                                                         clip           former self
  -------------------------------------------------------------------------------------

These are research hypotheses, not immutable market categories. Validate
them through interviews, observed sessions, and longitudinal product
data.

## 2.2 Three depth modes, same factual standard

  -----------------------------------------------------------------------
  Design dimension  Quick             Guided (default   Advanced
                                      for improvement)  
  ----------------- ----------------- ----------------- -----------------
  Language          Plain, short      Plain with inline Technical
                                      definitions       terminology with
                                                        definitions on
                                                        demand

  Opening           Match story and   Story, one        Event table,
                    best moments      strength, one     filters, coverage
                                      optional          and limitations
                                      opportunity       

  Visuals           Clips and         One court map or  Distributions,
                    annotated moments trend where       timelines, event
                                      useful            table, export

  Recommendation    Hidden unless     One editable      Competing
                    asked             focus             hypotheses and
                                                        alternatives

  Evidence          One tap           One tap           Direct from event
                                                        rows

  Main user benefit Fast enjoyment    Understand and    Audit and
                                      choose            investigate
  -----------------------------------------------------------------------

Personalization may change order, density, and language. It must never
change the underlying factual standard. Show why content is displayed
and offer **Change / Reset / Show all**.

## 2.3 Purpose selector

Offer up to two optional choices, always skippable and editable per
session:

-   **Keep the moments** --- enjoyment, memory, identity.
-   **Understand my game** --- curiosity and self-understanding.
-   **Choose something to practice** --- mastery and learning.
-   **Prepare to compete** --- tactics and opponent context.
-   **Discuss with someone** --- coach, partner, or club.
-   **Just play** --- no analysis or recommendations beyond the basic
    session record.

Do not ask a long questionnaire before delivering value. Ask about
purpose before or after the first session only when the answer will
materially change the experience.

------------------------------------------------------------------------

# 3. Behavioral Science Translated into Product Decisions

This section translates research-informed concepts into product
mechanisms. General sport, exercise, education, and HCI evidence does
not automatically prove that a specific badminton feature will work.
Treat the transfer as a hypothesis and test it.

## 3.1 Autonomy, competence, and relatedness

Self-Determination Theory highlights autonomy, competence, and
relatedness as important needs in motivation.

  -----------------------------------------------------------------------
  Need                    Product design          Avoid
  ----------------------- ----------------------- -----------------------
  Autonomy                User chooses purpose,   Forced goals, mandatory
                          depth, focus, clip      analysis, bundled
                          visibility, challenge,  consent
                          and notification        
                          settings                

  Competence              Show specific, credible Generic praise, ability
                          progress and manageable labels, impossible
                          experiments             goals

  Relatedness             Shared doubles          Public humiliation,
                          memories, partner       unrequested rankings,
                          playlists, respectful   social pressure
                          group milestones        
  -----------------------------------------------------------------------

## 3.2 Self-efficacy and credible mastery

Confidence should come from concrete evidence and attainable action, not
inflated praise.

Build: - A first-successful-shot milestone only when the event is
verified and historical coverage is sufficient. - Replayable examples of
a player's own successful execution. - Small, controllable
experiments. - Progress language that recognizes effort and evidence
without guaranteeing results. - A "not enough evidence yet" state that
feels normal, not punitive.

Avoid: - "You are becoming elite" after one good match. - Treating a
missed shot as a stable weakness. - Inferring self-confidence from
movement or facial expression. - Automatically raising the difficulty
after every success.

## 3.3 Goal setting and feedback

Use controllable process goals where they fit the player's chosen
purpose. Outcome goals remain legitimate for competitive players but
should not be forced on recreational users.

Examples: - "Try using a clear to reset the rally when it is
appropriate." - "Notice whether you can keep more neutral rallies
alive." - "Explore one shot type you have not seen in your recent
sessions." - "Save one rally you enjoyed."

The player can accept, edit, swap, dismiss, or postpone a suggested
focus. The system should not assume that a recommendation was practiced
merely because it was viewed.

## 3.4 Feedback timing and attentional focus

Evidence on feedback frequency, self-controlled feedback, and
attentional focus is mixed across tasks and populations. Do not
hard-code one universal schedule.

Design: - During recreational play: default to no interruptions. - After
play: show a concise recap. - During guided review: offer optional
external-focus cues and one experiment. - For coaches: permit a
different feedback schedule and annotation workflow. - Let players
control whether feedback appears immediately, after the session, or only
on request.

Test the effects on comprehension, retention, perceived pressure, and
later performance rather than assuming a single timing policy is best.

## 3.5 Emotion and attribution

Emotional states are not reliably inferable from a loss, posture, facial
expression, or celebration. Never auto-label a player as frustrated,
anxious, unmotivated, or confident.

Use neutral, optional prompts: - "What would help most now: keep the
moments, understand the match, or choose a practice idea?" - "Would you
like to review this now or later?" - "Was this clip useful to you?"

After a loss, provide the same choices as after a win. Separate the
match result from learning value. Do not force celebratory animations.

## 3.6 Flow, cognitive load, and interface complexity

-   Put one useful priority above the metric wall.
-   Make the first screen scannable in seconds.
-   Use progressive disclosure: **Summary → Evidence → Workspace**.
-   Show charts only when they help answer a question or choose an
    action.
-   Do not show all available metrics merely because they exist.
-   Preserve a clear exit and resume path.
-   Use plain language by default, with technical definitions one tap
    away.

## 3.7 Gamification and habit

Gamification effects vary and may fade. Rewards can support value but
should not replace it.

Launch with: - Personal records. - Skill discovery. - Meaningful clip
collections. - Optional challenges. - Shared partnership milestones. -
Participation recognition without judgment.

Do **not** launch with: - Punitive daily streaks. - Lost progress for
missed sessions. - Endless points, loot-box mechanics, or random
rewards. - Leaderboards as the default home screen. - Notifications
designed to exploit guilt or fear of missing out.

If streaks are ever tested, make them opt-in, forgiving, weekly or
event-based, and easy to disable. Measure harm as well as engagement.

## 3.8 Social comparison

Default to a player's own comparable history. Social comparison can
inspire or discourage and depends on context.

Later, test opt-in bounded comparisons among peers who consent and are
reasonably comparable. Show the reference group, metric definition, and
sample size. Never imply that an unadjusted ranking is a universal
measure of skill.

## 3.9 Sustainable participation

The goal is a valuable sporting life, not maximum screen time. A player
may use the product intermittently, take a break, or choose a session
with no analysis.

-   Resume without penalty.
-   Do not send "you are falling behind" messages.
-   Let the player pause all notifications.
-   Reward participation only when the player values it.
-   Do not escalate activity recommendations after a user reports
    discomfort or asks for fewer prompts.
-   Measure voluntary return and reported experience, not daily active
    use alone.

------------------------------------------------------------------------

# 4. Experience Principles and Required UI Behavior

## 4.1 Core principles

1.  **Sport first, app second:** optimize the player's time on court.
2.  **Value before configuration:** show a sample or first useful result
    before asking for detailed preferences.
3.  **Evidence before authority:** every material claim opens supporting
    footage and metric details.
4.  **One useful priority beats ten metrics:** rank and suppress; reveal
    more on demand.
5.  **Choice with structure:** recommend one option with a reason, but
    allow edit, swap, dismiss, and reset.
6.  **Self-reference before social comparison:** use comparable personal
    baselines by default.
7.  **Confidence must be earned:** praise specific verified evidence;
    show sample size.
8.  **Uncertainty is part of the interface:** coverage, reliability, and
    missing data are visible.
9.  **Loss is not failure:** keep result and learning value separate.
10. **Intermittent use is legitimate:** pause, export, leave, and resume
    gracefully.
11. **Depth is available, never imposed:** experts can inspect
    event-level evidence.
12. **Humans stay accountable:** player and coach can annotate, dispute,
    and correct.
13. **Privacy is a feature:** analyze ≠ share ≠ train.
14. **Every mechanic needs a value theory and harm test.**
15. **Correctability is infrastructure:** visible corrections propagate
    to affected summaries.
16. **No forced emotional interpretation:** ask, do not infer.
17. **Accessibility is core:** readable typography, contrast, captions,
    reduced motion, touch targets, and low-jargon explanations.

## 4.2 Emotional moments and interface response

  -----------------------------------------------------------------------
  Moment                  Risk                    Required response
  ----------------------- ----------------------- -----------------------
  First recording /       Embarrassment           Private start, selected
  seeing oneself                                  clips, controlled
                                                  sharing

  After a loss            Avoidance or            Quick recap / deep
                          disappointment          review / review later;
                                                  neutral facts

  After a win             Uncritical confidence   Specific evidence; no
                                                  outcome-only confetti

  Seeing a weakness       Shame or defensiveness  Observation language,
                                                  clip first, optional
                                                  action

  Frustrating rally       Irritation              No blame during play;
                                                  optional reset

  Plateau                 Doubt                   Explain uncertainty and
                                                  comparable sample;
                                                  revisit goal

  Return after a break    Vulnerability           Fresh baseline; no
                                                  regression alarm

  Comparing with others   Inspiration or          Let the player choose
                          inadequacy              self, peer, or expert
                                                  reference

  Coach criticism         Hurt or insight         Preserve evidence;
                                                  allow player response

  Personal best           Satisfaction            Show definition and
                                                  context; do not
                                                  auto-escalate target
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 5. Full Feature Catalogue

The catalogue is broad by design. It is not a commitment to build every
feature in the first release.

## 5.1 Layer A --- The Joy and Memory Layer

This is the recommended entry point for recreational users.

### Personal highlights

-   Best verified rally.
-   Longest rally and fastest reliably measured exchange.
-   Best smash or attacking sequence when stroke classification is
    reliable.
-   Best drop, clear, drive, net shot, backhand, or cross-court moment
    when identifiable.
-   Defensive recovery, difficult return, and rally-saving moment.
-   Comeback sequence, match-point save, deuce exchange, and winning
    point when score data is reliable.
-   Personal-best event compared with past sessions.
-   A player's chosen favorite clip.
-   A short session reel with optional narration.

### Fun and social moments

-   Celebrations, high-fives, encouragement, and sportsmanship where
    visible and permissioned.
-   Lucky shot or unexpected successful return.
-   Friendly blooper only after explicit approval.
-   Best moment with a named or nicknamed partner.
-   Doubles teamwork and rescue sequences.
-   Shared team reel.

Do not label someone clumsy, incompetent, or embarrassing. Avoid
interpreting facial expression as emotion. If a clip contains bystanders
or non-consenting participants, suppress it from shareable output or
apply the configured privacy policy.

### Personal sports story

Maintain a timeline of meaningful, verified events: - First saved
rally. - First verified example of a shot type. - Longest rally personal
best. - First approved shared highlight. - Returning after a break, if
the player wants participation milestones. - Favorite partners and
shared memories, subject to consent. - Player-written notes and selected
focus.

The system should not fabricate a milestone to ensure every session has
a highlight. If no reliable event exists, offer a neutral recap or let
the player select a moment manually.

## 5.2 Layer B --- Personal Progress

  -----------------------------------------------------------------------
  Capability              Definition /            Guardrail
                          requirement             
  ----------------------- ----------------------- -----------------------
  Shot repertoire         Distinct shot types     "Observed" is not the
                          observed with adequate  same as mastered
                          classification          
                          reliability             

  Rally participation     Number and duration of  Identity and rally
                          attributable rallies    boundaries must be
                                                  reliable

  Return consistency      Successful attributable Show denominator and
                          returns / eligible      exclusions
                          observed return         
                          attempts                

  Defensive resilience    Verified returns after  Opportunity-adjusted;
                          defined attack          do not penalize lack of
                          situations              opportunities

  Net-play history        Verified net exchanges  Camera perspective may
                          and outcomes            obscure contact

  Placement variety       Distribution across     Landing point must be
                          calibrated court zones  observable

  Movement coverage       Player positions mapped Camera calibration and
                          to court regions        occlusion matter

  Personal records        Best metric under a     Do not compare
                          stable definition and   incompatible camera
                          comparable conditions   setups

  Consistency trend       Repeated measures       Show sample size and
                          across comparable       variability
                          sessions                

  Focus history           Chosen, reviewed,       Do not infer practice
                          practiced, and later    from viewing
                          demonstrated states     

  Player reflection       Optional self-report of Never infer
                          usefulness, confidence, psychological state
                          or enjoyment            from video
  -----------------------------------------------------------------------

### Metric contract

Every displayed metric must define: - What counts in the numerator. -
What counts in the denominator. - Which events are excluded and why. -
Minimum sample size. - Supported camera and game conditions. - Identity
and event confidence requirements. - Whether the metric is descriptive,
estimated, or inferred. - Comparison baseline and time window. - Known
failure modes. - Whether changes are statistically or practically
meaningful enough to describe.

If a metric lacks a stable definition or validated detection quality,
keep it internal or label it as experimental. Do not put it in a
polished player-facing chart merely because it is computable.

## 5.3 Layer C --- Optional Challenges

Challenges should fit natural play and be easy to ignore.

  -----------------------------------------------------------------------
  Challenge         Purpose           Example           Measurement
                                                        requirement
  ----------------- ----------------- ----------------- -----------------
  Rally Explorer    Enjoy longer      Personal best     Reliable rally
                    exchanges         rally length      segmentation

  Shot Explorer     Discover          Several verified  Stroke
                    repertoire        shot types in a   classification
                                      session           

  Court Explorer    Experiment with   Explore different Court mapping and
                    placement         calibrated zones  landing estimate

  Doubles Duo       Celebrate         Both partners     Player
                    cooperation       contribute to a   attribution
                                      rally             

  Defence Hero      Recognize         Verified          Context and
                    resilience        difficult return  outcome

  Just Showed Up    Participation     Complete a        Session detection
                                      session           or user
                                                        confirmation

  Personal Best     Mastery           Exceed own prior  Comparable
                                      result            history

  Partner Memory    Relatedness       Save a shared     Consent and
                                      rally             identity

  Calm Review       Self-regulation   Choose review     No behavioral
                                      later or no       pressure
                                      review            
  -----------------------------------------------------------------------

Do not force a player to change tactics to satisfy a challenge. Avoid
assigning unsafe or overly strenuous challenges based on age or body
appearance. The user chooses whether to participate.

## 5.4 Layer D --- Singles Recognition

Retain existing categories while broadening the definitions beyond power
and winning.

  -----------------------------------------------------------------------
  Category                            Examples
  ----------------------------------- -----------------------------------
  Power                               Best smash, jump smash when
                                      reliably detected, attacking
                                      sequence

  Skill discovery                     First verified backhand, net shot,
                                      clear, drop, cross-court shot

  Defence                             Difficult return, recovery,
                                      defensive sequence

  Rally craft                         Long rally, varied exchange,
                                      sustained neutral rally

  Precision                           Verified landing in a calibrated
                                      region

  Resilience                          Rally-saving return, comeback
                                      contribution

  Personal progress                   New record, repeatable successful
                                      shot, consistency milestone

  Fun                                 Lucky Legend, Unexpected Return,
                                      approved funny moment

  Participation                       Session milestone, new partner,
                                      return after break

  Player-selected                     Favorite moment or custom award
  -----------------------------------------------------------------------

Awards such as Smash King/Queen, Defence Hero, Net Ninja, Rally
Champion, Comeback Champion, Precision Player, Lucky Legend, and Best
Celebration can be optional labels. They must not be the only way to
receive recognition.

## 5.5 Layer E --- Doubles and Social Analytics

  -----------------------------------------------------------------------
  Category                Example                 Evidence requirement
  ----------------------- ----------------------- -----------------------
  Shared rally            Both partners           Stable identity
                          contribute to a rally   attribution

  Partner rescue          One partner recovers    Position and sequence
                          after the other is out  evidence; avoid blame
                          of position             

  Attack combination      Rear-court attack       Shot and role
                          followed by front-court classification
                          interception            

  Defensive partnership   Shared defensive        Rally context
                          sequence and            
                          counterattack           

  Fast exchanges          Drive battle or quick   Temporal resolution and
                          net exchange            event confidence

  Court coverage          Relative positioning    Court calibration and
                          and region coverage     player identity

  Synchronized movement   Similar timing or       Describe observation,
                          coordinated movement    not inferred intent

  Sportsmanship           Visible high-five or    Consent and reliable
                          celebration             event detection

  Partnership memory      Best shared rallies and Both users' privacy
                          milestones              settings

  Team progress           Pair's own              Stable pair identity
                          comparable-session      and conditions
                          metrics                 
  -----------------------------------------------------------------------

A single camera may not support precise rotation, communication, or
responsibility attribution. Do not claim to detect verbal communication
unless audio processing is explicitly supported, permissioned, and
validated. Prefer "both partners contributed to this rally" over
"perfect communication" when intent is not observable.

## 5.6 Layer F --- Activity and Wellness (later phase)

Potential capabilities: - Approximate active playing time. - Rally count
and duration. - Court movement estimates. - Relative movement-intensity
summaries. - Activity consistency across weeks. - Optional self-reported
readiness, tiredness, enjoyment, or discomfort. - General warm-up and
recovery education. - Wearable integration only when user-authorized and
appropriately validated.

Limits: - Video alone should not be treated as a reliable measure of
calories, cardiovascular fitness, injury risk, or medical readiness. -
Do not infer health conditions, age, disability, or vulnerability from
appearance. - Never encourage playing through pain. - Never turn fatigue
estimates into medical advice. - Use extra caution with older adults and
users who may have accessibility or health needs; ask what they want, do
not stereotype them.

## 5.7 Layer G --- Competitive and Professional Depth

The recreational experience must not constrain advanced users. Reuse the
same evidence core for: - Score-state and rally-phase filtering. - Shot
sequences before winning and losing points. - Serve and return
patterns. - Attack/defence transitions. - Opportunity-adjusted shot
effectiveness. - Court position and movement coverage. - Opponent
tendencies, only when data and permissions support the comparison. -
Comparable-match trends. - Coach annotations and shared playlists. -
Event-table export and audit. - Alternative hypotheses rather than
unsupported causal claims.

Advanced metrics must expose definitions, sample size, coverage, event
provenance, and known limitations. A professional player or coach should
be able to challenge a result rather than being forced to trust a black
box.

------------------------------------------------------------------------

# 6. The Post-Session Experience

The post-session experience is likely to be the most important product
surface for recreational users.

## 6.1 Three-layer recap

### Layer 1 --- Emotional recap

-   One memorable clip or short reel.
-   One verified positive moment when evidence permits.
-   Clear replay, save, delete, and sharing controls.
-   No metric wall.
-   No forced celebration based solely on winning.

### Layer 2 --- Personal recap

-   Match/rally summary.
-   Personal records.
-   One relevant observation.
-   Optional history comparison.
-   A clear explanation of what was measured and how much evidence
    supports it.

### Layer 3 --- Social recap

-   Shared doubles reel.
-   Partner contributions.
-   Approved clips for sharing.
-   Team milestones.
-   Optional friendly challenge for next time.

Each layer should be accessible without requiring the player to consume
the others.

## 6.2 Match report structure

Recommended order: 1. **What happened?** A short, neutral match story.
2. **A moment worth keeping.** The best verified clip or a
player-selected clip. 3. **What went well?** One specific,
evidence-backed strength. 4. **What might be worth exploring?**
Optional, context-sensitive observation. 5. **What can I do next?**
Optional experiment or no recommendation. 6. **Evidence and limits.**
Source clips, definitions, sample size, coverage, uncertainty. 7.
**Player control.** Save, correct, hide, delete, export, or share.

Do not force a "weakness" card into every report. A player who chose
"Keep the moments" may never need a practice recommendation.

## 6.3 Example copy

Good: - "You kept this rally alive for 12 shots. Watch the recovery at
the end." - "We detected more successful returns in this session, but
the number of eligible attempts was small. Treat this as an early
signal." - "This may be worth exploring: several rallies ended after a
short return to the middle. Open the clips to inspect the pattern." -
"We could not reliably identify every shot in this video, so the shot
breakdown is incomplete." - "No comparable trend yet. Play a few more
sessions or choose a different comparison."

Bad: - "Your footwork is terrible." - "You lost because you lack
confidence." - "Your badminton IQ improved 23%." - "You are guaranteed
to improve if you follow this plan." - "You have been inactive for 9
days. Don't lose your streak." - "Perfect communication detected" when
only movement is visible.

------------------------------------------------------------------------

# 7. Personalization and the Player Experience Agent

## 7.1 Agent responsibilities

Use a combination of deterministic services and language models. These
are logical responsibilities, not a requirement to run a separate LLM
for each one.

  -----------------------------------------------------------------------
  Service / agent                     Responsibility
  ----------------------------------- -----------------------------------
  Preference service                  Stores purpose, depth,
                                      accessibility, content and
                                      notification preferences

  Event understanding                 Converts verified event records
                                      into bounded descriptions

  Highlight curator                   Ranks eligible clips for a selected
                                      purpose

  Progress service                    Compares compatible sessions and
                                      flags sample limitations

  Challenge recommender               Suggests optional, feasible
                                      challenges

  Social curator                      Creates permission-aware shared
                                      moments

  Activity insights                   Summarizes validated movement and
                                      activity measurements

  Evidence retrieval                  Retrieves event records, source
                                      clips, metric definitions, and
                                      provenance

  Safety/privacy policy               Enforces consent, visibility,
                                      claims policy, and retention rules

  Session memory                      Stores player-approved memories and
                                      longitudinal summaries

  Narration model                     Produces clear language grounded
                                      only in approved evidence
  -----------------------------------------------------------------------

The LLM should not calculate the official score, invent event records,
overwrite metric values, or decide that an uncertain event is certainly
true. It should select from and explain validated evidence.

## 7.2 Grounded recommendation contract

Each insight should include: - `claim`: the plain-language
observation. - `claim_type`: descriptive, comparison, hypothesis, or
recommendation. - `evidence_refs`: event IDs and clip ranges. -
`metric_definition_id`: exact metric version. - `coverage`: relevant
video/time coverage. - `sample_size`: eligible observations. -
`reliability_state`: calibrated state, not raw uncalibrated softmax. -
`limitations`: relevant missing data or assumptions. -
`comparison_context`: baseline, time window, conditions. -
`next_action`: optional and user-controlled. - `visibility`: private,
shared with named people, or approved for publication. - `created_at`
and `model_version`.

If the evidence contract is incomplete, the claim should be withheld,
weakened, or converted into a question.

## 7.3 Example agent flow

1.  Video pipeline produces candidate events.
2.  Event verifier checks boundaries, player attribution, outcomes, and
    confidence.
3.  Deterministic analytics computes metrics with versioned definitions.
4.  Preference service selects the user's chosen purpose and depth.
5.  Evidence retrieval returns relevant clips and historical
    comparisons.
6.  Curation service ranks eligible moments.
7.  Policy layer removes disallowed content and claims.
8.  Narration model explains only the approved evidence.
9.  UI displays the claim with clip, definition, and uncertainty access.
10. Player can save, dismiss, correct, or give feedback.
11. Feedback updates future ranking only through a transparent,
    reversible policy.

## 7.4 Do not over-personalize

-   Do not infer emotional state, personality, or motivation from
    footage.
-   Do not create hidden psychological profiles.
-   Do not target vulnerable moments with persuasive notifications.
-   Do not use sensitive health or demographic information to manipulate
    engagement.
-   Do not automatically escalate challenge difficulty.
-   Let the user inspect, reset, and delete preferences and memory.

------------------------------------------------------------------------

# 8. Technical Architecture

## 8.1 Shared evidence core, multiple experience layers

``` text
Video / Live Stream / Optional Wearables
                  |
                  v
      Ingestion, Decode, Calibration
                  |
                  v
      Perception and Tracking Layer
  Shuttle | Players | Pose | Court | Racket/contact cues
                  |
                  v
       Match Understanding Layer
  Rally segmentation | Strokes | Score | Outcomes | Context
                  |
                  v
       Canonical Event Ledger
  Identity | Timestamps | Evidence refs | Confidence | Version
                  |
                  v
        Deterministic Metric Engine
  Definitions | Denominators | Eligibility | Comparability
                  |
                  v
     Player/Session/Pair Memory Store
  Preferences | Verified milestones | History | Corrections
                  |
                  v
       Evidence Access and Policy Gate
  Consent | Visibility | Coverage | Claim rules | Retention
                  |
                  v
      Experience and Curation Services
  Highlights | Progress | Challenges | Social | Activity
                  |
                  v
      Grounded Narration / Optional LLM
                  |
                  v
       Quick | Guided | Advanced | Coach UI
```

The existing perception models and multi-agent harness should feed this
structure rather than bypass it. Competitive and recreational products
use the same verified events but differ in selection, depth, language,
and next-action policy.

## 8.2 Canonical event ledger

Recommended event fields:

``` json
{
  "event_id": "stable-unique-id",
  "session_id": "session-id",
  "event_type": "rally_end",
  "start_ms": 12400,
  "end_ms": 18600,
  "player_ids": ["player-a"],
  "team_id": "team-1",
  "event_payload": {},
  "evidence_refs": ["video-segment-ref"],
  "identity_state": "verified",
  "event_state": "verified",
  "reliability_state": "calibrated_high",
  "metric_definition_version": null,
  "model_versions": {},
  "coverage": {},
  "consent_scope": "private",
  "created_at": "ISO-8601",
  "supersedes_event_id": null
}
```

This is an illustrative schema, not a final database contract. Use
stable IDs, explicit lifecycle states, schema versioning, and
referential integrity. Do not encode raw confidence as a user-facing
probability unless it has been calibrated on representative target
footage.

## 8.3 Event lifecycle and correction

Use explicit states such as: - `candidate` - `needs_review` -
`verified` - `low_confidence` - `rejected` - `corrected` - `superseded`

Do not silently overwrite history. A correction should create an
auditable change, identify affected metrics and clips, and visibly
update downstream summaries. The UI should explain why a previous result
changed.

## 8.4 Metric registry

Every metric definition should specify: - Name and version. - Unit and
scope (player, pair, rally, session, match). - Numerator, denominator,
eligibility, and exclusions. - Supported camera/setup conditions. -
Minimum sample size. - Confidence/calibration policy. - Missing-data
behavior. - Comparison eligibility rules. - Known failure modes. -
User-facing explanation. - Owner and validation status.

Examples: - `return_success_rate_v1`: successful eligible returns
divided by reliably identified eligible return attempts. -
`rally_duration_v1`: end timestamp minus start timestamp for verified
rally boundaries. - `shot_repertoire_v1`: number of distinct shot
categories with at least the configured minimum verified examples. -
`court_region_coverage_v1`: unique calibrated regions visited, with a
specified sampling and occlusion policy.

Metric names and definitions must remain stable across versions or
explicitly identify a breaking change.

## 8.5 Confidence and coverage

Confidence is not a decoration; it controls whether the system is
allowed to make a claim.

-   Use calibrated reliability categories only after validation on
    target camera positions, lighting, player diversity,
    singles/doubles, and shuttle visibility conditions.
-   Do not display raw softmax scores as if they were probabilities of
    correctness.
-   Display the reason for uncertainty in plain language.
-   Show how much footage was analyzable and which events were excluded.
-   Require a larger evidence threshold for public awards, personal
    records, or claims that affect player identity.
-   Allow the system to abstain.

## 8.6 Session and player memory

Store: - User-selected purpose and depth. - Consent and sharing
permissions. - Verified session summaries. - Metric definition versions
and comparison eligibility. - Player-approved milestones and saved
clips. - Optional chosen focus and explicit reflection. - Corrections
and feedback. - Pair history only where participants have consented.

Prefer compact structured summaries and event references over
reprocessing all historical footage. Keep private player memory separate
from public/shared content.

## 8.7 Agent orchestration and performance

-   Use deterministic services for scoring, metric calculation, event
    validation, and permissions.
-   Use parallel processing for independent perception jobs where
    hardware and latency allow.
-   Cache reusable event and metric results by source/version.
-   Run expensive inference only when the selected capability requires
    it.
-   Generate deep reports asynchronously after the fast recap is
    available.
-   Keep live and post-session paths separate.
-   Add idempotency, retries, timeouts, backpressure, and job
    observability.
-   Avoid making a large multi-agent call for a task a deterministic
    function can solve.
-   Track latency and cost per session and per capability.

### Recommended execution paths

**Fast path:** ingest → essential tracking/events → session state →
basic verified recap.

**Post-session path:** richer stroke classification → historical
comparison → highlight curation → optional narration.

**Advanced path:** tactical sequences, additional pose analysis, deeper
opponent/context filtering, exports.

The interface must show processing state honestly. Do not present
pending or provisional analysis as final.

------------------------------------------------------------------------

# 9. Data, Privacy, Consent, and Safety

## 9.1 Consent model

Keep these permissions distinct: 1. Permission to record/process the
session. 2. Permission to identify a participant by name or persistent
identity. 3. Permission to save clips to an account. 4. Permission to
share with named people or a group. 5. Permission to publish externally.
6. Permission to use footage or derived data for model
improvement/training.

Consent for one purpose is not consent for another. Provide a clear path
to revoke permissions and delete eligible data. Account for venue rules
and bystanders.

## 9.2 Default privacy posture

-   Private by default.
-   Use nicknames or anonymous participant labels if preferred.
-   No automatic public sharing.
-   No public opponent profiles by default.
-   Minimize raw video retention; disclose the policy before upload or
    recording.
-   Separate raw footage, derived event records, and shared clips.
-   Encrypt data in transit and at rest, enforce authorization
    server-side, and audit sensitive access.
-   Provide export and deletion workflows.
-   Avoid storing face embeddings or biometric identity features unless
    strictly necessary, lawful, explicitly disclosed, and consented to.
-   Make coach/team access revocable and visible.
-   For minors, implement age-appropriate consent and safeguarding
    policies before enabling accounts or sharing.

## 9.3 Harm-aware design

Potential harms include shame, unwanted exposure, overtraining,
unhealthy comparison, false praise, inaccurate coaching, and privacy
loss. For every feature, document: - User value hypothesis. - Intended
beneficiaries and who might be excluded. - Failure modes and severity. -
Mitigations and kill criteria. - Consent requirements. - Evaluation
metric for harm. - Rollback plan.

A feature should be delayed if the team cannot explain what happens when
its detection is wrong.

------------------------------------------------------------------------

# 10. Information Architecture and Screens

## 10.1 Public website

-   Landing page with clear audience and value proposition.
-   Interactive short example.
-   Inspectable sample report with visible limitations.
-   "What we can and cannot analyze" page.
-   Recording guide: framing, court placement, lighting, permissions.
-   Pricing and equipment requirements before upload.
-   Privacy and data page in plain language.
-   Accessibility statement.
-   Research and validation page that distinguishes evidence from
    hypotheses.

## 10.2 Signed-in product

-   **Home:** resume the relevant task or show latest meaningful result.
-   **Sessions/Matches:** record/upload, status, reports, clips,
    corrections.
-   **Progress:** chosen focus and context-matched history.
-   **Explore:** optional challenges and skills.
-   **Library:** saved highlights, playlists, annotations, personal
    story.
-   **Partner/Team:** permission-gated shared sessions and doubles
    memories.
-   **Coach workspace:** authorized athletes, event evidence,
    annotations, exports.
-   **Settings:** purpose, depth, accessibility, notifications, privacy,
    data export/deletion, metric definitions, corrections.

Do not create a separate navigation section for every internal model or
analytics module. Organize the product around player questions.

## 10.3 Home-screen rules

For a new user: - Explain the product briefly. - Show a realistic
sample. - Offer a recording/upload path and a skippable purpose
choice. - Avoid a long questionnaire.

For a user with a processed session: - Show one relevant result and a
clear way to inspect evidence. - Offer "View all moments" and "Review
later." - Do not put a wall of charts above the result.

For a returning user: - Resume the last relevant task or offer the
latest session. - No streak-loss or regression message. - Allow "start
fresh" and "show all."

For an error or low-coverage session: - Explain what happened. -
Preserve any valid clips/results. - Give a specific fix where
possible. - Do not make the player repeat work without explanation.

## 10.4 Match-review interaction

Every insight card should include: - Short claim. - Why it may matter
(optional and conditional). - Source clip or event evidence. - Metric
definition and denominator. - Coverage and reliability explanation. -
Optional next action. - Save, dismiss, correct, and share controls as
appropriate.

Recommended states: - Loading. - Processing. - Ready. - Partially
analyzed. - Low coverage. - Needs review. - Failed but retryable. -
Unsupported recording. - Deleted or permission revoked.

Do not leave empty charts that look like zero values. Distinguish zero,
missing, not measured, not applicable, and insufficient evidence.

------------------------------------------------------------------------

# 11. Design System and Accessibility

## 11.1 Visual hierarchy

The visual design should feel like a calm sports companion rather than a
surveillance dashboard or casino-style gamification app.

-   Strong hierarchy, generous spacing, readable labels.
-   Video and evidence first; metrics second.
-   One primary action per card.
-   Use color as a supplement, never the sole carrier of meaning.
-   Avoid red/green framing of players as good/bad.
-   Keep celebrations brief and user-controlled.
-   Respect reduced-motion settings.
-   Avoid visual overload, excessive gradients, and dense data displays
    in Quick mode.

## 11.2 Data visualization rules

Choose a visualization based on the decision: - Timeline for event
sequence. - Court map for spatial coverage when calibrated. - Bar chart
for clear category comparison. - Line chart for repeated comparable
measures over time. - Clip strip for qualitative evidence. - Table for
advanced auditing and export.

Every chart needs a question, units, time window, sample size, and
definition. Do not use a chart when a sentence and a clip explain the
point more clearly.

## 11.3 Accessibility

-   Support keyboard navigation and screen readers.
-   Captions or textual descriptions for meaningful video events.
-   High contrast and scalable typography.
-   Large touch targets.
-   Plain-language explanations and optional technical detail.
-   Avoid relying on sound alone for alerts.
-   Reduced motion and no flashing effects.
-   Respect language preferences.
-   Offer controls that do not require precise gestures.
-   Design for varied vision, hearing, motor ability, and digital
    confidence without assuming that age predicts ability.

------------------------------------------------------------------------

# 12. Singles and Doubles Experience Examples

## 12.1 Singles: post-match example

**Opening:** "Here are three moments from your game."

1.  Best rally --- verified clip and rally length.
2.  Defensive recovery --- show the event and outcome, if reliable.
3.  Personal best --- compare with prior eligible sessions.

Optional: "Would you like to explore one pattern or keep the moments?"

Possible awards: - Rally Champion. - Defence Hero. - Shot Explorer. -
Personal Best. - Lucky Legend (opt-in). - Best Celebration
(consent-aware).

The system should not invent a shot category or declare a winner of a
subjective award without a clear rule.

## 12.2 Doubles: post-match example

**Opening:** "Your pair's moments from today."

1.  Shared rally with verified contributions from both partners.
2.  Defensive sequence that turned into an attack.
3.  Approved celebration or high-five.
4.  Pair-level record compared with the same pair's history, where
    enough data exists.

Optional: "Save this as a partnership memory?" The answer is private to
the user unless both participants' sharing permissions allow broader
visibility.

Possible awards: - Dynamic Duo. - Defence Duo. - Rescue Partner. - Power
Pair. - Partnership Milestone. - Best Team Celebration (opt-in).

Do not use pair analytics to assign blame to one partner. If a tactical
question is appropriate, present the sequence and invite review.

------------------------------------------------------------------------

# 13. Measurement and Experimentation

## 13.1 Product KPIs

  -----------------------------------------------------------------------
  Dimension                           Measures
  ----------------------------------- -----------------------------------
  Value                               Percentage of sessions with a
                                      meaningful clip or understood
                                      insight

  Trust                               Event accuracy, identity errors,
                                      correction rate, false achievement
                                      rate

  Comprehension                       Can users explain the finding in
                                      their own words?

  Enjoyment                           Optional player-reported enjoyment
                                      and recap usefulness

  Progress utility                    Players who find the history
                                      comparison relevant

  Return behavior                     Voluntary 7-day and 28-day return,
                                      sessions per active player

  Social value                        Approved clips shared, shared
                                      highlights viewed, pair
                                      participation

  Accessibility                       Task completion and error rates
                                      across access needs

  Privacy                             Consent failures, unauthorized
                                      access, complaints, deletion
                                      completion

  System quality                      Coverage, latency, cost, retry
                                      rate, failure rate

  Harm                                Reported shame, pressure, unwanted
                                      comparison, unsafe interpretation
  -----------------------------------------------------------------------

Do not optimize daily active use, time in app, or number of badges as
standalone goals.

## 13.2 Suggested experiments

### Experiment A: Recap format

Compare a short emotional recap with a metric-heavy report. Measure
usefulness, comprehension, and time to value---not just clicks.

### Experiment B: Personal progress

Compare no history, personal-baseline comparison, and personal-baseline
comparison with clip evidence. Test whether the comparison is understood
and trusted.

### Experiment C: Optional challenges

Test an opt-in challenge against no challenge. Measure participation and
enjoyment, but also pressure, dismissals, and negative feedback.

### Experiment D: Social recap

Test private individual highlights versus consent-based shared doubles
highlights. Measure perceived value and privacy comfort.

### Experiment E: Feedback timing

Compare post-session feedback with player-selected timing. Measure
comprehension, retention of the observation, perceived interruption, and
later performance when feasible.

Use appropriate randomization, pre-registered primary outcomes where
practical, and enough follow-up to distinguish novelty from sustained
value. Avoid presenting correlation as causation.

## 13.3 Interview and usability research

Recruit diverse players across: - Age groups and accessibility needs. -
Beginners, recreational regulars, club players, and advanced players. -
Singles and doubles. - Different levels of technology confidence. -
Players who want fun, improvement, fitness, competition, or social
connection.

Ask about actual recent behavior, not only hypothetical feature
preference: - "Tell me about the last time you wanted to play again." -
"What made a session worth remembering?" - "What would feel embarrassing
or intrusive in a sports app?" - "When would you prefer not to see
analysis?" - "Which statistic would you trust least, and why?" - "Show
me what you would do with this clip." - "What would make you delete the
video?" - "Would you still value the product if you did not improve
technically?"

Observe people using the prototype after a real session. Treat stated
enthusiasm as an initial signal, not proof of retention.

------------------------------------------------------------------------

# 14. Evaluation and Release Gates

No feature should ship to player-facing production only because the
model produces outputs.

## 14.1 Technical validation

-   Representative footage across camera positions, lighting, shuttle
    visibility, court conditions, singles/doubles, and player diversity.
-   Event-level precision/recall or suitable classification metrics.
-   Identity-switch and attribution error rates.
-   Rally boundary and score-state validation.
-   Calibration checks for any displayed reliability categories.
-   Coverage and failure-mode reporting.
-   Latency, cost, and resource profiling.

## 14.2 Product validation

-   Can the player understand the claim?
-   Can the player open its evidence?
-   Can they tell what the system did not observe?
-   Can they correct or dismiss it?
-   Does the insight match the player's chosen purpose?
-   Does the product remain useful after a loss or a poor-quality
    recording?
-   Does the experience work without creating a public identity or
    profile?

## 14.3 Release gates

1.  **Private internal evaluation:** no public claims.
2.  **Closed player pilot:** consented sessions, visible uncertainty,
    manual review where necessary.
3.  **Limited release:** only validated capabilities; monitoring and
    rollback.
4.  **Broader release:** evidence of reliable detection and positive
    user value.
5.  **Advanced metrics:** separate validation and expert review before
    exposure.

A feature should be disabled or downgraded when false claims, identity
errors, privacy issues, or harm reports exceed pre-agreed thresholds.
Define those thresholds before the experiment.

------------------------------------------------------------------------

# 15. Prioritized Roadmap

## Phase 0 --- Evidence and instrumentation foundation

-   Define canonical event schema and metric registry.
-   Establish event lifecycle and correction propagation.
-   Create supported-conditions matrix.
-   Implement consent and visibility policy.
-   Instrument technical coverage, latency, and error rates.
-   Create a representative validation set.

**Exit condition:** the team can explain where each displayed fact came
from and how it can fail.

## Phase 1 --- Joy Layer (MVP)

-   Reliable rally segmentation and player attribution for supported
    conditions.
-   Best-moment selection and simple session reel.
-   Private save/delete/share controls.
-   Singles and doubles basics.
-   Opt-in funny/social clips.
-   Short post-session recap.
-   Partial-analysis and failure states.

**Exit condition:** players value the recap; the system does not invent
events or expose non-consenting participants.

## Phase 2 --- Progress Layer

-   Persistent player profiles and session memory.
-   Stable metrics with denominators.
-   Personal records and comparable-session rules.
-   Evidence-linked insight cards.
-   Player corrections and feedback.
-   Clear distinction between reviewed, practiced, and later
    demonstrated.

**Exit condition:** users understand the comparison and trust its
limitations.

## Phase 3 --- Explore and Social Layer

-   Optional challenges.
-   Personal sports story.
-   Pair-level memory and shared playlists.
-   Adaptive curation based on explicit preference and feedback.
-   Bounded experiments for reminders and social features.

**Exit condition:** evidence of user value without increased shame,
pressure, or privacy concerns.

## Phase 4 --- Activity Layer

-   Validated movement and activity summaries.
-   Optional self-reported readiness and enjoyment.
-   General warm-up education.
-   Wearable integrations only where consented and supported.

**Exit condition:** accuracy, usefulness, and safety are validated for
the target use cases.

## Phase 5 --- Advanced performance and coach workspace

-   Tactical sequence analysis.
-   Advanced filters and exports.
-   Coach annotations and authorized sharing.
-   Alternative hypotheses and richer comparison controls.
-   More advanced biomechanical features only after validation.

**Exit condition:** expert users can audit and challenge outputs; claims
are suitable for the intended level of decision-making.

------------------------------------------------------------------------

# 16. Definition of Done for Every Insight

An insight is not complete until all applicable checks pass:

-   [ ] The player purpose makes this insight relevant.
-   [ ] The event and player identity are reliable enough for the claim.
-   [ ] The metric has a versioned definition.
-   [ ] Numerator, denominator, and exclusions are known.
-   [ ] The source clip or event evidence is accessible.
-   [ ] Coverage and meaningful uncertainty are communicated.
-   [ ] The wording describes observation before interpretation.
-   [ ] Causal claims are avoided unless supported by appropriate
    evidence.
-   [ ] Any recommendation is optional and feasible.
-   [ ] Privacy permissions allow this display and sharing scope.
-   [ ] The user can correct, dismiss, or hide the insight.
-   [ ] Corrections update dependent metrics and summaries.
-   [ ] Failure and insufficient-evidence states are designed.
-   [ ] The feature has a user-value hypothesis and harm test.
-   [ ] The evaluation plan includes technical and user outcomes.

------------------------------------------------------------------------

# 17. Research Foundation and Evidence Discipline

The platform's design should draw from several evidence families:

1.  **Self-Determination Theory and exercise motivation:** autonomy,
    competence, and relatedness.
2.  **Self-efficacy:** credible mastery experiences and attainable next
    steps.
3.  **Goal setting and self-regulation:** controllable process goals,
    reflection, and chosen focus.
4.  **Motor learning and augmented feedback:** feedback timing,
    attentional focus, practice context, and retention.
5.  **Achievement goal and motivational climate research:**
    mastery-oriented environments and the risks of social comparison.
6.  **Behavior-change and gamification reviews:** effects are variable
    and may decline; test sustained value and harms.
7.  **Human-computer interaction and trust:** progressive disclosure,
    explainability, user control, and correctability.
8.  **Accessibility and inclusive design:** adapt to actual user needs
    rather than age stereotypes.
9.  **Badminton-specific movement and participation research:**
    understand sport context, while avoiding overgeneralization from
    elite or structured settings.
10. **Privacy and safety engineering:** consent boundaries, data
    minimization, access control, and auditable changes.

### Evidence labels

Use explicit labels in internal documentation: - **Strong:** converging
reviews or meta-analyses, with direct relevance. - **Moderate:**
credible findings but heterogeneous or indirect. - **Limited:** narrow,
product-authored, or indirectly relevant evidence. - **Hypothesis:**
plausible product idea requiring direct validation.

No existing study validates this exact product or proves that a specific
highlight, badge, or UI will improve retention. Use research to form
better hypotheses, then validate with recreational and competitive
badminton players.

### Research and reference starting points

-   Self-Determination Theory overview:
    https://selfdeterminationtheory.org/the-theory/
-   World Health Organization, physical activity guidance:
    https://www.who.int/news-room/fact-sheets/detail/physical-activity
-   PubMed, systematic review on badminton health benefits:
    https://pubmed.ncbi.nlm.nih.gov/35897446/
-   PubMed, gamification and physical activity review:
    https://pubmed.ncbi.nlm.nih.gov/34982715/
-   PubMed, exercise motivation and behavior-change research can be
    explored through:
    https://pubmed.ncbi.nlm.nih.gov/?term=self-determination+theory+exercise+systematic+review
-   Google Scholar, badminton performance analysis:
    https://scholar.google.com/scholar?q=badminton+performance+analysis+computer+vision
-   Google Scholar, badminton movement and injury prevention:
    https://scholar.google.com/scholar?q=recreational+badminton+injury+prevention
-   Google Scholar, motor learning and feedback:
    https://scholar.google.com/scholar?q=motor+learning+self-controlled+feedback+systematic+review
-   Google Scholar, gamification and physical activity:
    https://scholar.google.com/scholar?q=gamification+physical+activity+systematic+review+meta-analysis

Verify the full text, population, study design, publication date, and
limitations before using any paper to justify a shipped product
decision. Do not cite a study as direct badminton evidence if it studied
a different population or activity.

------------------------------------------------------------------------

# 18. Final Product Vision

The system should help a player say:

-   "I can relive my best moments."
-   "I can understand my own game without being judged."
-   "I can see progress when there is enough evidence."
-   "I can share the experience with people I choose."
-   "I can explore improvement if I want to."
-   "I can simply play and enjoy myself."
-   "I can trust the system because it shows its evidence and admits
    what it does not know."

For recreational users, start with **Joy → Progress → Optional
Exploration → Social Memory → Activity Insights**. For competitive and
professional users, preserve the same trustworthy evidence core and
expose deeper tactical and technical tools.

The defining product advantage is not merely detecting a smash or
producing a polished video. It is making sophisticated badminton
analytics feel useful, respectful, and understandable to the person who
plays.

**The governing principle: the technology should adapt to the
player---not require the player to adapt to the technology.**
