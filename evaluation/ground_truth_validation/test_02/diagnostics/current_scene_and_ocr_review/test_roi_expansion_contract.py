"""RED acquisition contract, using deterministic OCR observations only.

These synthetic engineering controls are not Part2 sporting ground truth.
Production remains untouched; a failing case is evidence for review, not a
permission to apply an unvalidated ROI policy to the active baseline.
"""
from types import SimpleNamespace
import numpy as np

from bai_badminton.perception.scoreboard import ScoreboardReader, parse_scoreboard


def box(x, y, width=60, height=20):
    return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]


class VisibleFieldsOCR:
    """Returns only text boxes entirely inside supplied image crop.

    The fixture's acquisition corner and locked ROI both begin at (0,0), so
    local/global field coordinates coincide. A pixel marker chooses layout.
    """
    def __call__(self, image):
        fields = [(box(10, 10), 'ALPHA'), (box(120, 10, 20), '21'),
                  (box(10, 40), 'BETA'), (box(120, 40, 20), '19')]
        if image[0, 0, 0] == 255:
            fields += [(box(200, 10, 20), '1'), (box(200, 40, 20), '0')]
        h, w = image.shape[:2]
        fields = [(b, text) for b, text in fields if b[2][0] <= w and b[2][1] <= h]
        return SimpleNamespace(boxes=[b for b, _ in fields], txts=[text for _, text in fields],
                               scores=[.99] * len(fields))


def frames():
    narrow = np.zeros((720, 1280, 3), dtype=np.uint8)
    expanded = narrow.copy()
    expanded[0, 0] = 255
    return narrow, expanded


def test_complete_corner_observations_preserve_new_rightmost_column():
    _, expanded = frames()
    result = VisibleFieldsOCR()(expanded[:180, :576])
    parsed = parse_scoreboard(result.boxes, result.txts, result.scores, 30)
    assert parsed is not None
    assert parsed[0].rows == (('ALPHA', 1), ('BETA', 0))


def test_unchanged_board_remains_readable_under_locked_roi():
    narrow, _ = frames()
    reader = ScoreboardReader(VisibleFieldsOCR(), every=30)
    assert reader.maybe_read(0, narrow).rows == (('ALPHA', 21), ('BETA', 19))
    initial = reader.roi
    assert reader.maybe_read(30, narrow).rows == (('ALPHA', 21), ('BETA', 19))
    assert reader.roi == initial


def test_expanded_board_must_not_silently_publish_completed_game_as_current():
    narrow, expanded = frames()
    reader = ScoreboardReader(VisibleFieldsOCR(), every=30)
    assert reader.maybe_read(0, narrow).rows == (('ALPHA', 21), ('BETA', 19))
    # All new current digits lie in the normal acquisition corner but outside
    # the old locked ROI. Returning old columns as current is the defect.
    for frame in range(30, 391, 30):
        reading = reader.maybe_read(frame, expanded)
        assert reading is None or reading.rows == (('ALPHA', 1), ('BETA', 0))
