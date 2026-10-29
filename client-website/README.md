# Rally client website

A portable public introduction to a video intelligence product, starting with badminton. Rally is a working name. The revision combines varied generated sports imagery, locally estimated 2D pose, an interactive analytics catalogue, inspectable synthetic event records, grounded example questions and the supplied tracking-reference film.

This is a client-facing demonstration with no analytics backend, account or upload service. Every calculation uses a clearly identified synthetic fixture; model estimates and illustrative concepts are labelled separately.

## Run

Node.js 22 or later. No packages to install, environment variables, API keys, GPU, Python or parent repository dependencies.

```sh
npm run dev
npm test
npm run check
npm run build
npm run preview
```

Default preview: http://127.0.0.1:4178/. Custom port:

```sh
npm run preview -- --host 127.0.0.1 --port 14178
```

Stop with Ctrl+C. The server serves only public HTML, source, fonts and media; it rejects private/hidden files, symlinks and path traversal. MP4 single-byte ranges support playback and seeking. It accepts GET and HEAD, with no request or form-content logging.

This revision was developed locally as explicitly requested. It does not require connecting to or operating the analytics GPU server.

## Extract and deploy separately

Copy the **whole client-website folder** into a new repository or unrelated directory. Run the same commands there. No file is imported from its parent repository. Keep package.json, package-lock.json, scripts/ and tests/ for development. Publish only the generated **dist/** contents using a static host.

The build checks all literal references before copying the public trees. Local, relative paths support deployment at the domain root or a subpath. The builder replaces only its own marked output; it refuses to delete an unowned dist directory.

```sh
npm run preview -- --base /rally/
```

Then open http://127.0.0.1:4178/rally/. No rewrite rules, SPA fallback or server routes are needed. The host should serve MP4 with byte-range support, JavaScript as text/javascript, fonts with their font MIME type, and assets with their matching types. The supplied local preview supports these behaviours.

## Source map

- index.html and src/styles.css: complete editorial page, native responsive navigation and FAQ.
- src/vision.js and pose-data.js: confidence-filtered 2D estimates exported during asset preparation.
- src/catalogue-data.js: immutable fixture and pure calculations; shared by charts and guided investigation.
- src/catalogue.js: six catalogue views, definitions, keyboard-safe chart selection and inspectable event sequences.
- src/investigation.js: bounded local question demonstration with genuine fixture citations and abstention.
- src/brief*.js: local brief preparation, copy and download.
- assets/brand/: outlined identity family, originals and internal concept SVGs.
- scripts/: build, reference checker and safe preview, all Node built-ins.

## Brand and contact

The outlined logo assets, page title, visible copy and accessible labels use the working name Rally. src/site-config.js controls brief naming and the optional verified contact mailbox. A future rename must also update the logo artwork and static copy.

The brief form prepares text locally. Nothing is sent. Leave contactEmail empty until the owner provides a verified business mailbox; this enables an optional visitor-initiated email draft. The page contains no tracker, external AI request or customer upload.

## Design and evidence

DESIGN.md is the current design contract, also copied to docs/design.md and the parent Design/design.md for this project. See docs/asset-provenance.md, docs/brand-evolution.md, docs/revision-research.md, docs/capabilities.md and docs/verification.md for source, rationale, limits and checks. The reference clip illustrates a future domain direction; it does not claim that Rally ships basketball support.
