# Rally Review frontend

React + Vite SPA for the Rally Review web app. See the repo-root
[`README.md`](../../README.md#frontend-in-detail) for the full architecture
explanation (pages, routing, state approach, styling). This file is just the
day-to-day commands.

## Development

Run the Flask backend first (from `webapp/`, in another terminal):
```bash
python3 server.py --port 8000
```

Then, here:
```bash
npm install
npm run dev
```
Opens on `http://localhost:5173` with hot reload. `vite.config.js` proxies
`/api/*` requests to the Flask backend on `:8000`, so the browser only ever
talks to one origin — no CORS setup, session cookies stay correctly scoped.

## Production build

```bash
npm run build
```
Produces static files in `dist/`. Flask (`server.py`) serves these directly —
no separate frontend server needed in production. Reload the browser after a
rebuild; no backend restart required.

To sanity-check the production build behaves the same as dev mode before
relying on it (routing edge cases can differ subtly): stop the Vite dev
server, run the build, and hit `http://localhost:8000` directly.
