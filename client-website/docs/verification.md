# Verification record

29 October 2026. Authoritative package: `/home/administrator/Desktop/sport-analytics/Sports_Analytics/client-website/`.

## Server checks

Executed on the GPU server after sourcing the existing `../gpu-env.sh`; Node 22.23.3 and the existing media environment were preserved.

- `npm test`: 18 tests passed, zero failures. Includes example evidence/abstention, local brief validation, isolated builds, public-file boundaries, symlinks, traversal, MIME types and subpath serving.
- `npm run check`: local references in all 19 public files validated.
- `npm run build`: static output generated successfully, approximately 600 KiB on disk.
- `node --check` on all source JavaScript modules: passed.
- Installed design-taste static lint, run against HTML and source on the server: zero failures and zero warnings. The evidence pipeline's structural connector is an explicit, narrowly documented exception to decorative-divider detection.
- Independent source review accepted after repairs to light-surface focus contrast, initial demo state, citation navigation and no-JavaScript disclosures.

## Extraction proof

Copied the complete source package, excluding prebuilt output, to `/tmp/rally-standalone.eshdL4/client-website/`, outside the project repository. No `node_modules`, parent source, Python package, API credentials or shared imports were supplied.

The isolated copy passed `npm run build`. Its static preview mounted at `/rally/` returned HTTP 200 for the page, main module, CSS, local font and panoramic image. The temporary extraction-check server was closed after verification.

This proves that extraction does not require the analytics repository. A Node 22+ executable is needed only for the included tooling; the deployed result is ordinary static HTML/CSS/JavaScript.

## Real browser review

Used the Codex in-app browser through a private SSH loopback forward, with actual rendered page interaction.

| Viewport | Result |
| --- | --- |
| 1440 x 900 | Desktop masthead, complete title, evidence workspace and platform story inspected |
| 1280 x 720 | Complete hero title and definition remain on the first screen; no horizontal overflow |
| 768 x 1024 | Tablet crop selects the original scene; section headings remain at two lines; no horizontal overflow |
| 390 x 844 | Mobile composition, native menu, stacked demo and citation navigation inspected; no horizontal overflow |
| 320 x 740 | Small phone text, heading breaks and tile metadata fit; no horizontal overflow |

Verified interactions:

- Source and Movement buttons change actual SVG visibility. A browser regression caught an SVG `hidden` property issue; the repaired implementation toggles the real attribute, and was verified visible/hidden in both directions.
- Phase buttons change the local scene, annotation, court marker, answer and citation together.
- Home and ArrowRight keyboard commands select the expected phase and corresponding answer.
- Evidence citations select the related scene, restore Source and bring the source into view. At 390px, the source was within the viewport after activation.
- The speed question supplies no fabricated metric and hides the unavailable citation.
- Coach/venue and future-domain controls update copy and development-state labels.
- Native capability and FAQ disclosures work, including the doubles limitation.
- Brief role/source/goal selection generates the expected plain-text content. Copy, actual text download and Edit were exercised. The QA download was verified and removed afterward.
- Methodology and data dialogs open, close with Escape and restore focus.
- Browser console had no warning or error entries during the reviewed final interactions.

Reduced-motion rules and no-JavaScript content were source-reviewed. The browser-control API did not expose JavaScript or motion-preference emulation, so those two modes were not separately browser-emulated. Native disclosures, baseline content, explicit noscript notes and CSS reduced-motion overrides provide their fallbacks.

Browser screenshots are delivered separately as review artifacts. The scripted design inspector was not used for browser control; browser verification used the supported CUA surface.

## Boundaries and remaining launch choices

Rally remains a working name. `src/site-config.js` contains the public name and optional verified contact mailbox. The default brief is local-only; there is no pretend backend submission.

No deployment or publication was performed. The analytics service, its existing tunnel, training jobs and pre-existing user changes were outside this change. The website uses a separate preview port, 4178, forwarded locally to 14178 for review.
