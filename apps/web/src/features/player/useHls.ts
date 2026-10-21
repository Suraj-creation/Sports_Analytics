// light build: no subtitles/DRM/alt-audio — none apply to a match proxy
import Hls from "hls.js/light";
import { useEffect, useState } from "react";
import { hlsUrl } from "@/lib/api";

export type HlsState = "idle" | "loading" | "ready" | "waiting" | "error";

/**
 * Attach the session's HLS stream. The playlist is an EVENT playlist that grows while the
 * proxy is encoded, so hls.js would treat it as live and jump to the edge — `startPosition: 0`
 * and `liveDurationInfinity` keep it a seekable VOD-like timeline starting at frame 0.
 * While the first segments don't exist yet the server answers 404; we keep retrying.
 */
export function useHls(video: HTMLVideoElement | null, sessionId: string, enabled: boolean): HlsState {
  const [state, setState] = useState<HlsState>("idle");

  useEffect(() => {
    if (!video || !enabled) return;
    const src = hlsUrl(sessionId);
    let retry: ReturnType<typeof setTimeout> | null = null;
    setState("loading");

    if (Hls.isSupported()) {
      const hls = new Hls({
        startPosition: 0,
        liveDurationInfinity: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        maxBufferLength: 30,
        enableWorker: true,
      });
      hls.on(Hls.Events.MANIFEST_PARSED, () => setState("ready"));
      hls.on(Hls.Events.ERROR, (_e, data) => {
        if (!data.fatal) return;
        if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
          // not ready yet (404) or a dropped connection: try again shortly
          setState("waiting");
          retry = setTimeout(() => {
            hls.loadSource(src);
            hls.startLoad(Math.max(0, video.currentTime));
          }, 2000);
        } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
          hls.recoverMediaError();
        } else {
          setState("error");
        }
      });
      hls.loadSource(src);
      hls.attachMedia(video);
      return () => {
        if (retry) clearTimeout(retry);
        hls.destroy();
      };
    }

    // Safari / iOS: native HLS
    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      const onMeta = () => setState("ready");
      const onErr = () => {
        setState("waiting");
        retry = setTimeout(() => {
          video.src = src;
        }, 2000);
      };
      video.addEventListener("loadedmetadata", onMeta);
      video.addEventListener("error", onErr);
      video.src = src;
      return () => {
        if (retry) clearTimeout(retry);
        video.removeEventListener("loadedmetadata", onMeta);
        video.removeEventListener("error", onErr);
        video.removeAttribute("src");
        video.load();
      };
    }
    setState("error");
    return undefined;
  }, [video, sessionId, enabled]);

  return state;
}
