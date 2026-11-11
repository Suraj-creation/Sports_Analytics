# Sequential benchmark index

Frozen improved pipeline; legacy rally-reference agreement. Tests 5 and 8 skipped by explicit user instruction. All eight requested evaluations are verified; see the consolidated report.

| Test | Status | TP / FP / FN | Precision | Recall | F1 | Record |
|---|---|---|---|---|---|---|
| 1 | historical verified | 36 / 0 / 0 | 1.000000 | 1.000000 | 1.000000 | [record.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test1_historical/record.json) |
| 2 | historical verified | 68 / 7 / 5 | 0.906667 | 0.931507 | 0.918919 | [record.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test2_historical/record.json) |
| 3 | evaluated; artifacts verified | 18 / 6 / 1 | 0.750000 | 0.947368 | 0.837209 | [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test3/REPORT.md) |
| 4 | evaluated; artifacts verified | 38 / 8 / 3 | 0.826087 | 0.926829 | 0.873563 | [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test4/REPORT.md) |
| 5 | skipped by user | — | — | — | — | [user_skip.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test5/user_skip.json) |
| 6 | evaluated; artifacts verified | 35 / 12 / 7 | 0.744681 | 0.833333 | 0.786517 | [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test6/REPORT.md) |
| 7 | evaluated; artifacts verified | 28 / 4 / 2 | 0.875000 | 0.933333 | 0.903226 | [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test7/REPORT.md) |
| 8 | skipped by user | — | — | — | — | [user_skip.json](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test8/user_skip.json) |
| 9 | evaluated; artifacts verified | 69 / 15 / 13 | 0.821429 | 0.841463 | 0.831325 | [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test9/REPORT.md) |
| 10 | evaluated; artifacts verified | 85 / 13 / 8 | 0.867347 | 0.913978 | 0.890052 | [REPORT.md](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10_retry1/REPORT.md) |

Test10 initial failure is preserved in [test10](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/test10/failure.json). The separate retry extends only the original FFprobe frame-count deadline from 300 to 1800 seconds; inference, profile, models and matching remain frozen.

Historical Tests1/2 retain their original catalogue-publication failure receipts and independent completion proofs. No earlier results are overwritten.

[Consolidated eight-video benchmark](/home/administrator/Desktop/sport-analytics/sequential-benchmark-20261106/consolidated_v1/REPORT.md)
