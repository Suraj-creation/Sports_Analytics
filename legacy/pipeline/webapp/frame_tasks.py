"""
frame_tasks.py
---------------
Pre-extracts a small set of candidate court-annotation frames right after
upload, so an intern's court task only needs a still image -- never the
live video -- and the multi-hour pipeline run isn't triggered until they
submit their 8 points.

Runs on its own small thread pool, deliberately separate from jobs.py's
single-item pipeline queue: frame ranking is cheap CPU/OpenCV work, not
GPU inference, and sharing the pipeline queue would make every
batch-uploaded video wait behind every prior video's full run just to get
a frame extracted -- defeating the point of decoupling annotation from
pipeline runtime.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2

import db
import jobs

PROJECT_ROOT = jobs.PROJECT_ROOT
ANALYSIS_DIR = PROJECT_ROOT / "analysis"
CANDIDATES_DIR = Path(__file__).resolve().parent / "uploads" / "candidates"
CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)

N_CANDIDATES = 5

_executor = ThreadPoolExecutor(max_workers=2)


def submit(job_id):
    _executor.submit(_extract_candidates_safe, job_id)


def _extract_candidates_safe(job_id):
    try:
        _extract_candidates(job_id)
    except Exception as e:
        job = jobs.JOBS.get(job_id)
        if job is not None:
            job.court_task_status = "extraction_failed"
            job.error = f"Frame extraction failed: {e}"
            job.persist()


def _extract_candidates(job_id):
    job = jobs.JOBS.get(job_id)
    if job is None:
        return
    match_folder = Path(job.match_folder)
    match_folder.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(PROJECT_ROOT))
    import run_full_pipeline  # noqa: E402 -- heavy work is gated by __main__, safe to import

    match_video = match_folder / f"{job.match_name}.mp4"
    # Same call the pipeline itself makes later (idempotent) -- guarantees
    # candidates come from the exact video the pipeline will use, so pixel
    # coordinates in the submitted court.json line up, and makes the
    # pipeline's own later call a no-op skip.
    run_full_pipeline._preprocess_video(Path(job.video_path), match_video, 1280, 720, 30.0)

    sys.path.insert(0, str(ANALYSIS_DIR))
    from frame_picker import rank_candidate_frames

    ranked = rank_candidate_frames(str(match_video), step_sec=10.0, max_candidates=40,
                                   court_type=job.court_type, verify_stable=True)
    top = ranked[:N_CANDIDATES]

    out_dir = CANDIDATES_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(match_video))
    candidates = []
    for frame_no, score, _ in top:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if not ok:
            continue
        jpg_path = out_dir / f"{frame_no}.jpg"
        cv2.imwrite(str(jpg_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 92])
        candidates.append({
            "frame_no": int(frame_no), "score": round(float(score), 4),
            "width": int(frame.shape[1]), "height": int(frame.shape[0]),
            "image_url": f"/api/court-task/{job_id}/frame/{len(candidates)}.jpg",
        })
    cap.release()

    if not candidates:
        raise RuntimeError("Frames were ranked but none could be read/saved")

    job.court_task_candidates = candidates
    job.court_task_selected_idx = 0
    job.court_task_status = "pending"
    job.persist()
