# Manifest-driven component evaluation

Native complete fresh worker and original cache guards passed. Generated references measure agreement, not physical accuracy. Original data and predictions are unchanged.

## Interval reference agreement

| Reference | Declared role | TP | FP | FN | Precision | Recall | F1 | Mean IoU |
|---|---|---|---|---|---|---|---|---|
| Test1_Full.csv | coarse_legacy_label_agreement | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 | 0.8421299050542989 |
| Test1_Full2.csv | partial_mixed_label_candidate | 19 | unavailable | 1 | unavailable | 0.95 | unavailable | 0.8468352271418205 |
| Test1_Full_rally.csv | legacy_generated_reference_agreement | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 | 0.8710256650394885 |
| Test1_Full_rev_T.csv | legacy_generated_reference_agreement | 34 | 2 | 1 | 0.9444444444444444 | 0.9714285714285714 | 0.9577464788732394 | 0.8678779703223529 |
| Test1_Full_rev_T4.csv | legacy_generated_reference_agreement | 36 | 0 | 2 | 1.0 | 0.9473684210526315 | 0.972972972972973 | 0.8710256650394885 |
| win_predictions.csv | legacy_generated_reference_agreement | 36 | 0 | 0 | 1.0 | 1.0 | 1.0 | 0.8710256650394885 |

## Test1_Full.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 30.88888888888889 | 22.5 | 41.26809367484226 | 97.0 | 73.0 | 30.77777777777778 | 22.5 |
| end_frame | 14.0 | 12.5 | 16.74149867179691 | 44.0 | 26.0 | 0.7777777777777778 | 3.0 |
| start_time_sec | 1.0296296296296341 | 0.7500000000000231 | 1.3756031224947443 | 3.2333333333333343 | 2.43333333333333 | 1.0259259259259306 | 0.7500000000000231 |
| end_time_sec | 0.46666666666666856 | 0.4166666666666572 | 0.5580499557265648 | 1.4666666666666401 | 0.8666666666666742 | 0.025925925925926033 | 0.09999999999999432 |
| duration_sec | 1.159259259259263 | 0.8000000000000114 | 1.4883498194931137 | 3.6666666666666714 | 2.4833333333333485 | -1.0000000000000044 | -0.8000000000000114 |

## Test1_Full.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.027777777777777776 | 0.027777777777777776 |
| start | 3 | 0.1 | 4 | 0.1111111111111111 | 0.1111111111111111 |
| start | 5 | 0.16666666666666666 | 8 | 0.2222222222222222 | 0.2222222222222222 |
| start | 10 | 0.3333333333333333 | 10 | 0.2777777777777778 | 0.2777777777777778 |
| start | 15 | 0.5 | 15 | 0.4166666666666667 | 0.4166666666666667 |
| start | 30 | 1.0 | 22 | 0.6111111111111112 | 0.6111111111111112 |
| end | 1 | 0.03333333333333333 | 1 | 0.027777777777777776 | 0.027777777777777776 |
| end | 3 | 0.1 | 3 | 0.08333333333333333 | 0.08333333333333333 |
| end | 5 | 0.16666666666666666 | 5 | 0.1388888888888889 | 0.1388888888888889 |
| end | 10 | 0.3333333333333333 | 16 | 0.4444444444444444 | 0.4444444444444444 |
| end | 15 | 0.5 | 24 | 0.6666666666666666 | 0.6666666666666666 |
| end | 30 | 1.0 | 34 | 0.9444444444444444 | 0.9444444444444444 |

## Test1_Full.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8421299050542989 |
| median_iou | 0.865878787878787 |
| minimum_iou | 0.620253164556963 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 75.0 |
| percent IoU strictly above 0.9 | 44.44444444444444 |
| percent IoU strictly above 0.95 | 19.444444444444443 |

Missed reference IDs: none.
## Test1_Full.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test1_Full2.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 32.94736842105263 | 25.0 | 44.91512463583544 | 106.0 | 73.99999999999999 | 25.473684210526315 | 21.0 |
| end_frame | 13.0 | 9.0 | 18.202082009311027 | 46.0 | 29.599999999999987 | 8.052631578947368 | 6.0 |
| start_time_sec | 1.0982456140350922 | 0.8333333333333428 | 1.497170821194515 | 3.5333333333333314 | 2.4666666666666623 | 0.8491228070175483 | 0.700000000000017 |
| end_time_sec | 0.4333333333333414 | 0.29999999999998295 | 0.6067360669770386 | 1.5333333333333385 | 0.9866666666666727 | 0.26842105263157395 | 0.20000000000000284 |
| duration_sec | 1.0649122807017646 | 0.6666666666666856 | 1.3861259067053637 | 2.69999999999996 | 2.5866666666666673 | -0.5807017543859743 | -0.5000000000000284 |

## Test1_Full2.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.05263157894736842 | 0.05 |
| start | 3 | 0.1 | 2 | 0.10526315789473684 | 0.1 |
| start | 5 | 0.16666666666666666 | 5 | 0.2631578947368421 | 0.25 |
| start | 10 | 0.3333333333333333 | 6 | 0.3157894736842105 | 0.3 |
| start | 15 | 0.5 | 6 | 0.3157894736842105 | 0.3 |
| start | 30 | 1.0 | 13 | 0.6842105263157895 | 0.65 |
| end | 1 | 0.03333333333333333 | 3 | 0.15789473684210525 | 0.15 |
| end | 3 | 0.1 | 4 | 0.21052631578947367 | 0.2 |
| end | 5 | 0.16666666666666666 | 5 | 0.2631578947368421 | 0.25 |
| end | 10 | 0.3333333333333333 | 11 | 0.5789473684210527 | 0.55 |
| end | 15 | 0.5 | 14 | 0.7368421052631579 | 0.7 |
| end | 30 | 1.0 | 17 | 0.8947368421052632 | 0.85 |

## Test1_Full2.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8468352271418205 |
| median_iou | 0.9047619047619031 |
| minimum_iou | 0.5260416666666674 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 78.94736842105263 |
| percent IoU strictly above 0.9 | 52.63157894736842 |
| percent IoU strictly above 0.95 | 26.31578947368421 |

Missed reference IDs: 5.
## Test1_Full2.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 5 | 2308 | 2496 | Unscored partial-reference proposal; not FP |
| 21 | 10249 | 10538 | Unscored partial-reference proposal; not FP |
| 22 | 10605 | 10738 | Unscored partial-reference proposal; not FP |
| 23 | 10775 | 11085 | Unscored partial-reference proposal; not FP |
| 24 | 11274 | 11397 | Unscored partial-reference proposal; not FP |
| 25 | 11613 | 11867 | Unscored partial-reference proposal; not FP |
| 26 | 11982 | 12196 | Unscored partial-reference proposal; not FP |
| 27 | 12455 | 12954 | Unscored partial-reference proposal; not FP |
| 28 | 13115 | 13439 | Unscored partial-reference proposal; not FP |
| 29 | 13686 | 13982 | Unscored partial-reference proposal; not FP |
| 30 | 14222 | 14331 | Unscored partial-reference proposal; not FP |
| 31 | 14430 | 15171 | Unscored partial-reference proposal; not FP |
| 32 | 15354 | 15529 | Unscored partial-reference proposal; not FP |
| 33 | 15664 | 15951 | Unscored partial-reference proposal; not FP |
| 34 | 16000 | 16385 | Unscored partial-reference proposal; not FP |
| 35 | 16521 | 17031 | Unscored partial-reference proposal; not FP |
| 36 | 17074 | 17207 | Unscored partial-reference proposal; not FP |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics. Partial reference: precision/F1/FP unavailable; recall describes agreement only with supplied positive rows.

## Test1_Full_rally.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.25 | 20.5 | 41.17408839981228 | 106.0 | 69.5 | 24.194444444444443 | 14.0 |
| end_frame | 10.472222222222221 | 6.0 | 14.648663192705788 | 44.0 | 22.5 | -2.1944444444444446 | -2.5 |
| start_time_sec | 0.9416666666666749 | 0.6833333333333362 | 1.372469613327078 | 3.5333333333333314 | 2.3166666666666735 | 0.8064814814814899 | 0.4666666666667183 |
| end_time_sec | 0.3490740740740812 | 0.20000000000002416 | 0.48828877309019647 | 1.4666666666666686 | 0.7500000000000284 | -0.073148148148151 | -0.08333333333337123 |
| duration_sec | 1.111111111111119 | 0.6333333333333302 | 1.527969684916783 | 4.0 | 2.7000000000000064 | -0.8796296296296409 | -0.5666666666666629 |

## Test1_Full_rally.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.027777777777777776 | 0.027777777777777776 |
| start | 3 | 0.1 | 6 | 0.16666666666666666 | 0.16666666666666666 |
| start | 5 | 0.16666666666666666 | 12 | 0.3333333333333333 | 0.3333333333333333 |
| start | 10 | 0.3333333333333333 | 17 | 0.4722222222222222 | 0.4722222222222222 |
| start | 15 | 0.5 | 17 | 0.4722222222222222 | 0.4722222222222222 |
| start | 30 | 1.0 | 25 | 0.6944444444444444 | 0.6944444444444444 |
| end | 1 | 0.03333333333333333 | 4 | 0.1111111111111111 | 0.1111111111111111 |
| end | 3 | 0.1 | 9 | 0.25 | 0.25 |
| end | 5 | 0.16666666666666666 | 17 | 0.4722222222222222 | 0.4722222222222222 |
| end | 10 | 0.3333333333333333 | 23 | 0.6388888888888888 | 0.6388888888888888 |
| end | 15 | 0.5 | 26 | 0.7222222222222222 | 0.7222222222222222 |
| end | 30 | 1.0 | 34 | 0.9444444444444444 | 0.9444444444444444 |

## Test1_Full_rally.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8710256650394885 |
| median_iou | 0.9192570644833666 |
| minimum_iou | 0.5380710659898521 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 83.33333333333333 |
| percent IoU strictly above 0.9 | 55.55555555555556 |
| percent IoU strictly above 0.95 | 27.77777777777778 |

Missed reference IDs: none.
## Test1_Full_rally.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test1_Full_rev_T.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 26.794117647058822 | 20.5 | 38.867421712640464 | 106.0 | 68.0 | 22.5 | 14.0 |
| end_frame | 11.647058823529411 | 7.5 | 16.65744843111616 | 46.0 | 25.099999999999998 | 7.529411764705882 | 5.5 |
| start_time_sec | 0.89313725490197 | 0.6833333333333362 | 1.2955807237546846 | 3.5333333333333314 | 2.2666666666666755 | 0.7500000000000094 | 0.4666666666667183 |
| end_time_sec | 0.38823529411765584 | 0.2500000000000071 | 0.5552482810372057 | 1.5333333333333385 | 0.8366666666666673 | 0.25098039215686174 | 0.18333333333337265 |
| duration_sec | 0.9107843137254996 | 0.5833333333333188 | 1.2366806721895975 | 2.69999999999996 | 2.1233333333333406 | -0.49901960784314753 | -0.28333333333334565 |

## Test1_Full_rev_T.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.029411764705882353 | 0.02857142857142857 |
| start | 3 | 0.1 | 6 | 0.17647058823529413 | 0.17142857142857143 |
| start | 5 | 0.16666666666666666 | 12 | 0.35294117647058826 | 0.34285714285714286 |
| start | 10 | 0.3333333333333333 | 16 | 0.47058823529411764 | 0.45714285714285713 |
| start | 15 | 0.5 | 16 | 0.47058823529411764 | 0.45714285714285713 |
| start | 30 | 1.0 | 24 | 0.7058823529411765 | 0.6857142857142857 |
| end | 1 | 0.03333333333333333 | 3 | 0.08823529411764706 | 0.08571428571428572 |
| end | 3 | 0.1 | 8 | 0.23529411764705882 | 0.22857142857142856 |
| end | 5 | 0.16666666666666666 | 12 | 0.35294117647058826 | 0.34285714285714286 |
| end | 10 | 0.3333333333333333 | 22 | 0.6470588235294118 | 0.6285714285714286 |
| end | 15 | 0.5 | 26 | 0.7647058823529411 | 0.7428571428571429 |
| end | 30 | 1.0 | 31 | 0.9117647058823529 | 0.8857142857142857 |

## Test1_Full_rev_T.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8678779703223529 |
| median_iou | 0.9192570644833666 |
| minimum_iou | 0.5260416666666674 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 85.29411764705883 |
| percent IoU strictly above 0.9 | 55.88235294117647 |
| percent IoU strictly above 0.95 | 29.41176470588235 |

Missed reference IDs: 5.
## Test1_Full_rev_T.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|
| 5 | 2308 | 2496 | FP under complete reference |
| 36 | 17074 | 17207 | FP under complete reference |

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Test1_Full_rev_T4.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.25 | 20.5 | 41.17408839981228 | 106.0 | 69.5 | 24.194444444444443 | 14.0 |
| end_frame | 10.472222222222221 | 6.0 | 14.648663192705788 | 44.0 | 22.5 | -2.1944444444444446 | -2.5 |
| start_time_sec | 0.9416666666666749 | 0.6833333333333362 | 1.372469613327078 | 3.5333333333333314 | 2.3166666666666735 | 0.8064814814814899 | 0.4666666666667183 |
| end_time_sec | 0.3490740740740812 | 0.20000000000002416 | 0.48828877309019647 | 1.4666666666666686 | 0.7500000000000284 | -0.073148148148151 | -0.08333333333337123 |
| duration_sec | 1.111111111111119 | 0.6333333333333302 | 1.527969684916783 | 4.0 | 2.7000000000000064 | -0.8796296296296409 | -0.5666666666666629 |

## Test1_Full_rev_T4.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.027777777777777776 | 0.02631578947368421 |
| start | 3 | 0.1 | 6 | 0.16666666666666666 | 0.15789473684210525 |
| start | 5 | 0.16666666666666666 | 12 | 0.3333333333333333 | 0.3157894736842105 |
| start | 10 | 0.3333333333333333 | 17 | 0.4722222222222222 | 0.4473684210526316 |
| start | 15 | 0.5 | 17 | 0.4722222222222222 | 0.4473684210526316 |
| start | 30 | 1.0 | 25 | 0.6944444444444444 | 0.6578947368421053 |
| end | 1 | 0.03333333333333333 | 4 | 0.1111111111111111 | 0.10526315789473684 |
| end | 3 | 0.1 | 9 | 0.25 | 0.23684210526315788 |
| end | 5 | 0.16666666666666666 | 17 | 0.4722222222222222 | 0.4473684210526316 |
| end | 10 | 0.3333333333333333 | 23 | 0.6388888888888888 | 0.6052631578947368 |
| end | 15 | 0.5 | 26 | 0.7222222222222222 | 0.6842105263157895 |
| end | 30 | 1.0 | 34 | 0.9444444444444444 | 0.8947368421052632 |

## Test1_Full_rev_T4.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8710256650394885 |
| median_iou | 0.9192570644833666 |
| minimum_iou | 0.5380710659898521 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 83.33333333333333 |
| percent IoU strictly above 0.9 | 55.55555555555556 |
| percent IoU strictly above 0.95 | 27.77777777777778 |

Missed reference IDs: 2, 8.
## Test1_Full_rev_T4.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## win_predictions.csv boundary and duration errors

| Quantity | MAE | Median abs | RMSE | Max abs | P90 abs | Mean signed | Median signed |
|---|---|---|---|---|---|---|---|
| start_frame | 28.25 | 20.5 | 41.17408839981228 | 106.0 | 69.5 | 24.194444444444443 | 14.0 |
| end_frame | 10.472222222222221 | 6.0 | 14.648663192705788 | 44.0 | 22.5 | -2.1944444444444446 | -2.5 |
| start_time_sec | 0.9416666666666749 | 0.6833333333333362 | 1.372469613327078 | 3.5333333333333314 | 2.3166666666666735 | 0.8064814814814899 | 0.4666666666667183 |
| end_time_sec | 0.3490740740740812 | 0.20000000000002416 | 0.48828877309019647 | 1.4666666666666686 | 0.7500000000000284 | -0.073148148148151 | -0.08333333333337123 |
| duration_sec | 1.111111111111119 | 0.6333333333333302 | 1.527969684916783 | 4.0 | 2.7000000000000064 | -0.8796296296296409 | -0.5666666666666629 |

## win_predictions.csv boundary tolerances

| Boundary | Frames | Seconds | Within | Matched fraction | All-GT fraction |
|---|---|---|---|---|---|
| start | 1 | 0.03333333333333333 | 1 | 0.027777777777777776 | 0.027777777777777776 |
| start | 3 | 0.1 | 6 | 0.16666666666666666 | 0.16666666666666666 |
| start | 5 | 0.16666666666666666 | 12 | 0.3333333333333333 | 0.3333333333333333 |
| start | 10 | 0.3333333333333333 | 17 | 0.4722222222222222 | 0.4722222222222222 |
| start | 15 | 0.5 | 17 | 0.4722222222222222 | 0.4722222222222222 |
| start | 30 | 1.0 | 25 | 0.6944444444444444 | 0.6944444444444444 |
| end | 1 | 0.03333333333333333 | 4 | 0.1111111111111111 | 0.1111111111111111 |
| end | 3 | 0.1 | 9 | 0.25 | 0.25 |
| end | 5 | 0.16666666666666666 | 17 | 0.4722222222222222 | 0.4722222222222222 |
| end | 10 | 0.3333333333333333 | 23 | 0.6388888888888888 | 0.6388888888888888 |
| end | 15 | 0.5 | 26 | 0.7222222222222222 | 0.7222222222222222 |
| end | 30 | 1.0 | 34 | 0.9444444444444444 | 0.9444444444444444 |

## win_predictions.csv overlap

| Measure | Value |
|---|---|
| mean_iou | 0.8710256650394885 |
| median_iou | 0.9192570644833666 |
| minimum_iou | 0.5380710659898521 |
| percent IoU strictly above 0.5 | 100.0 |
| percent IoU strictly above 0.75 | 83.33333333333333 |
| percent IoU strictly above 0.9 | 55.55555555555556 |
| percent IoU strictly above 0.95 | 27.77777777777778 |

Missed reference IDs: none.
## win_predictions.csv extra or unscored predictions

| Prediction ID | Start frame | End frame | Interpretation |
|---|---|---|---|

Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.

## Annotation coverage

| File | Declared role | Purpose | Ambiguity |
|---|---|---|---|
| Test1_Full.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full2.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_ball_filled.csv | dense_generated_shuttle | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_court.json | manual_court | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_rally.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_rev_T.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| Test1_Full_rev_T4.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| player_detections.csv | dense_generated_players | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |
| win_predictions.csv | interval_reference | Previously reviewed Test1 reference control; original annotations unchanged | Generated/legacy candidate, no independent contact/identity/outcome ground truth |

## Generated point disagreement

| Reference | Population | Bound | Count | Mean px | Median px | Min px | Max px | P90 px | P95 px |
|---|---|---|---|---|---|---|---|---|---|
| Test1_Full_ball_filled.csv | all current | True | 11853 | 7.459979560329491 | 1.4785138511368239 | 0.028962643394979764 | 561.7686982419276 | 2.6547696931020446 | 3.3336566742250384 |
| Test1_Full_ball_filled.csv | fresh detector | True | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| player_detections.csv | all current | True | 33466 | 3.069777164116277 | 1.5077146267190589 | 0.013598654728157834 | 70.43559424620481 | 7.51108890594865 | 10.645644688104078 |
| player_detections.csv | fresh detector | True | 13966 | 1.456916422808158 | 1.0257089152434755 | 0.013598654728157834 | 68.93718454085308 | 2.608834957186396 | 3.940757460234197 |

## Point coverage and data quality

| Reference | Count meaning | Count |
|---|---|---|
| Test1_Full_ball_filled.csv | reference_visible=False,current_raw_present=False | 3071 |
| Test1_Full_ball_filled.csv | visibility_unknown | 0 |
| Test1_Full_ball_filled.csv | visible_invalid_numeric | 0 |
| Test1_Full_ball_filled.csv | out_of_image_reference_points | 0 |
| Test1_Full_ball_filled.csv | reference_visible=True,current_raw_present=False | 2161 |
| Test1_Full_ball_filled.csv | reference_visible=False,current_raw_present=True | 183 |
| Test1_Full_ball_filled.csv | reference_visible=True,current_raw_present=True | 11853 |
| player_detections.csv | reference_points | 33768 |
| player_detections.csv | out_of_image_reference_points | 0 |
| player_detections.csv | current_points | 33716 |
| player_detections.csv | all_current_unmatched_reference | 302 |
| player_detections.csv | all_current_unmatched_current | 250 |
| player_detections.csv | fresh_detector_unmatched_reference | 19802 |
| player_detections.csv | fresh_detector_unmatched_current | 125 |
| player_detections.csv | missing_or_invalid_slot_coordinates | 768 |

## Byte-identical dense-reference aliases

| Duplicate | Evaluated primary |
|---|---|

## Single-frame court candidates

| File | Frame | Bound | Mean corner px | Max corner px | Limit |
|---|---|---|---|---|---|
| Test1_Full_court.json | 8634 | True | 1.7975722890811696 | 3.529581642118429 | single-frame manual candidate; not all-frame accuracy |

## Raw component coverage

| Quantity | Count |
|---|---|
| frames | 17268 |
| raw_shuttle_present | 12036 |
| detector_executed_frames | 7091 |
| person_rows | 33716 |
| scene_telemetry_present | 3610 |
| scene_raw_hypotheses | 13 |
| actual_content_epoch_increments | 13 |
| content_epoch_decreases | 0 |
| detailed_diagnostic_frames | 3600 |
| person_current_detector_matches | 14091 |
| person_propagated_or_unmatched | 19625 |
| pose_present_rows | 26752 |
| pose_current_source_rows | 26752 |
| pose_present_without_current_source | 0 |
| pose_current_on_propagated_box | 12661 |
| racket_present_rows | 11385 |
| racket_current_source_rows | 11385 |
| racket_present_without_current_source | 0 |
| racket_current_on_propagated_box | 0 |
| scene_decision_records | 13 |
| scene_positive_correspondence_vetoes | 0 |
| scene_current_detector_probes | 13 |

## Track coverage

| Quantity | Count |
|---|---|
| camera_rows | 17268 |
| player_rows | 33702 |
| nonfinite_projected_court_rows | 0 |
| player_projected_court_rows | 33045 |
| projected_court_on_propagated_box | 19281 |
| racket_rows | 11376 |
| shuttle_rows | 17268 |

## Live event counts

| Quantity | Count |
|---|---|
| calibration | 1 |
| activity_interval | 122 |
| scene | 17 |
| participant_observation | 123 |
| format_decision | 1 |
| rally_start | 36 |
| stroke | 446 |
| contact | 446 |
| rally_end | 36 |
| shuttle_turn | 41 |
| identity_ambiguity | 50 |
| broadcast_score | 473 |
| match_phase | 1 |
| highlight | 3 |

## Outcome and score coverage

| Quantity | Value |
|---|---|
| predicted_rallies | 36 |
| known_winner_outputs | 0 |
| unknown_winner_outputs | 36 |
| canonical_point_events | 0 |
| broadcast_score_observation_events | 473 |
| accuracy_status | unavailable_without_independent_identity_event_outcome_score_labels |

## Predicted stroke counts

| Predicted class | Count |
|---|---|
| unknown | 309 |
| push | 47 |
| lift | 27 |
| drive | 2 |
| net_shot | 30 |
| drop | 21 |
| clear | 8 |
| smash | 2 |

## Actual runtime and resources

| Quantity | Measured value |
|---|---|
| original_parent_status | completed |
| worker_exit_code | 0 |
| physical_gpu_index | 1 |
| allocated_gpu_uuid | GPU-a618f090-66bf-ad80-b0a5-0c91bee61fab |
| worker_pid | 3713778 |
| parent_failure_inclusive_elapsed_s | unavailable |
| parent_failure_inclusive_source_fps | unavailable |
| neural_only_throughput_fps | unavailable |
| model_loading_time_s | unavailable |
| media_ready_time_s | 1.9531396771781147 |
| model_staging_time_s | 1.7218959531746805 |
| worker_final_cpu_s | 20979.958542 |
| worker_maxrss_bytes | 2841280512 |
| sampled_worker_tree_peak_rss_bytes | 2847993856 |
| sampled_worker_gpu_peak_mib | 2124 |
| sampled_cpu_seconds_max_observed | 20979.89 |
| sampled_cpu_seconds_last_observed | 20979.89 |
| sampled_system_available_ram_min_bytes | 107879612416 |
| sample_count | 849 |
| resource_rows | 849 |
| sampling_error_count | 0 |
| parent_completed_elapsed_s | 1757.9354004859924 |
| parent_completed_source_fps | 9.822886549315834 |
| worker_elapsed_s | 1750.7910022903234 |
| worker_source_fps | 9.86297049585622 |
| component_initialization_including_models_s | 8.783029728103429 |

## Stage invocation timing (scopes can overlap)

| Stage | Calls | Seconds | P50 ms | P95 ms |
|---|---|---|---|---|
| court | 288 | 97.00811115140095 | 306.3772339373827 | 600.6470515858375 |
| content_continuity_and_players | 288 | 779.635243398603 | 3084.4872179441154 | 3324.3302265647794 |
| shuttle | 288 | 254.9297770988196 | 868.7680105213076 | 1035.7128290692344 |
| players | 288 | 70.28981927037239 | 224.15028139948845 | 524.0213180193676 |
| ocr | 288 | 238.65013947989792 | 811.7475498002023 | 1005.8855943381784 |

## Verified actual model artifacts

| Group | Model | SHA256 | Status |
|---|---|---|---|
| registry_artifacts | osnet_ain_x0_25 | unavailable | unavailable_not_claimed_loaded |
| registry_artifacts | racketvision_balltrack | unavailable | unavailable_not_claimed_loaded |
| registry_artifacts | rfdetr_small | fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e | verified |
| registry_artifacts | rtmpose_m_body7 | f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741 | verified |
| registry_artifacts | tracknetv3 | df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a | verified |
| package_ocr_artifacts | det | 090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f | verified |
| package_ocr_artifacts | cls | e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c | verified |
| package_ocr_artifacts | rec | 6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884 | verified |

## Actual worker backend declarations

| Stage | Requested | Actual | Device | Dtype | Fallback |
|---|---|---|---|---|---|
| shuttle | torch-cuda | torch-cuda | cuda:0 | torch.float16 | False |
| shuttle_association | unavailable | numpy-cpu | unavailable | unavailable | unavailable |
| content_continuity | unavailable | opencv-cpu | unavailable | unavailable | unavailable |
| player_detector | onnx-cuda | onnx-cuda | unavailable | unavailable | False |
| pose | onnx-cuda | onnx-cuda | unavailable | unavailable | False |
| ocr | onnx-cpu | unavailable | unavailable | unavailable | False |
| racket | opencv-cpu | opencv-cpu | unavailable | unavailable | False |

## Source and coordinate provenance

| Quantity | Value |
|---|---|
| Source SHA256 | 877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6 |
| Native guard root | /home/administrator/Desktop/sport-analytics/Sports_Analytics |
| Recorded pipeline commit | caa91761948d09f2cfe4937b0db743fff8643a12 |
| Coordinate review | diagnostic_coordinate_binding_declared |

## Unavailable physical accuracy

| Metric family | Value | Prerequisite |
|---|---|---|
| player_AP_mAP_IoU | unavailable | Independently reviewed boxes and complete positive/negative coverage; supplied generated points are not boxes. |
| tracking_IDF1_HOTA_ID_switches_fragmentation | unavailable | Reviewed persistent athlete identities, boxes and visibility; two generated detection slots are not persistent IDs. |
| pose_PCK_OKS | unavailable | Reviewed keypoints and joint visibility, skeleton convention and scale. |
| shuttle_physical_localization_PR | unavailable | Independent reviewed coordinates/visibility; filled model estimates do not identify interpolated frames. |
| racket_contact_PR_F1_temporal_error | unavailable | Reviewed contact/racket times and negative windows, not rally-level labels. |
| stroke_per_class_PR_F1_confusion | unavailable | Complete per-contact stroke taxonomy and labels; a single ball_types field per coarse rally is insufficient. |
| winner_outcome_accuracy_PR_F1_confusion | unavailable | Verified symbolic Player A/B identity and source-bound adjudicated outcomes; win_predictions is generated. |
| score_sequence_accuracy | unavailable | Reviewed broadcast identity, point alignment and score sequence, accounting for edited-video omissions. |
| highlight_quality | unavailable | Reviewed highlight relevance/boundaries; rally overlap and execution are not relevance accuracy. |
| player_analytics_accuracy | unavailable | Reviewed participant identities and metric-specific physical movement/event labels. |

Full per-reference rows, original fields/eligibility and semantic field counts: [reference_raw_details.json](reference_raw_details.json). All scalar metrics and complete actual Worker/profile/backend/source provenance: [component_reference_metrics.json](component_reference_metrics.json). Detailed OCR/scene/events/tracks/resources: [component_raw_details.json](component_raw_details.json). Synchronized points are separate point_reference_XX.jsonl files.

Execution, coverage and generated-reference agreement do not validate physical accuracy. Unavailable values remain null, not zero. Raw arrays are preserved outside this summary.
