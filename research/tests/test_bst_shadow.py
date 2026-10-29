"""Cache geometry cannot silently mix reference views in a BST experiment."""

import msgpack
import numpy as np

from bai_engine.schema.events import Event, Provenance
from research.evaluation.bst_shadow import detected_context, extract_frames


def calibration(reference, matrix, frame=0):
    return Event(
        session_id="fixture",
        type="calibration",
        frame_start=frame,
        frame_end=frame,
        pts_us=0,
        payload={"cam_ref": reference, "H": matrix.tolist()},
        provenance=Provenance(model="court"),
    )


def write_chunk(path, reference=10, camera=None):
    row = {
        "f": 2,
        "sh": 1,
        "cs": "VALID",
        "r": False,
        "v": "main",
        "l": False,
        "g": camera.ravel().tolist() if camera is not None else None,
        "p": [],
        "s": [12.0, 20.0],
    }
    path.write_bytes(msgpack.packb({"v": 10, "cr": reference, "frames": [row]}, use_bin_type=True))


def test_tracked_frame_composes_camera_after_reference_homography(tmp_path):
    reference = np.array([[100.0, 0.0, 640.0], [0.0, -40.0, 400.0], [0.0, 0.0, 1.0]])
    camera = np.array([[1.0, 0.0, 40.0], [0.0, 1.0, -20.0], [0.0, 0.0, 1.0]])
    write_chunk(tmp_path / "seg_00000.msgpack", camera=camera)
    # A later calibration in another reference must not win merely by recency.
    frames, _ = extract_frames(tmp_path, [calibration(10, reference), calibration(11, np.eye(3), 1)])
    np.testing.assert_allclose(frames[2].homography.H, camera @ reference)
    np.testing.assert_allclose(frames[2].homography.image_to_court(np.array([[680.0, 380.0]])), [[0.0, 0.0]])


def test_tracked_reference_without_per_frame_camera_is_unavailable(tmp_path):
    write_chunk(tmp_path / "seg_00000.msgpack")
    frames, report = extract_frames(tmp_path, [calibration(10, np.eye(3))])
    assert frames[2].homography is None
    assert report["frame_calibration"] == {"tracked_camera_pose_unavailable": 1}


def test_untracked_static_reference_does_not_require_camera_matrix(tmp_path):
    write_chunk(tmp_path / "seg_00000.msgpack", reference=None)
    frames, _ = extract_frames(tmp_path, [calibration(None, np.eye(3))])
    np.testing.assert_array_equal(frames[2].homography.H, np.eye(3))


def test_neighbor_contacts_come_from_machine_rallies_without_cross_rally_borrowing():
    strokes = [
        Event(
            event_id=f"s{frame}",
            session_id="fixture",
            type="stroke",
            frame_start=frame,
            frame_end=frame,
            pts_us=0,
            provenance=Provenance(model="rules"),
        )
        for frame in (10, 20, 22)
    ]
    rally = Event(
        session_id="fixture",
        type="rally_end",
        frame_start=0,
        frame_end=21,
        pts_us=0,
        payload={"shots": [{"event_id": "s10"}, {"event_id": "s20"}]},
        provenance=Provenance(model="fsm"),
    )
    assert detected_context([rally, *strokes], strokes) == {"s10": (None, 20), "s20": (10, None), "s22": (None, None)}
