"""Isolated acquisition counterfactual; not registered production code."""
from bai_badminton.perception.scoreboard import ScoreboardReader, CORNERS


class FullCornerValidationReader(ScoreboardReader):
    """Keep the successful acquisition corner, not a potentially truncated board.

    One unchanged OCR call per eligible cadence. Four-corner discovery and
    existing miss-unlock count are retained. Full corner means existing bounded
    acquisition region, not a claim that every broadcast layout lies there.
    """
    def maybe_read(self, frame_idx, img):
        if self.roi is None:
            acquisition = self._corner
        else:
            acquisition = self._locked_acquisition_corner
        result = super().maybe_read(frame_idx, img)
        if result is not None:
            self._locked_acquisition_corner = acquisition
            h, w = img.shape[:2]
            self.roi = tuple(int(v * bound) for v, bound in zip(CORNERS[acquisition], (w, h, w, h), strict=True))
        return result
