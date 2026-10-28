# Optional OSNet appearance review

`bai_badminton.perception.offline_reid` is a local, opt-in diagnostic. It is not connected to production matching, does not change participants, and does not download files. It gives a cosine similarity only; it cannot confirm identity or calculate a probability. Similar clothes, lighting changes, pose and court-side changes can produce false matches. Do not use its output as an authoritative identity or scoring decision.

The adapter requires the exact `osnet_ain_x0_25.pt` checkpoint from [LibreYOLO/LibreReID-osnet](https://huggingface.co/LibreYOLO/LibreReID-osnet), SHA-256 `ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347`. Provide its local path explicitly; the adapter verifies the digest before loading. No weights are committed. The model card says training datasets have research-oriented terms; review them before any production use. The adapted OSNet code and both MIT notices are included in `sports/badminton/src/bai_badminton/perception/_vendor/`.

From the server worktree, source `../gpu-env.sh`, use the existing `.venv` and place its package source on `PYTHONPATH`. Use a local, manually selected video frame and person bounding boxes, then discard the returned vectors as soon as comparisons finish. Example (replace frame and boxes with actual local observations):

```python
from bai_badminton.perception.offline_reid import OSNetReviewEmbedder, compare_features

reviewer = OSNetReviewEmbedder("/path/to/osnet_ain_x0_25.pt", device="cuda:0")
features = reviewer.embed(bgr_frame, [[x1, y1, x2, y2], [x3, y3, x4, y4]])
cue = compare_features(features[0], features[1])
print(cue)  # identity_decision is always unresolved; probability is None
del features
```

Frames are BGR uint8 up to 4K and crops must be wholly within the frame. The default batch is limited to eight crops, with a hard maximum of 16. The adapter does not save frames or features, but the caller is responsible for not writing them to disk, logs or external services. Real-video feasibility was checked on four approximate crops of one unlabelled frame; no identity accuracy or long-video stability was established.
