/* api.js -- thin fetch wrappers. Every backend route already lives under
   /api/*, always same-origin (proxied in dev, same host in prod), so
   credentials are implicit -- no CORS/token handling needed. */

async function handle(resp) {
  if (!resp.ok) {
    let message = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      if (body.error) message = body.error;
    } catch {
      /* non-JSON error body -- keep the generic HTTP status message */
    }
    throw new Error(message);
  }
  const contentType = resp.headers.get("content-type") || "";
  return contentType.includes("application/json") ? resp.json() : resp;
}

export function apiGet(url) {
  return fetch(url, { credentials: "same-origin" }).then(handle);
}

export function apiPostJson(url, body) {
  return fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body ?? {}),
  }).then(handle);
}

export function apiPost(url) {
  return fetch(url, { method: "POST", credentials: "same-origin" }).then(handle);
}

export function apiPostForm(url, formData) {
  return fetch(url, { method: "POST", credentials: "same-origin", body: formData }).then(handle);
}
