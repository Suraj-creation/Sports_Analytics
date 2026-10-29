# Revision research and tool choices

29 October 2026. The user's later mission explicitly requested local work and no remote GPU connection. All revision work stayed in the local standalone client-website folder. The existing analytics checkout, GPU jobs and Cloudflare tunnel were not operated.

## Design decisions grounded in references

The connected A1 tools supplied the live-page screenshot and structural reference for [Google Cloud × Team USA](https://sports.withgoogle.com/teamusa/): large sports imagery, confident type and visible movement analysis inside the narrative. Rally uses its own imagery, identity and product claims. The [Future](https://future.co/) reference informed more varied human participation and a warm after-game scene. The user-named [Vibrant gallery](https://vibrant.design/websites) and its Rauno entry informed precise, restrained controls. These are references for principles, not cloned artwork or layouts.

Foundational local sources were read completely: Video_Intelligence_Platform_Master_Context.md and Cortex_Creative_Direction_Visual_Assets_Sports_Intelligence.md under Design/references, plus the relevant local sports/analytics/agent modules. The local code separates perception observations, temporal events, deterministic analytics and grounded explanation. Its tool inventory includes match_overview, list_rallies, get_rally, player_stats, find_strokes, top_highlights, momentum and rules_and_background. The website does not invent live, doubles, validated biomechanics, pose-agent tools or cross-session identity capabilities.

## Skills and tools used

- Design Taste Frontend, Bolder and Impeccable guided art direction, hierarchy, varied compositions and the bounded desktop/mobile review.
- Design Motion Principles and Awwwards Motion Study guided small single-entry motion, native controls and reduced-motion handling. No autoplay, scroll pinning or decorative perpetual animation.
- UI UX Pro Max supplied secondary guidance. Its advertised local search script was missing; no install or environment change was needed.
- The dedicated [Logo Design workflow](https://github.com/kaankiziltug/logo-design-skill) informed internal concepts, SVG construction and small-size inspection. See brand-evolution.md.
- A1/Design/Inspo/Awwwards capabilities were assessed; A1 supplied the strongest selected sports reference. Native CUA performed browser inspection and interactions.
- Built-in image generation created two distinct scenes. Installed local CPU vision tooling produced the exported pose points. FFmpeg inspected the supplied video, extracted contact sheets and prepared faststart/poster assets.

Impeccable context and concept-seed were run. The user had already approved the direction and expressly authorised internal exploration and selection, so no duplicate approval checkpoint was added.

## Named libraries and tools assessed

| Source | Decision |
| --- | --- |
| [Taste Skill](https://github.com/Leonxlnx/taste-skill), [Impeccable](https://github.com/pbakaus/impeccable), [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), [Emil Kowalski skills](https://github.com/emilkowalski/skills) | Use compatible installed guidance. |
| [OpenDesign](https://github.com/nexu-io/open-design) | Full design workspace; unnecessary to add. The user-named old owner URL returned 404. |
| [Motion](https://motion.dev/docs/quick-start) | Vanilla API exists, but CSS/WAAPI already cover the limited motion without another runtime. |
| [Aceternity](https://ui.aceternity.com/) | React/Tailwind component stack would conflict with this dependency-free site. Reference only. |
| [Animmaster](https://animmasterlib.dev/) | Selective motion reference; no purchase or incompatible component import. |
| [agent-browser](https://github.com/vercel-labs/agent-browser) | Existing CUA was sufficient. The user-named browser-use owner URL returned 404. |
| [Responsively](https://responsively.app/) | Viewport testing already available; no installation. |
| [Refero Styles](https://styles.refero.design/), [A1](https://a1.gallery/), [Inspo](https://inspomcp.dev/) | Connected reference research; no external runtime dependency. |

The website stays HTML/CSS/ES modules with Node built-ins for tooling. No React, animation library, model, Python dependency, hosted font, analytics service or third-party script is required to deploy it.
