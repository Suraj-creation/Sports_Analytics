# Rally client website implementation plan

> For agentic workers: use the approved design contract and execute all tasks without further design gates.

**Goal:** Build a complete, portable client-facing Rally website that makes video intelligence tangible through an editorial story and working evidence illustration.

**Architecture:** Standards-based HTML, CSS and small ES modules; no runtime packages or analytics API. A built-in Node static builder copies only the standalone package's public files. All fonts and images are local.

**Spec:** docs/design.md, approved by the user on 29 October 2026.

## Global constraints

- Canonical project: /home/administrator/Desktop/sport-analytics/Sports_Analytics/client-website/.
- Windows temporary files are transfer staging, not the authoritative project.
- Do not change existing analytics files, environment, port 8010, tunnel, or user changes.
- No parent-path imports, symlinks, remote runtime assets or secret configuration.
- Brand Rally is provisional. Future domains, shot estimates and sample content are clearly identified.
- No publication; separate deployment will follow later.

## Task 1: Independent tooling and extraction

Create package.json, package-lock.json, .gitignore, scripts/build.mjs, scripts/serve.mjs, scripts/check.mjs, tests/tooling.test.mjs and README.md. Scripts use only Node built-ins. Validate traversal handling, subpath requests, MIME types and build boundaries with meaningful node:test cases. Build copies index.html, src/ and assets/ into an owned dist directory, rejects symlinks and never copies docs, secrets or node_modules. Serve defaults to 127.0.0.1:4178 and supports --host/--port/--dir. Check local HTML/CSS/module asset references and reject parent/runtime external dependencies. Run tests before and after implementation, then test on the GPU server with its existing environment.

## Task 2: Story and visual experience

Create index.html, src/styles.css, src/site-config.js and local image assets. Build the approved photographic masthead, repeated editorial axis, human story, interactive sample, six capabilities, audience depth, wider platform, trust, FAQ and demo brief close. Use a single Archivo family and paper/forest/chartreuse palette. Include semantic landmarks, skip link, focus styles, honest metadata and local SVG favicon. Content is visible without JS. Generated scenes never represent an analysed customer session.

## Task 3: Working demonstration and request brief

Create src/demo-data.js, src/demo.js, src/brief.js and src/main.js. Three phases (preparation, contact candidate, recovery) share selected state. Source/movement controls change overlays. Fixed example questions produce a source-linked illustration; citation controls select the phase and reveal its source frame. Speed/distance questions explicitly abstain. Form validates a useful role and goal, then prepares a text brief with copy/download; no invented submission. A configurable verified contact can later enable a mail draft. Test state transitions and brief behavior through the real browser.

## Task 4: Verification, review and delivery

Run npm test, npm run check and npm run build on the GPU server after source ../gpu-env.sh. Launch a separate preview on 4178 and forward it to the local browser. Inspect 1440, 768, 390 and 320 widths, keyboard navigation, reduced motion, all controls and no-JS reading. Check errors and external runtime requests. Copy only client-website to a temporary isolated directory and build/serve it without the repository. Obtain independent source review, repair material findings, and write docs/verification.md, docs/capabilities.md and docs/assets.md.

## Decisions and progress

- Ruling: work in the explicitly requested new folder in the current non-main feature checkout; do not change the user's branch or create another checkout. The standalone directory is the change boundary and existing dirty files stay untouched.
- Ruling: execute the tightly coupled visual and interaction work together; delegate independent tooling and final review through the installed skills.
- Design approved. All four implementation tasks complete. Server checks, independent source review, browser interactions and isolated extraction passed. See verification.md.
