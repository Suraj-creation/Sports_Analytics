import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { setCsrf, uploadVideo } from "./api";

/** The stand-in delivers actual lifecycle events, including abort without error/load. */
class ControlledUpload {
  static instances: ControlledUpload[] = [];
  upload = { onprogress: null as ((event: ProgressEvent) => void) | null };
  onabort: ((event: ProgressEvent) => void) | null = null;
  onerror: ((event: ProgressEvent) => void) | null = null;
  onload: ((event: ProgressEvent) => void) | null = null;
  status = 201;
  responseText = '{"session_id":"saved-recording"}';
  withCredentials = false;
  open = vi.fn();
  send = vi.fn();
  setRequestHeader = vi.fn();
  constructor() {
    ControlledUpload.instances.push(this);
  }
  abort() {
    this.onabort?.(new ProgressEvent("abort"));
  }
}

function currentUpload() {
  const xhr = ControlledUpload.instances.at(-1);
  if (!xhr) throw new Error("No upload request was created");
  return xhr;
}

describe("uploadVideo lifecycle", () => {
  beforeEach(() => {
    ControlledUpload.instances = [];
    vi.stubGlobal("XMLHttpRequest", ControlledUpload);
    setCsrf(null);
  });
  afterEach(() => {
    vi.unstubAllGlobals();
    setCsrf(null);
  });

  it("settles cancellation promptly with AbortError when XHR only emits abort", async () => {
    const upload = uploadVideo(new FormData(), vi.fn());
    const fulfilled = vi.fn();
    const rejected = vi.fn();
    void upload.promise.then(fulfilled, rejected);

    upload.abort();
    await Promise.resolve();

    expect(fulfilled).not.toHaveBeenCalled();
    expect(rejected).toHaveBeenCalledOnce();
    expect(rejected.mock.calls[0]?.[0]).toBeInstanceOf(DOMException);
    expect(rejected.mock.calls[0]?.[0]?.name).toBe("AbortError");
    // Repeated cancellation and late events cannot settle a second time.
    upload.abort();
    currentUpload().onload?.(new ProgressEvent("load"));
    await Promise.resolve();
    expect(rejected).toHaveBeenCalledOnce();
    expect(fulfilled).not.toHaveBeenCalled();
  });

  it("retains upload progress, CSRF protection and the successful response", async () => {
    setCsrf("bound-token");
    const progress = vi.fn();
    const form = new FormData();
    const upload = uploadVideo(form, progress);
    const xhr = currentUpload();
    expect(xhr.open).toHaveBeenCalledWith("POST", "/api/sessions");
    expect(xhr.setRequestHeader).toHaveBeenCalledWith("X-CSRF-Token", "bound-token");
    expect(xhr.withCredentials).toBe(true);
    expect(xhr.send).toHaveBeenCalledWith(form);
    xhr.upload.onprogress?.(new ProgressEvent("progress", { lengthComputable: true, loaded: 2, total: 4 }));
    expect(progress).toHaveBeenCalledWith(0.5);
    xhr.onload?.(new ProgressEvent("load"));
    await expect(upload.promise).resolves.toEqual({ session_id: "saved-recording" });
  });
});
