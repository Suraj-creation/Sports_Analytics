import msgpack
import numpy as np
import pytest

from bai_badminton.perception.diagnostics import DiagnosticSelection, FrameDiagnostic, summarize_heatmap
from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3


def test_competing_weak_and_masked_components_are_retained_without_mutation():
    hm = np.zeros((12, 16), np.float32)
    hm[2, 2] = 0.9
    hm[5, 7] = 0.55
    hm[9, 12] = 0.23
    mask = np.ones_like(hm, np.uint8)
    mask[2, 2] = 0
    original, original_mask = hm.copy(), mask.copy()
    result = summarize_heatmap(hm, 0.5, mask, scale=(2.5, 2.5), selection=DiagnosticSelection(), window_votes=2)
    assert result.reason == "accepted"
    assert result.raw_peak == pytest.approx(0.9)
    assert result.masked_peak == pytest.approx(0.55)
    assert [c.mask_allows_peak for c in result.candidates] == [False, True, True]
    assert [c.selected_peak for c in result.candidates] == [False, True, False]
    assert [c.above_inference_threshold for c in result.candidates] == [True, True, False]
    assert result.candidates[0].peak_xy == (5, 5)
    np.testing.assert_array_equal(hm, original)
    np.testing.assert_array_equal(mask, original_mask)


@pytest.mark.parametrize("kind", ["no_positive_peak", "below_threshold", "mask_rejected"])
def test_different_rejection_causes_do_not_collapse_to_zero(kind):
    hm = np.zeros((8, 8), np.float32)
    mask = np.ones_like(hm, np.uint8)
    if kind == "below_threshold":
        hm[2, 2] = 0.25
    elif kind == "mask_rejected":
        hm[2, 2] = 0.8
        mask[2, 2] = 0
    result = summarize_heatmap(hm, 0.5, mask, scale=(1, 1), selection=DiagnosticSelection(), window_votes=1)
    assert result.reason == kind
    assert all(not c.selected_peak for c in result.candidates)


def test_roundtrip_keeps_frame_identity_and_uncalibrated_semantics():
    hm = np.zeros((8, 8), np.float32)
    hm[3, 4] = 0.4
    summary = summarize_heatmap(hm, 0.5, None, scale=(2.5, 2.5), selection=DiagnosticSelection(), window_votes=1)
    value = FrameDiagnostic(123, 4.1, 2, "main", "VALID", summary, "model_ran", "tracknet-v3")
    assert FrameDiagnostic.from_dict(value.to_dict()) == value
    assert summary.support_semantics == "raw_model_support_uncalibrated"
    assert summary.candidates[0].peak_support == pytest.approx(0.4)


@pytest.mark.parametrize(
    "value",
    [
        {"ranges": [[0, 4000]]},
        {"ranges": [[4, 8], [8, 12]]},
        {"ranges": [[-1, 3]]},
        {"ranges": [[3, 2]]},
        {"ranges": [[True, 3]]},
        {"top_k": 9},
        {"top_k": 0},
        {"top_k": True},
        {"candidate_floor": 0},
        {"candidate_floor": float("nan")},
        {"ranges": [3]},
        {"unknown": 1},
    ],
)
def test_selection_rejects_unbounded_or_invalid_configuration(value):
    with pytest.raises(ValueError):
        DiagnosticSelection.parse(value)


def test_selection_is_opt_in_with_bounded_inclusive_ranges():
    selection = DiagnosticSelection.parse({"ranges": [[3, 5], [8, 9]], "top_k": 2})
    assert [i for i in range(12) if selection.includes(i)] == [3, 4, 5, 8, 9]
    assert not DiagnosticSelection().includes(4)


def test_candidate_limit_and_row_major_ties_are_deterministic():
    hm = np.zeros((24, 24), np.float32)
    hm[::3, ::3] = 0.7
    summary = summarize_heatmap(hm, 0.5, None, scale=(1, 1), selection=DiagnosticSelection(top_k=2), window_votes=1)
    assert len(summary.candidates) == 2
    assert [c.peak_xy for c in summary.candidates] == [(0, 0), (3, 0)]
    assert summary.candidates[0].selected_peak


def synthetic_model():
    model = TrackNetV3.__new__(TrackNetV3)
    model.seq_len, model.in_dim, model.batch, model.threshold = 8, 27, 4, 0.5
    model.bg = BackgroundModel(every=1, capacity=4, refresh=1)

    def forward(inputs):
        heatmaps = np.zeros((len(inputs), 8, HEIGHT, WIDTH), np.float32)
        for b, values in enumerate(inputs):
            for index in range(8):
                marker = round(float(values[3 + 3 * index, 0, 0]) * 255)
                heatmaps[b, index, 20 + marker % 100, 50 + marker % 200] = 0.55 + 0.01 * (marker % 5)
                heatmaps[b, index, 200, 350] = 0.28
        return heatmaps

    model._forward = forward
    return model


@pytest.mark.parametrize("count,step", [(1, 8), (7, 8), (8, 8), (9, 4), (60, 8), (64, 4)])
def test_optional_diagnostics_preserve_every_prediction_background_and_window_vote(count, step):
    frames = [np.full((72, 128, 3), i + 1, np.uint8) for i in range(count)]
    shots = [0 if i < count // 2 else 1 for i in range(count)]
    masks = [np.ones((HEIGHT, WIDTH), np.uint8) for _ in frames]
    ordinary, instrumented = synthetic_model(), synthetic_model()
    expected = ordinary.detect(frames, shots, step=step, masks=masks)
    indices = {0, count - 1}
    actual, summaries = instrumented.detect_with_diagnostics(
        frames,
        shots,
        step=step,
        masks=masks,
        selection=DiagnosticSelection(),
        indices=indices,
    )
    assert actual == expected
    assert [i for i, value in enumerate(summaries) if value is not None] == sorted(indices)
    assert instrumented.bg._count == ordinary.bg._count
    for shot in set(shots):
        np.testing.assert_array_equal(instrumented.bg._median[shot], ordinary.bg._median[shot])
    assert all(summaries[i].window_votes >= 1 for i in indices)
    assert all(len(summaries[i].background_sha256) == 64 for i in indices)


def test_unknown_diagnostic_schema_or_mismatched_frame_is_rejected(tmp_path):
    from test_plugin_discipline import make_session

    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception_types import ChunkPerception, FramePerception
    from bai_badminton.plugin import StaleCacheError

    session = make_session(tmp_path, "singles")
    diagnostic = FrameDiagnostic(0, 0.0, 0, "main", "VALID", None, "provider_unavailable", "unavailable")
    frame = FramePerception(
        0,
        None,
        0.0,
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
        view="main",
        diagnostic=diagnostic,
    )
    payload = session.encode_perception(ChunkPerception(0, 0, [frame]))
    assert session.decode_perception(payload, diagnostic=True).frames[0].diagnostic == diagnostic
    for field, value in (("schema", "unknown:v9"), ("frame_idx", 1), ("shot_id", 9)):
        data = msgpack.unpackb(payload, raw=False)
        data["frames"][0]["dg"][field] = value
        with pytest.raises(StaleCacheError):
            session.decode_perception(msgpack.packb(data, use_bin_type=True), diagnostic=True)


def test_pre_diagnostic_codec_is_readable_only_for_diagnostics_and_never_carries_new_values(tmp_path):
    from test_plugin_discipline import make_session

    from bai_badminton.perception.calibration_state import CalibrationState
    from bai_badminton.perception_types import ChunkPerception, FramePerception
    from bai_badminton.plugin import StaleCacheError

    session = make_session(tmp_path, "singles")
    frame = FramePerception(0, None, 0, calibration_state=CalibrationState.VALID, detector_observed=True)
    data = msgpack.unpackb(session.encode_perception(ChunkPerception(0, 0, [frame])), raw=False)
    data["v"] = 17
    del data["frames"][0]["dg"]
    payload = msgpack.packb(data, use_bin_type=True)
    assert session.decode_perception(payload, diagnostic=True).frames[0].diagnostic is None
    with pytest.raises(StaleCacheError, match="sequential"):
        session.decode_perception(payload)


def test_mask_connected_component_keeps_explicit_selected_masked_peak():
    heatmap = np.zeros((8, 8), np.float32)
    heatmap[2, 2:5] = [0.9, 0.2, 0.7]
    mask = np.ones_like(heatmap, np.uint8)
    mask[2, 2] = 0
    summary = summarize_heatmap(
        heatmap,
        0.5,
        mask,
        scale=(1, 1),
        selection=DiagnosticSelection(),
        window_votes=1,
        decoded_xy=(4, 2),
    )
    assert summary.candidates[0].peak_xy == (2, 2)
    assert summary.selected_masked_peak_xy == (4, 2)
    assert summary.decoded_xy == (4, 2)
    assert summary.candidate_extraction == "top_k_components_above_diagnostic_floor"


@pytest.mark.parametrize("value", [None, 42, [], "bad"])
def test_malformed_diagnostic_top_level_is_a_controlled_validation_error(value):
    with pytest.raises(ValueError):
        FrameDiagnostic.from_dict(value)


@pytest.mark.parametrize(
    "extra",
    [
        {"frame_idx": 4},
        {"large": list(range(100))},
        {"nonfinite": float("nan")},
        {"tensor": np.zeros(3)},
        {"deep": {"a": {"b": {"c": {"d": {"e": {"f": 1}}}}}}},
    ],
)
def test_nested_player_diagnostics_are_frame_bound_finite_and_bounded(extra):
    players = {"schema": "player-tracking-diagnostics:v1", "frame_idx": 3, **extra}
    with pytest.raises(ValueError):
        FrameDiagnostic(3, 0.1, 0, "main", "VALID", None, "provider_unavailable", "unavailable", players)


def test_player_diagnostic_values_are_detached_from_provider_reuse():
    players = {"schema": "player-tracking-diagnostics:v1", "frame_idx": 3, "roi_rejected": [{"bbox": [1, 2, 3, 4]}]}
    value = FrameDiagnostic(3, 0.1, 0, "main", "VALID", None, "provider_unavailable", "unavailable", players)
    players["roi_rejected"][0]["bbox"][0] = 999
    assert value.players["roi_rejected"][0]["bbox"][0] == 1


def test_player_admission_carry_and_reset_diagnostics_do_not_change_boxes():
    from bai_badminton.perception.players import CourtROI, PlayerPerception

    boxes = np.array([[10.0, 10, 30, 70], [300, 10, 330, 70]])

    def detector(_):
        return boxes.copy(), np.array([0.95, 0.9])

    def setup():
        p = PlayerPerception(detector, None, 30, det_stride=2, pose_stride=0)
        p.set_roi(CourtROI(np.array([[0.0, 0], [100, 0], [100, 100], [0, 100]], np.float32), pad_px=0))
        return p

    plain, observed = setup(), setup()
    image = np.zeros((400, 400, 3), np.uint8)
    for frame in (0, 2, 3):
        observed.set_diagnostics(True, 2)
        expected = plain.process(frame, image)
        actual = observed.process(frame, image)
        assert len(actual) == len(expected)
        if frame != 0:
            assert len(actual) == 1
        for found, reference in zip(actual, expected, strict=True):
            np.testing.assert_array_equal(found.bbox, reference.bbox)
            assert found.conf == reference.conf
        assert observed.last_diagnostic["frame_idx"] == frame
        if frame % 2 == 0:
            assert observed.last_diagnostic["pre_roi_count"] == 2
            assert observed.last_diagnostic["roi_rejected_count"] == 1
        else:
            assert observed.last_diagnostic["fresh_matched_count"] == 0
    observed.on_cut()
    assert observed.last_diagnostic is None


def test_direct_diagnostic_calls_cannot_exceed_the_frame_budget():
    model = synthetic_model()
    frames = [np.zeros((4, 4, 3), np.uint8)] * 3601
    with pytest.raises(ValueError, match="budget"):
        model.detect_with_diagnostics(
            frames,
            [0] * len(frames),
            step=8,
            masks=None,
            selection=DiagnosticSelection(),
            indices=set(range(len(frames))),
        )
