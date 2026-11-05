import React from "react";
import { createRoot } from "react-dom/client";
import { VideoStage } from "@/features/player/VideoStage";
import { frameClock, timeToFrame } from "@/lib/frameClock";
import { usePlayback } from "@/stores/playback";
import { useSession } from "@/stores/session";

const errors = [];
window.addEventListener("error", (event) => errors.push(String(event.message)));
const query = new URLSearchParams(location.search);
const name = query.get("case");
const mode = query.get("transport") || "hls";
const wait = async (predicate) => {
  const end = performance.now() + 15000;
  while (!predicate()) {
    if (performance.now() > end) throw Error("media readiness timeout");
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
};
window.ready = (async () => {
  const cases = await (await fetch("/cases.json")).json();
  const info = cases[name];
  const fps = info.fps;
  const session = {
    session_id: name, title: "Synthetic media contract", sport: "badminton",
    source: { kind: "upload", uri: "synthetic" },
    media: { fps_num: info.fps_num, fps_den: info.fps_den,
      n_frames: info.identities.length, width: 320, height: 180,
      duration_us: info.identities.length / fps * 1e6, has_audio: info.has_audio },
    players: [], profile: "isolated", status: "analysed",
    frontier_frame: info.identities.length - 1, analysed_frames: info.identities.length,
    created_at: "2026-11-05T00:00:00Z", meta: {},
  };
  useSession.setState({ session });
  usePlayback.setState({ waitForAnalysis: false, layers: {
    shuttle: false, players: false, pose: false, court: false, labels: false, scoreBug: false,
  } });
  let video;
  if (mode === "hls") {
    createRoot(document.getElementById("root")).render(
      <VideoStage session={session} controlsVisible={false} />,
    );
    await wait(() => document.querySelector("video"));
    video = document.querySelector("video");
  } else {
    video = document.createElement("video");
    video.muted = true;
    video.src = `/fixture/${name}/proxy.mp4`;
    document.getElementById("root").append(video);
    usePlayback.getState().bindVideo(video);
    const callback = (_now, meta) => {
      frameClock.publish(timeToFrame(meta.mediaTime, fps));
      video.requestVideoFrameCallback(callback);
    };
    video.requestVideoFrameCallback(callback);
    video.addEventListener("seeked", () => frameClock.publish(timeToFrame(video.currentTime, fps)));
  }
  // These tiny fixture files fit one buffer. Wait for the final segment so a
  // first backward/forward seek cannot race manifest/segment acquisition.
  await wait(() => video.readyState >= 2 && video.videoWidth > 0
    && video.buffered.length > 0
    && video.buffered.end(video.buffered.length - 1) >= (info.identities.length - 1) / fps);
  video.pause();
  window.auditRun = async (indices) => {
    const rows = [];
    const canvas = document.createElement("canvas");
    canvas.width = 320; canvas.height = 180;
    const context = canvas.getContext("2d", { willReadFrequently: true });
    for (const target of indices) {
      const row = await new Promise((resolve) => {
        let settled = false;
        let callback;
        const finish = (meta, missing) => {
          if (settled) return;
          settled = true;
          clearTimeout(timer);
          if (callback != null) video.cancelVideoFrameCallback(callback);
          context.drawImage(video, 0, 0, 320, 180);
          let identity = 0;
          for (let bit = 0; bit < 9; bit++) {
            const x = Math.round(320 * (0.03 + 0.105 * bit)) + 3;
            const pixels = context.getImageData(x, 65, 14, 50).data;
            let sum = 0;
            for (let index = 0; index < pixels.length; index += 4)
              sum += pixels[index] + pixels[index + 1] + pixels[index + 2];
            if (sum / (pixels.length / 4 * 3) > 127) identity |= 1 << bit;
          }
          resolve({ target, expected_identity: info.identities[target], identity,
            media_time: meta?.mediaTime ?? null, current_time: video.currentTime,
            presented_frame: meta ? timeToFrame(meta.mediaTime, fps) : null,
            frame_clock: frameClock.frame, callback_missing: missing });
        };
        const timer = setTimeout(() => finish(null, true), 2500);
        const onFrame = (_now, meta) => {
          // A queued callback from the previous image is not evidence of this
          // seek. This check uses timestamps, never the expected barcode ID.
          if (video.seeking || Math.abs(meta.mediaTime - video.currentTime) > 1.01 / fps) {
            callback = video.requestVideoFrameCallback(onFrame);
            return;
          }
          finish(meta, false);
        };
        callback = video.requestVideoFrameCallback(onFrame);
        usePlayback.getState().seekFrame(target, fps);
      });
      rows.push(row);
    }
    return { name, transport: mode, fps, rows, errors,
      ready_state: video.readyState, duration: video.duration };
  };
  return { name, transport: mode, ready: true };
})().catch((error) => {
  window.setupError = String(error.stack || error);
  throw error;
});
