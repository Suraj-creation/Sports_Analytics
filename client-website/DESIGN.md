# Rally — design and experience system, revision 2

29 October 2026. This is the primary design specification for the client-facing website. A self-contained copy travels in client-website/DESIGN.md. The original reference library is preserved.

## A. Product and brand foundation

Rally makes a recorded game inspectable: pixels become observations, observations become events, defined calculations become analytics, and evidence supports an explanation. Amateur badminton is the emotional and practical entry point; a broader video-intelligence foundation is the architectural horizon. The website must serve the player who wants a memory as well as the player who wants analysis. It must also make the catalogue and agentic harness tangible to a technical or commercial visitor.

Keep the existing working name and forest/ivory/lime identity. The first website was too repetitive: one athlete, near-identical overhead images, a fixed editorial axis, and analytics largely hidden behind a single modest demo. This revision changes composition, media, analytical depth and interaction while preserving product truth and portability.

## B. Creative direction

**Concept: the match film meets the evidence notebook.** Sport supplies the emotion; a visible analytical layer opens the moment. The core visual contrast is a large, physical action against precise, quiet evidence. Avoid a wall of generic cards, decorative HUD noise, repeated image sequences and exaggerated data claims.

The first viewport has a dark, high-impact split composition: a short, oversized human promise on the left and a large badminton action with a visible pose estimate on the right. The primary action opens the evidence experience. After the hero, composition changes materially: an intimate post-game photograph, a live illustration/workspace, a full-width data catalogue, an investigation trace, a wide tracking film, and a confident closing invitation.

Internal approaches considered: a full-screen film campaign (high emotion, insufficient product depth); a dense analysis terminal (strong mechanism, intimidating to amateurs); and a sports editorial with embedded evidence instruments (selected: human and technical value reinforce each other). The user's explicit request for an internally selected, more ambitious result governs this direction; no extra review gate is introduced.

## C. Logo and visual identity

Two incumbent assets exist: an application favicon using an angular apex/trajectory and dot, and the marketing website's two lime directional slashes. Preserve both under assets/brand/original. Explore three grayscale evolutions internally, test small-size geometry, then select an evolution with recognizable directional energy. Do not reuse the upstream logo skill's fictional Ralli example or an unrelated identity.

Deliver an editable symbol, outlined horizontal lockups, one-colour light/dark variants and a small favicon. Maintain a minimum clear space of one main stroke width; use the simplified mark at 16–24px. Header and footer must use approved variants, not random redraws. No gradients, neural-node clipart or literal shuttlecock mark.

## D. Design tokens

- Forest canvas: #0D211C. Deep stage: #081713. Ink: #172D25.
- Paper: #F3F4ED. Pale analytical surface: #E5EBDF. Lime action/selected evidence: #DBF268.
- Secondary dark copy: #B9C9BC; secondary light copy: #53645A. Use full ink for normal body text.
- Locally bundled Archivo variable is the shared voice. Body 17–19px, small metadata 13–14px, lead 22–27px, section heading 38–68px, primary display up to 114px. Tracking stays at or above -0.04em.
- Content width: 1440px; outer gutter 24–48px, 20px on narrow phones. Major section spacing 88–120px; connected controls 8–16px.
- Breakpoints: 1120px, 900px, 640px, 360px. Adapt composition rather than shrinking a dashboard.
- Primary controls are flat and solid; one consistent small corner treatment. App fragments may use restrained borders and semantic panels. No decorative glow, glass or generic gradients.

## E. Composition and layout

1. **Opening:** a short two-line title and genuine product definition; large badminton media with a visible pose layer, actual landmark count where available, source/overlay control, and an explicit generated-scene context.
2. **Human value:** a contrasting photograph of different people reviewing their game. One useful observation and the freedom to choose enjoyment or analytical depth.
3. **Evidence explorer:** two different badminton scenes, independently switchable source/pose/movement/events layers, a coherent sample event record and source-linked answers. No three-image version of the same overhead pose.
4. **Analytics catalogue:** a full-width, genuinely interactive record with tabs for rallies, shots, movement, patterns, highlights and progress. Every chart has a clear question, data source and definition. Planned states show prerequisites instead of fabricated charts.
5. **Agentic investigation:** a user-triggered example shows a real bounded tool flow and an evidence-linked result from the same fixture. Explain retrieval, calculation and grounding; do not invent deployed specialist agents.
6. **Wider foundation:** the supplied basketball tracking film is shown uncropped, with native controls and chapter seeks. Label its source and reference status. Other sports and industrial applications remain future directions.
7. **Close:** a focused local demo-brief flow, concise FAQs and a strong brand close. Preserve copy/download and editable configuration.

On phones, the pose scene precedes its evidence, catalogue tabs wrap without clipping, charts remain legible, and the wide supplied film keeps its native aspect ratio. No viewport scroll locks or horizontal overflow.

## F. Images and analytical assets

Use a small, varied family: a male player in a low courtside net-recovery action; one retained female overhead image within the explorer; and a candid image of different amateur players reviewing a recording. Vary person, action, angle and emotional role. Never fill multiple sections with near-duplicate athletes.

Source image processing must preserve anatomy and equipment. Analytical skeletons are code/SVG geometry aligned to the actual image, not painted by image generation. Use locally computed 2D pose estimates if the installed environment can provide them; otherwise clearly identify hand-authored illustrations. Confidence determines visible landmarks and connections. An image estimate does not establish validated biomechanics.

The supplied video is H.264, 854x480, 30 fps, approximately 16.97 seconds, with no audio stream. It shows basketball gameplay followed by pre-existing player boxes and tags. Copy a local version and poster into the standalone package, preserve the original reference, and use object-fit: contain with aspect-ratio 854/480. Do not add an inaccurately aligned overlay or relabel the sport as badminton.

## G. Motion and interaction

Primary lens: Jakub's production polish; selective Jhey experimentation for the analytical reveal; Emil's restraint for repeated controls. The signature moment reveals a pose over a real-feeling scene. A second authored moment steps through the evidence/tool chain on explicit action. The rest is fast feedback and subtle continuity.

Use native CSS and WAAPI; do not add React libraries to this static site. Feedback: 140–220ms. Panel continuity: 220–360ms. One entry choreography: 600–850ms from an already readable state. Keyboard actions update immediately. Reduced motion disables spatial entrances and auto motion. No pulsing CTAs, perpetual particles or fake processing spinners. Video begins paused and retains native play/pause/seek controls.

Motion evidence studied: supplied video at 0–5, 5–11 and 11–17 seconds shows source-to-tracking transition, persistent player boxes and full-court camera motion. It informs temporal clarity and chapter controls, not a claim that Rally generated its annotations.

## H. Components and data contracts

The six-rally synthetic fixture is shared across the catalogue and guided Ask. Official durations: 8, 12, 6, 18, 10, 16 seconds. Candidate stroke counts: 6, 10, 4, 14, 8, 12. Therefore active play is 70 seconds, 54 candidate strokes, mean nine strokes, longest by stroke count Rally 4. Eight strokes are Unknown; classification coverage is 46/54 and is not accuracy. Two warm-up exchanges are excluded from official totals.

Definition panels contain: user question, formula, numerator/denominator, eligible events, exclusions, source references and limitation. Use a screen-reader-readable data table alongside charts. Rallies are keyboard-selectable. Shot charts retain Unknown. Movement paths are illustrative unless calibration supports physical units. Progress remains Planned where identity/comparability is absent.

The tool trace uses actual project responsibilities: match_overview, list_rallies, get_rally and grounding validation. Supported read-only tools also include player_stats, find_strokes, top_highlights, momentum, and rules_and_background. Do not imply a deployed pose, trajectory, cross-session or agent-triggered reanalysis tool. A speed request must abstain.

## I. Product storytelling and evidence hierarchy

The progression is personal moment -> inspectable observation -> coherent event record -> reproducible calculation -> grounded answer -> larger foundation. Every section adds a new kind of understanding.

Point-of-use states: implemented foundation; implemented with limitations; illustrative or experimental; planned/research. Shot naming remains a rule-based preview. Movement has calibration, jitter and identity constraints. Cross-session identities and all-four-player attribution are incomplete. The prior server audit and local checkout differ; never present an architectural validation requirement as a universally enforced guarantee.

## J. Technical boundary

All implementation and media processing for this revision occur locally in C:/Users/Govin/Desktop/Badminton_analytics/client-website. No SSH or GPU-server operations. Node24/Python/FFmpeg are available locally; reuse installed packages for offline asset preparation only. Ship no inference model, Python runtime or analytics backend with the website.

Keep the independent package/lock/build/preview/tests and relative runtime paths. Data modules, SVGs, fonts, video and imagery are local. Separate modules own catalogue calculations, pose rendering, investigation and brief generation. Public build output excludes docs, tests and source tools. Moving client-website must remain sufficient to build and deploy independently.

## K. Reference and decision log

- Google Cloud x Team USA, inspected through A1 and its live official page: sport and measurable movement share one story; borrow analytical visibility and variation of scale, never its athlete claims, artwork, logos or proprietary type.
- Future, inspected through A1: human participation and varied activity images make the technology personally meaningful; borrow the human scene, not the testimonial/pricing structure or serif styling.
- Vibrant Design website gallery and its Rauno entry: interaction details are deliberate, not effects layered over a template. Use fast, precise control feedback and a single signature reveal.
- Linear and Lightspark project references: dense product evidence and a clear modular platform story remain useful; the old rigid 42% axis does not remain binding.
- Dedicated logo-design skill: SVG-first geometry, multiple mark types, small-size and one-colour testing; internal selection follows the user's explicit instruction.
- UI/UX Pro Max: touch targets, contrast, chart alternatives and responsive semantics. Its local CLI is not currently at the advertised path; use the installed guidance and record the limitation if the script cannot be located.
- Source URLs and current compatibility assessment are recorded in docs/revision-research.md.

## L. Quality gates

Build the complete revision before a batched desktop/mobile browser review; repair observed issues together and confirm once. Avoid unbounded polish loops. Required: no broken assets; all layer, catalogue, formula, trace, film, form and disclosure controls work; keyboard focus is visible; 320px and 390px have no overflow; reduced motion has a static path; film remains uncropped; generated/estimated/reference/future labels are unambiguous.

Run meaningful data tests, static asset/dependency checks, build, mechanical Impeccable detector and an isolated-copy build. Preserve pre-existing unrelated changes. Provide a local preview, screenshots, portable source and a concise implementation/verification record. Deployment remains separate.

## Final implementation decisions

The bounded review removed decorative section kickers and numbered chapter labels so the headings and real product evidence carry the sequence. Functional CSS text has a 12px minimum. Synthetic citations open a dedicated record with durations, event IDs and the complete candidate sequence, explicitly separate from the generated image studies. Keyboard chart selection restores focus. Responsive images retain their intrinsic proportions. The final build contains no repeated preparation/recovery photo set.
