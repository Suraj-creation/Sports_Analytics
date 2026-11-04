# Rally client website: design and build contract
Date: 29 October 2026. Brand: Rally, a replaceable working name.
Canonical destination: /home/administrator/Desktop/sport-analytics/Sports_Analytics/client-website/

## Brief
What: a standalone public introduction to an evidence-grounded video intelligence platform.
Who: badminton players first, then coaches, venues and prospective platform partners.
Goal: understand the product through an interactive example and explore a product conversation.
Tone: cinematic, personal, exact.
Constraints: no imports or runtime dependency on the analytics platform; all assets local; honest capability states.

## Approach
Recommended: show one sporting moment becoming an inspectable record, then reveal the underlying engine.
Alternatives considered: a consumer-only highlights site (clear but undersells the platform) and a partner-first infrastructure site (deep but remote from player value).
Use the existing app's Rally name provisionally; isolate brand/contact settings for replacement.

## Narrative and complete section plan
1. Your game. Seen clearly.
   A photographic masthead followed by an oversized two-line title and a concise product definition.
   Supporting copy: Turn badminton footage into replayable moments, movement patterns and answers you can inspect.
   Primary action: Explore a rally. Navigation: Experience, Intelligence, Foundation, Questions.
   A visible caption identifies generated imagery and the illustrative nature of overlays.

2. The point is only part of it.
   A human story: a recovery you did not notice, an exchange worth remembering, a pattern to revisit.
   Playing can be valuable without every session becoming an examination.
   One considered text composition and a sport image; no invented customers or testimonials.

3. Follow the evidence.
   A functional guided product illustration: source view, estimated movement view, and an evidence-linked answer.
   Controls switch the visual layer, select one of three event phases and answer fixed example questions.
   Selecting an evidence citation selects its phase and reveals the related source view.
   Sample values are visibly identified as illustrative, never advertised as a measured product benchmark.
   Include an insufficient-evidence answer for speed or precise physical measurement.
   No fake live upload, playback, chatbot, account, analytics API, or submission success.

4. Built to show its work.
   Six connected capabilities in a varied editorial layout:
   - Practical footage ingestion: recorded match uploads and supported media inputs.
   - Scene and player perception: people, court geometry and tracking observations.
   - Temporal understanding: contacts and rallies assembled across time.
   - Defined analytics: calculations from structured records, with availability conditions.
   - Evidence-linked investigation: frame references, source clips and metric definitions.
   - Correction and evaluation: inspect, correct and evaluate rather than hiding ambiguity.
   Shot naming remains a preview. Movement requires valid calibration and usable tracks.
   These are mechanisms and product areas, not universal accuracy promises.

5. Depth, on your terms.
   Players can revisit a moment and explore their matches.
   Coaches and venues can see the collaboration/installation vision, explicitly described as a development direction.
   Avoid claims that coach permissions, venue packages or commercial pricing are already available.

6. Badminton first. A wider foundation.
   A clear visual sequence: Video > Perception > Events > Defined metrics > Evidence > Explanation.
   Explain reusable ingestion, event records, deterministic computation and provenance in plain language.
   Other sports and visual workflows are future domain opportunities requiring their own models and validation.
   Efficient orchestration is an architectural principle; do not invent cost or latency savings.

7. Trust you can inspect.
   Explain source conditions, estimated versus observed outputs, incomplete evidence, player identity limits and corrections.
   Four-player individual attribution and cross-session identity are not advertised as completed.
   No precise biomechanics, injury prevention, universal live support or made-up accuracy numbers.

8. Questions, answered.
   What footage is suitable? What can it show today? Is doubles supported?
   Is this live? How do estimates work? Will other sports be supported?
   Plain native disclosures with concrete, qualified answers.

9. See what your footage could reveal.
   A working contact-preparation flow with role and goal choices.
   Until a verified business contact is supplied, generate/copy/download a request brief locally and state that it has not been sent.
   Never invent a mailbox, submit to an unknown service, or collect data silently.
   Designed footer with a large Rally wordmark and a methodology note.

## Visual contract
Primary reference: ElevenLabs Refero style 031056ff-7af1-46db-8daa-115f731c5d26, borrowing warm paper/ink hierarchy and restrained product exposition.
Composition: design-taste editorial-report, a photographic masthead and repeated 42% editorial axis that collapses on mobile.
Secondary references: Linear (close product evidence), Lightspark (modular platform explanation), Freshman (cinematic image treatment only).
Palette: paper #F3F3EC, ink #182C25, dark field #14251F, accent #DBF268.
Type: locally bundled Archivo variable sans, at most five primary size roles; large tight headings and readable 17-20px body.
Strong media, flat fields and deliberate section changes. No decorative gradients, floating icon cards, fake logos or ornamental charts.
Images: a coherent generated badminton scene family, clearly described as illustrations; HTML/SVG overlays remain editable and accessible.
Motion: short state transitions and purposeful event/path changes. No autoplay, perpetual animation, scroll lock or hidden essential content.
Respect reduced motion and keyboard use.

## Standalone architecture
Use standards-based HTML, CSS and small JavaScript modules with zero runtime packages.
Own package.json, independent lockfile, local assets/fonts, scripts for preview/build/check, README and deployment instructions.
Copy only client-website/ to extract. No symlinks, parent paths, shared source imports, GPU runtime, analytics routes, private video, API or secrets.
Build produces static dist/ suitable for independent static hosting, including relative URLs for subpath portability.
No deployment or public publication in this task; user has requested separate deployment later.
The running analytics service on 8010, its tunnel and unrelated GPU jobs remain untouched.

## Validation and acceptance
Run standalone source checks and build on the GPU server after sourcing ../gpu-env.sh.
Test example layers, phases, citations, unavailable answers, request brief, keyboard navigation and native disclosures.
Inspect desktop, tablet and mobile, including 390px and 320px, with reduced motion.
Check no horizontal overflow, missing local assets, console errors or external runtime requests.
Build an isolated copy outside the repository to prove extraction works without parent files or node_modules.
Document the claim matrix, sources, asset provenance, verification and remaining brand/contact decisions inside the package.

## Approval and delivery
User approved the complete direction and full build on 29 October 2026. Implementation completed in this standalone package; current verification is in verification.md.
