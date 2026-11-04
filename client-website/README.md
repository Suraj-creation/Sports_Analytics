# Rally client website

A portable static introduction and guided product illustration. Rally is a working name. Example frames, event records and movement overlays are illustrative, not an analysed customer session or an accuracy benchmark. The website has no analytics backend, account flow or upload service.

## Run locally

Use Node.js 22 or later. All tooling uses Node built-ins; there are no packages to install and no environment variables or GPU dependencies.

```sh
npm run dev
```

Open `http://127.0.0.1:4178/`. Source preview serves only `index.html`, `src/` and `assets/`. It does not expose documentation, tests, package files, hidden files, directory listings or symbolic links. Restart preview after adding or removing public files. Existing file edits are read on each request; refresh the browser to see them.

```sh
npm run dev -- --host 127.0.0.1 --port 4178
npm test
npm run check
npm run build
npm run preview
```

`dev` and `preview` default to `127.0.0.1:4178`. Both accept `--host`, `--port` and `--dir`; paths supplied with `--dir` resolve from the current working directory. Stop with Ctrl+C. The preview server records no request logs, cookies, form contents or user data. It accepts only GET and HEAD.

On the project GPU server, follow the repository runtime instructions before validation:

```sh
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
cd client-website
npm test
npm run check
npm run build
```

This website uses its own preview port. Existing analytics service operations on port 8010 are separate.

## Build and extract

`npm run build` checks local references, then creates `dist/` with only the HTML, source modules/styles, local fonts and media required by the website. Private repository files, documentation, scripts and dependencies are excluded. Unsupported or hidden files inside the public trees fail the build. Symbolic links are rejected. Generated output has an ownership marker; the builder refuses to replace a pre-existing `dist/` it does not own. Move or rename that directory first.

To extract the project, copy this entire `client-website/` directory into an unrelated folder. Run the same commands there. No parent repository files, shared imports, Python environment, API credentials or `node_modules` are needed. Keep `package.json`, `package-lock.json`, `scripts/` and `tests/` with the source package for future builds. Publish only the contents of `dist/`.

The checker validates literal HTML/CSS/module references against the public file set, including fragment targets. Runtime URLs must be local and relative. Local `../assets/` references from `src/` are valid; references leaving this package fail. Outbound HTTP(S), mail and telephone links on anchors are allowed. Computed module imports are deliberately unsupported by the static checker. Browser verification remains necessary for interaction and dynamically created content.

## Static deployment

Use any static host with `dist/` as its document root. This repository does not deploy or publish automatically. Serve JavaScript as `text/javascript`, styles as `text/css`, SVG as `image/svg+xml` and fonts with the appropriate font MIME type. There are no server routes, rewrites, SPA fallback rules or secrets to configure.

All runtime references are relative, so the same output can live at `/` or a folder such as `/rally/`. Preserve the trailing slash at the folder URL. To verify a mounted folder locally:

```sh
npm run preview -- --base /rally/
```

Then open `http://127.0.0.1:4178/rally/`. `--base` also works with source preview. The small Node server is a development preview; use the static host's production HTTP service for publication.

## Working name and contact setup

`src/site-config.js` exports `siteConfig` with `name`, `wordmark` and `contactEmail`. Change `name` and `wordmark` to replace the working brand in visible nodes. Before a public launch, also review the page title, description, accessible labels and footer for consistency, and review the capability statements in `docs/`. Keep imagery provenance and the illustrative-example labels visible.

The request flow prepares a brief locally for copying or downloading. Nothing is sent. Leave `contactEmail: ''` until the owner supplies and confirms a public business mailbox. Setting that verified address enables an **Open email draft** link that the visitor chooses to send in their own mail application. Do not add a mailbox, submission endpoint, analytics tracker or third-party collection service by assumption. No passwords or application secrets belong in this package.

See `docs/design.md`, `docs/capabilities.md`, `docs/assets.md` and `docs/verification.md` for the design, claim limits, asset provenance and validation record.
