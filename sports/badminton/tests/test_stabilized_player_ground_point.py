"""Camera registration preserves the observed floor point, not an enclosing box's foot.

Independent synthetic coordinate invariants; actual fixed-camera Test1 has
identity poses and therefore does not establish a measured improvement here.
"""
import numpy as np
import pytest

from bai_badminton.court import Homography
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _stabilise
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs
from bai_engine.store import EventStore


def inverse_camera(kind):
    if kind == "identity":
        return np.eye(3)
    if kind == "rotation":
        angle = np.deg2rad(20)
        a, b = np.cos(angle), np.sin(angle)
        return np.array([[a, -b, 640 - 640*a + 360*b], [b, a, 360 - 640*b - 360*a], [0, 0, 1.]])
    return np.array([[1.02, .03, 4], [-.02, .99, 7], [.0001, -.0002, 1.]])


def expected_ground(point, inverse):
    # Explicit homogeneous point algebra, independent of bbox-envelope code.
    x, y = point
    w = inverse[2, 0]*x + inverse[2, 1]*y + inverse[2, 2]
    rx = (inverse[0, 0]*x + inverse[0, 1]*y + inverse[0, 2])/w
    ry = (inverse[1, 0]*x + inverse[1, 1]*y + inverse[1, 2])/w
    return ((rx - 640)/100, (360 - ry)/50)


def engine_case(tmp_path, inverse, *, state=CalibrationState.VALID):
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path/"e.sqlite", "S1"))
    h = Homography(np.array([[100.,0,640],[0,-50.,360],[0,0,1.]]),0,4)
    eng.set_calibration(0,h,cam_ref=10)
    frames=[]
    for i in range(12):
        people=[PersonObs(track_id=0,bbox=np.array([600.,200.,640.,500.]),conf=.95,detector_matched=True),PersonObs(track_id=1,bbox=np.array([620.,170.,660.,300.]),conf=.95,detector_matched=True)]
        frames.append(FramePerception(frame_idx=i,shuttle_xy=None,shuttle_conf=0,persons=people,cam=np.linalg.inv(inverse),view="main",calibration_state=state,detector_observed=True))
    eng.ingest(ChunkPerception(0,11,frames,models={"player_detector":"independent_fixture@1"},cam_ref=10))
    return eng,frames,h


@pytest.mark.parametrize("kind",["rotation","projective","identity"])
def test_current_engine_projects_the_original_detector_ground_point(tmp_path,kind):
    inv=inverse_camera(kind);eng,frames,_=engine_case(tmp_path,inv)
    snapshots=eng._participant_frames[-1]
    assert {s.track_id for s in snapshots.values()} == {0,1}
    by_track={s.track_id:s for s in snapshots.values()}
    assert by_track[0].court_xy == pytest.approx(expected_ground((620,500),inv),abs=1e-10)
    assert by_track[1].court_xy == pytest.approx(expected_ground((640,300),inv),abs=1e-10)
    # Stabilisation must not rewrite raw image evidence used for overlays.
    np.testing.assert_array_equal(frames[-1].persons[0].bbox,[600,200,640,500])
    assert frames[-1].persons[0].court_xy is None


def test_unavailable_geometry_still_has_no_authoritative_floor_coordinates(tmp_path):
    eng,frames,_=engine_case(tmp_path,inverse_camera("rotation"),state=CalibrationState.LOST)
    assert eng._geometry_valid == [False]*12
    assert all(s.court_xy is None for per_frame in eng._participant_frames for s in per_frame.values())
    assert all(t.court_x is None and t.court_y is None for t in eng.drain_tracks())
    np.testing.assert_array_equal(frames[-1].persons[0].bbox,[600,200,640,500])


def test_no_calibration_stabilisation_compatibility():
    raw=PersonObs(track_id=3,bbox=np.array([600.,200.,640.,500.]),conf=.8)
    result=_stabilise(raw,inverse_camera("rotation"))
    assert result.court_xy is None
    assert result.track_id==3 and result.conf==.8
    np.testing.assert_array_equal(raw.bbox,[600,200,640,500])
