"""Optional image-only foreground port does not add participant observations."""

from test_content_pipeline_integration import chunk, perception

from bai_badminton.perception.scene_change import ForegroundRegion


def test_scene_receives_detached_foreground_even_when_people_authority_withheld(tmp_path, monkeypatch):
    pipeline, ports, _ = perception(tmp_path, monkeypatch)
    tracking = ports["tracking"]

    def process(frame, image, strides):
        tracking.last_detector_observed = True
        return []

    tracking.process = process
    tracking.foreground_regions = lambda frame: tuple(
        ForegroundRegion(frame, f"visual:{k}", (10.0 + k * 40, 10.0, 30.0 + k * 40, 100.0), True, True)
        for k in range(2)
    )
    result = pipeline.process(chunk(0, 3), in_play=True)
    assert all(frame.persons == [] for frame in result.frames)
    for frame, args in ports["content_continuity"].calls[1:]:
        assert len(args["previous_regions"]) == 2
        assert {r.key for r in args["previous_regions"]} == {"visual:0", "visual:1"}
        assert all(r.frame == frame - 1 for r in args["previous_regions"])
    assert all(len(frame.foreground_regions) == 2 for frame in result.frames)
    pipeline.close()


def test_no_foreground_port_preserves_existing_provider_fallback(tmp_path, monkeypatch):
    pipeline, ports, _ = perception(tmp_path, monkeypatch, count=4)
    assert not hasattr(ports["tracking"], "foreground_regions")
    pipeline.process(chunk(0, 3), in_play=True)
    for _, args in ports["content_continuity"].calls[1:]:
        assert len(args["previous_regions"]) == 4
        assert all(r.key.startswith("track:") for r in args["previous_regions"])
    pipeline.close()
