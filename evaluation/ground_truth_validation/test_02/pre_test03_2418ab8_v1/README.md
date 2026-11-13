# Test 2: candidate 2418ab8 regression evidence

Status: full fresh neural inference and separate postprocessing are complete; independent metrics/source review and regression diagnosis remain pending. This is **not** accepted cross-test validation and does not authorize Test 3.

- [Original inference](original_inference/): 29,296 fresh frames; successful original worker and parent. Its outer analysis failure remains unchanged.
- [Separate completed postprocessing](postprocessing/): explicit actual native producer and tool roots; no new NN; all original artifacts unchanged; own-run full semantic replay parity passed.
- [Complete comparison](comparison.md) and [component matrices](metrics/): unchanged matching, thresholds and original annotations; all seven Test 2 files accounted for. Physical metrics without independent labels remain null.
- [All nine weak resets and retained controls](weak_scene_evidence/): 75 synchronized source/baseline/current frames.
- [Largest generated-reference timing shift](delayed_start_evidence/): all 111 source frames800–910, covering preparation versus visible serve near the different reference starts.
- [Independent numeric/provenance review](independent_review/): complete population, all changed rows and pending source-review plan.
- [Newly missed short event](short_event_evidence/): all 86 source frames 11690–11775, including coarse reference 33 [11700,11760).

Coarse F1 changes 0.9200→0.9127516779 (69/6/6→68/6/7), while generated-rally F1 changes 0.9189189189→0.9251700680 (68/7/5→68/6/5). Coarse mean IoU improves 0.8306646002→0.8380953372; generated mean IoU worsens 0.8493108146→0.8307896604. These different changes are not a physical contact accuracy claim. The additional coarse miss and changed temporal boundaries are under investigation.

The exact completed source video is retained for diagnosis. No Test 2 media has been deleted, and no Test 3 data/video has been accessed in this phase. Navigation links preserve the original actual NN location rather than pretending it ran inside this index.
