# Highlights: product and visual design

## Scope and authorization

Add `/highlights` to Rally's primary navigation on `top10`. The user requested
design planning followed by sequential implementation and refinement. Work is
local and frontend-only. Do not run tests, builds, inference, media processing,
backend services or remote runtimes. Install nothing. Keep changes uncommitted.
Existing Moments, match analysis, accepted evidence and unrelated edits remain intact.

## Product question

Which parts of this session do I want to revisit, and what supports each one?

Audience: recreational singles and doubles players returning after a session.
Primary job: open a moment, understand why it is included, keep a personal pick.
Secondary job: distinguish observed results, subjective selections and missing evidence.
Mode: Operate, with media-led browsing. Preserve the existing Rally visual world.

## Inventory and truth

- Ten insight types, not a promise of ten supported results for every recording.
- Session and rally IDs, canonical frame ranges, shot counts and score availability.
- Physical participants, teams and scoring slots are separate objects.
- Existing ranked moments are suggestions, not independently verified annotations.
- Player picks are subjective and private local drafts in this increment.
- Existing cross-session name grouping cannot establish a personal record.
- A doubles formation does not establish a coverage mistake.
- Recorded smash/rally association is not immediate smash conversion.
- No production analytics are recalculated in the frontend.
- Example data is synthetic, named in the source selector, notice and detail view.
- No source video is supplied for the example; geometry is labelled illustration.
- No background analysis or model download is triggered by any Highlights control.

## Reference lock

The primary authority is Rally's incumbent `styles/tokens.css`, Archivo Variable,
224px sidebar, labelled navigation and semantic light/dark roles.

Studied through design-mcp on 2026-11-04:

- Loom library, screen `93ca9887-b084-4661-b743-7074ef8cd9ff`,
  https://www.loom.com/looms/videos : adopt thumbnail-first browsing and compact
  metadata. Reject repeated menus and its unrelated brand color.
- TwelveLabs library, screen `cfcce4bc-bc26-4b09-8afb-974a3303eb46`,
  https://playground.twelvelabs.io/indexes : adopt the clear distinction between
  sample material and owned videos. Reject destructive overlays as page structure.
- ElevenLabs style `031056ff-7af1-46db-8daa-115f731c5d26`,
  https://styles.refero.design/style/031056ff-7af1-46db-8daa-115f731c5d26 : borrow
  flat surfaces and quiet metadata, not its fonts, marketing scale or accent colors.
- Linear style `90ce5883-bb24-4466-93f7-801cd617b0d1` was considered for density;
  its dark marketing world is inappropriate for replacing an established app.

Skills: design-research, Taste (app-screen guidance), Impeccable (Operate mode,
craft floor and polish), design-motion-principles (Emil primary, Jakub secondary).
No installed skill named elonski or unslop was found; apply the available
anti-slop guidance instead. Impeccable's bundled engine is absent; no helper was
downloaded. Source review replaces automated/visual checks at the user's request.

## Composition exploration

All options preserve a 4px spacing grid, 32px desktop gutter, 16px mobile gutter,
12px surfaces and the existing typeface. No layout depends on stock match imagery.

1. Equal ten-tile grid: scannable, but gives an unsupported record and a real clip
   equal emphasis. Rejected as the primary composition.
2. Video-editor workbench: persistent player, dense rally list and review inspector.
   Strong for annotation, too operational for returning to a personal memory.
3. Featured moment + compact shortlist + grouped collection: selected. A moment
   gets visual priority while all ten types remain discoverable through filters.

Desktop structure:

    Title / introduction                     Add a moment
    Example / recordings       Session       Player or team
    Source notice
    Featured rally (about 2/3) | Worth another look (about 1/3)
    Collection tabs / category filters / search / count
    Moments to keep: varied clip tiles
    Match patterns: comparison tiles
    Your history: personal record and partnership tiles

On tablet the featured region becomes a single column with a horizontal shortlist.
On phone all content follows source order; cards become one column, controls wrap,
and six primary navigation destinations remain accessible with >=44px targets.
Detail review uses a focus-managed Radix sheet, full-width on narrow screens.
No separate modal is used merely to explain a number; definition details expand inline.

## Visual decisions

- Existing forest ink, sage surfaces and semantic accent roles across both themes.
- 28px page heading; 22px featured title; 16px tile titles; 13-15px body; 12px metadata.
- Flat sections, deliberate media/copy proportions, hairlines only where grouping helps.
- No gradients, glow, rainbow analytics, invented ranking scores, emoji or icon boxes.
- The signature element is a canonical rally strip and measured court geometry,
  explicitly illustrated for synthetic data. It must never impersonate footage.
- Numerical comparisons use tabular digits, labelled bars and visible denominators.
- Search and filters are immediate. Focus changes never depend on animation.
- Short opacity/transform sheet transitions only; no page entrance choreography.
- Reduced-motion preferences and the existing explicit motion setting are respected.

## Insight behavior

| Type | Result and evidence rule | First-increment interaction |
| --- | --- | --- |
| Rally of the Match | Longest observed vs favourite are separate; include losses and ties | Inspect longest; choose favourite |
| Made Me Smile | Selecting participant, source interval, optional reason, private draft | Choose a rally or custom interval |
| Comeback Moment | Same-game deficit to first recovery; gaps break the claim | Inspect illustrative score sequence; real candidate remains reviewable |
| Keep-Alive Personal Best | Same verified person, comparable prior sessions, no first-session record claim | Inspect example history; live history explains linking requirement |
| Best Save | Incoming attack, defender, successful return, later rally outcome | Choose a save without asserting a win or calibrated difficulty |
| Partnership Memory | Both stable IDs and shared membership; contributions need contacts | Inspect pair context; choose a private memory |
| Start vs Finish | Ordered full-match rally halves, explicit odd-rally policy | Inspect two labelled comparison groups |
| Short vs Long | 1-4, 5-8, 9+ observed shots; rates use known winners | Inspect server buckets or synthetic parts with denominators |
| Doubles Court Coverage | Calibration, simultaneous identity/visibility, coach review | Inspect illustrated interval and requirements; N/A for singles |
| Smash Conversion | Direct/forced/continued/own-error/uncertain; distinguish rally association | Inspect outcome breakdown and denominator |

Proposed example definitions are version 1, not adopted sport rules. Count contacts
including the serve. Example comeback starts at a deficit of five and ends at the
first tie. Halves use rally order, with an odd middle rally assigned to the finish.
Smash conversion is (direct winners + reviewed forced errors) / resolved attempts;
continued rallies and own errors stay in the denominator, uncertain attempts are
shown separately. Never silently apply these formulas to production rows.

## Presentation contracts and data boundaries

`features/highlights/types.ts` describes a sport-neutral collection, insight,
metric, chart, evidence range, participant/team choice and local personal pick.
An explicit provider registry resolves supported sports. Badminton labels,
illustrations, example material and existing-response adapters stay in
`features/highlights/badminton/`. The engine and inference pipeline are untouched.

An insight declares group, availability, origin, definition, required evidence,
evidence references and optional chart/metrics. Example origin is never a human
review status. Live items expose observed/provisional status without promotion.

The live adapter consumes the existing overview and session insights read APIs.
It can display the server's longest count, existing ranked candidates and existing
rally-length buckets. No fabricated history, coverage judgement, save classification,
score recovery or smash conversion fills a missing production contract.
No unsupported sport silently receives the badminton catalogue.

Local picks have schema version, source namespace, session ID, analysis revision,
source fingerprint, selected participant or explicit unknown, frame range, note,
kind and creation time. Synthetic and real picks use separate keys. Boundaries
are validated against media and source revision. Read/write failures are visible.
Only small metadata is stored; never media blobs, weights or credentials.
There is no sharing backend: all picks remain private and labelled as local drafts.

The example can be rendered when authentication service is unreachable; this does
not unlock protected API data or bypass a successful authentication requirement.
Existing auth remains authoritative when it responds. Live reads remain protected
by the backend and have error/retry states; the UI never starts that backend.

## Interaction and resilience

- Default to the explicit example collection; owned recordings are an intentional switch.
- Session and participant changes reset stale detail selection and form context.
- Participant filters retain team statistics only when that participant's team is known.
- All, personal picks and review-needed views have useful empty states and reset actions.
- Search finds titles, types and descriptions; result counts are announced politely.
- Loading reserves the page structure; a failed read offers retry and example recovery.
- Drawers use Radix focus trap, Escape, labelled close and return focus to trigger.
- Personal-pick form defaults to unknown selector and private; never claims server save.
- Long names wrap, chart values cannot exceed their declared scales, and no missing
  value becomes zero or unknown winner becomes a named participant.

## Completion boundary

Deliver UI source, design record, implementation record and source-level review.
Do not claim runtime, accessibility, visual or pipeline validation. Tests, builds,
browser checks and inference are intentionally not run under the user's instructions.
