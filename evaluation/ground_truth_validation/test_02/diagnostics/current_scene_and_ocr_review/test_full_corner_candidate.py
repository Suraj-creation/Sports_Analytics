"""Engineering controls for isolated full-corner acquisition counterfactual."""
import numpy as np
from full_corner_candidate import FullCornerValidationReader
from test_roi_expansion_contract import VisibleFieldsOCR, frames


def test_complete_available_corner_keeps_new_column_without_extra_ocr_calls():
    narrow, expanded = frames()
    reader = FullCornerValidationReader(VisibleFieldsOCR(), every=30)
    assert reader.maybe_read(0, narrow).rows == (('ALPHA', 21), ('BETA', 19))
    assert reader.calls == 1
    assert reader.maybe_read(15, expanded) is None
    assert reader.calls == 1
    for frame in range(30, 391, 30):
        assert reader.maybe_read(frame, expanded).rows == (('ALPHA', 1), ('BETA', 0))
    assert reader.calls == 14


def test_unchanged_board_remains_readable_and_corner_stable():
    narrow, _ = frames()
    reader = FullCornerValidationReader(VisibleFieldsOCR(), every=30)
    assert reader.maybe_read(0, narrow).rows == (('ALPHA', 21), ('BETA', 19))
    roi = reader.roi
    assert reader.maybe_read(30, narrow).rows == (('ALPHA', 21), ('BETA', 19))
    assert reader.roi == roi == (0, 0, 576, 180)


def test_exactly_existing_miss_budget_unlocks_and_resumes_corner_search():
    narrow, _ = frames()
    class DisappearingOCR(VisibleFieldsOCR):
        def __call__(self, image):
            if image[0, 0, 0] == 127:
                return None
            return super().__call__(image)
    reader = FullCornerValidationReader(DisappearingOCR(), every=30)
    assert reader.maybe_read(0, narrow) is not None
    blank = np.full_like(narrow, 127)
    for count in range(1, reader.max_misses + 1):
        assert reader.maybe_read(30 * count, blank) is None
        assert (reader.roi is None) is (count == reader.max_misses)
    assert reader._corner == 1
