"""Controlled tensor/index contract check; synthetic heatmaps, never real inference."""

import json
from pathlib import Path

import numpy as np

from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3

records = []
for n in [1, 7, 8, 9, 48, 60, 64]:
    m = TrackNetV3.__new__(TrackNetV3)
    m.seq_len, m.in_dim, m.batch, m.threshold = 8, 27, 4, 0.5
    m.bg = BackgroundModel()
    windows = []

    def forward(x, windows=windows):
        y = np.zeros((len(x), 8, HEIGHT, WIDTH), np.float32)
        for b, t in enumerate(x):
            indices = [round(float(t[(j + 1) * 3, 0, 0]) * 255) for j in range(8)]
            windows.append(indices)
            for j, index in enumerate(indices):
                y[b, j, 20, 10 + index] = 1
        return y

    m._forward = forward
    images = [np.full((36, 64, 3), i, np.uint8) for i in range(n)]
    detections = m.detect(images, step=8)
    assert len(detections) == n and all(d is not None for d in detections)
    assert np.allclose([d.x for d in detections], [(10 + i) / 8 for i in range(n)])
    records.append(
        {"frames": n, "window_inputs": windows, "all_real_frame_outputs_correct": True, "synthetic_only": True}
    )
path = Path("artifacts/benchmarking/investigation/audit_c/window_contract.json")
path.write_text(json.dumps(records, indent=2) + "\n")
print(json.dumps(records, indent=2))
