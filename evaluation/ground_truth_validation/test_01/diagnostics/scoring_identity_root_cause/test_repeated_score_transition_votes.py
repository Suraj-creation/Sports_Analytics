"""Red regression: retries of one source point must not become independent row-map votes."""
from bai_badminton.score_ocr import ScoreReconciler
from bai_badminton.perception_types import ScoreReading

def test_repeated_single_transition_cannot_establish_row_mapping():
 rec=ScoreReconciler()
 for frame,points in [(0,(10,10)),(30,(10,10)),(90,(11,10)),(120,(11,10))]:
  rec.add(ScoreReading(frame,(('ALPHA',points[0]),('BETA',points[1])),conf=.99))
 ref=rec.source_transition(40,80,120,lookback=60)
 assert ref is not None
 results=[rec.winner_from_ocr({'P1':0,'P2':0},40,80,120,'P1',lookback=60) for _ in range(3)]
 assert rec.row_map is None, ('one source transition counted three times',ref.transition_id,rec._votes,results)
