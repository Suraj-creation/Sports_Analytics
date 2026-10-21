/* xhrUpload.js -- fetch() cannot reliably report upload (request-body)
   progress across browsers; XMLHttpRequest still can, via
   xhr.upload.addEventListener('progress', ...). Kept as one small,
   dependency-free utility rather than pulling in axios for this. */

export function postFormWithProgress(url, formData, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", (ev) => {
      if (ev.lengthComputable && onProgress) {
        onProgress(Math.round((ev.loaded / ev.total) * 100));
      }
    });
    xhr.addEventListener("load", () => {
      let body = {};
      try { body = JSON.parse(xhr.responseText || "{}"); } catch { /* non-JSON */ }
      if (xhr.status >= 200 && xhr.status < 300) resolve(body);
      else reject(new Error(body.error || `HTTP ${xhr.status}`));
    });
    xhr.addEventListener("error", () => reject(new Error("Network error during upload")));
    xhr.open("POST", url);
    xhr.withCredentials = true;
    xhr.send(formData);
  });
}
