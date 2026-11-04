# Rally boundary metrics

Signed errors are prediction minus ground truth. Null means unavailable.

```json
{
  "status": "evaluated",
  "matching_policy": {
    "version": "rally-boundaries-v1",
    "minimum_iou": 0.5,
    "assignment": "maximum cardinality, then total IoU + 1e-9/(1 + boundary distance seconds)",
    "intervals": "[start timestamp, end timestamp); duration=end-start; no inclusive-frame addition",
    "tolerance_denominators": "matched pairs and all ground-truth rallies reported separately",
    "zero_denominators": "precision/recall/F1=0; unavailable conditional metrics=null"
  },
  "fps": 30.0,
  "detection": {
    "ground_truth_count": 36,
    "predicted_count": 49,
    "matched_count": 30,
    "true_positives": 30,
    "false_positives": 19,
    "false_negatives": 6,
    "precision": 0.6122448979591837,
    "recall": 0.8333333333333334,
    "f1": 0.7058823529411765
  },
  "boundary_and_duration_errors": {
    "start_frame": {
      "mae": 49.43333333333333,
      "median_absolute_error": 23.0,
      "rmse": 75.25312839565764,
      "max_absolute_error": 202.0,
      "p90_absolute_error": 117.60000000000008,
      "mean_signed_error": 48.03333333333333
    },
    "end_frame": {
      "mae": 40.4,
      "median_absolute_error": 7.0,
      "rmse": 96.46311903174878,
      "max_absolute_error": 442.0,
      "p90_absolute_error": 103.80000000000001,
      "mean_signed_error": -33.4
    },
    "start_time_sec": {
      "mae": 1.6477777777777882,
      "median_absolute_error": 0.7666666666666799,
      "rmse": 2.508437613188595,
      "max_absolute_error": 6.7333333333333485,
      "p90_absolute_error": 3.9200000000000186,
      "mean_signed_error": 1.6011111111111225
    },
    "end_time_sec": {
      "mae": 1.3466666666666711,
      "median_absolute_error": 0.23333333333333428,
      "rmse": 3.215437301058293,
      "max_absolute_error": 14.733333333333348,
      "p90_absolute_error": 3.4600000000000053,
      "mean_signed_error": -1.1133333333333368
    },
    "duration_sec": {
      "mae": 2.845555555555561,
      "median_absolute_error": 1.9333333333333371,
      "rmse": 4.34637780226248,
      "max_absolute_error": 15.800000000000011,
      "p90_absolute_error": 6.783333333333374,
      "mean_signed_error": -2.7144444444444593
    }
  },
  "overlap": {
    "mean_iou": 0.7633148904564976,
    "median_iou": 0.7679480019856078,
    "minimum_iou": 0.5040000000000002,
    "percent_strictly_exceeding": {
      "0.5": 100.0,
      "0.75": 50.0,
      "0.9": 36.666666666666664,
      "0.95": 6.666666666666667
    }
  },
  "boundary_tolerances": {
    "start": [
      {
        "frames": 1,
        "seconds": 0.03333333333333333,
        "within_count": 0,
        "matched_accuracy": 0.0,
        "all_gt_accuracy": 0.0
      },
      {
        "frames": 3,
        "seconds": 0.1,
        "within_count": 3,
        "matched_accuracy": 0.1,
        "all_gt_accuracy": 0.08333333333333333
      },
      {
        "frames": 5,
        "seconds": 0.16666666666666666,
        "within_count": 7,
        "matched_accuracy": 0.23333333333333334,
        "all_gt_accuracy": 0.19444444444444445
      },
      {
        "frames": 10,
        "seconds": 0.3333333333333333,
        "within_count": 12,
        "matched_accuracy": 0.4,
        "all_gt_accuracy": 0.3333333333333333
      },
      {
        "frames": 15,
        "seconds": 0.5,
        "within_count": 14,
        "matched_accuracy": 0.4666666666666667,
        "all_gt_accuracy": 0.3888888888888889
      },
      {
        "frames": 30,
        "seconds": 1.0,
        "within_count": 18,
        "matched_accuracy": 0.6,
        "all_gt_accuracy": 0.5
      }
    ],
    "end": [
      {
        "frames": 1,
        "seconds": 0.03333333333333333,
        "within_count": 4,
        "matched_accuracy": 0.13333333333333333,
        "all_gt_accuracy": 0.1111111111111111
      },
      {
        "frames": 3,
        "seconds": 0.1,
        "within_count": 8,
        "matched_accuracy": 0.26666666666666666,
        "all_gt_accuracy": 0.2222222222222222
      },
      {
        "frames": 5,
        "seconds": 0.16666666666666666,
        "within_count": 12,
        "matched_accuracy": 0.4,
        "all_gt_accuracy": 0.3333333333333333
      },
      {
        "frames": 10,
        "seconds": 0.3333333333333333,
        "within_count": 17,
        "matched_accuracy": 0.5666666666666667,
        "all_gt_accuracy": 0.4722222222222222
      },
      {
        "frames": 15,
        "seconds": 0.5,
        "within_count": 18,
        "matched_accuracy": 0.6,
        "all_gt_accuracy": 0.5
      },
      {
        "frames": 30,
        "seconds": 1.0,
        "within_count": 24,
        "matched_accuracy": 0.8,
        "all_gt_accuracy": 0.6666666666666666
      }
    ]
  },
  "missed_gt_rallies": [
    5,
    23,
    25,
    28,
    29,
    31
  ],
  "unmatched_predictions": [
    {
      "pred_rally": 2,
      "start_frame": 891,
      "end_frame": 1023,
      "start": 29.7,
      "end": 34.1
    },
    {
      "pred_rally": 5,
      "start_frame": 1585,
      "end_frame": 1654,
      "start": 52.833333333333336,
      "end": 55.13333333333333
    },
    {
      "pred_rally": 7,
      "start_frame": 2309,
      "end_frame": 2423,
      "start": 76.96666666666667,
      "end": 80.76666666666667
    },
    {
      "pred_rally": 21,
      "start_frame": 8110,
      "end_frame": 8266,
      "start": 270.3333333333333,
      "end": 275.53333333333336
    },
    {
      "pred_rally": 24,
      "start_frame": 9548,
      "end_frame": 9646,
      "start": 318.26666666666665,
      "end": 321.53333333333336
    },
    {
      "pred_rally": 25,
      "start_frame": 9685,
      "end_frame": 9947,
      "start": 322.8333333333333,
      "end": 331.56666666666666
    },
    {
      "pred_rally": 28,
      "start_frame": 10769,
      "end_frame": 10908,
      "start": 358.96666666666664,
      "end": 363.6
    },
    {
      "pred_rally": 29,
      "start_frame": 10949,
      "end_frame": 11085,
      "start": 364.96666666666664,
      "end": 369.5
    },
    {
      "pred_rally": 31,
      "start_frame": 11634,
      "end_frame": 11745,
      "start": 387.8,
      "end": 391.5
    },
    {
      "pred_rally": 32,
      "start_frame": 11801,
      "end_frame": 11867,
      "start": 393.3666666666667,
      "end": 395.56666666666666
    },
    {
      "pred_rally": 35,
      "start_frame": 12771,
      "end_frame": 12954,
      "start": 425.7,
      "end": 431.8
    },
    {
      "pred_rally": 36,
      "start_frame": 13176,
      "end_frame": 13252,
      "start": 439.2,
      "end": 441.73333333333335
    },
    {
      "pred_rally": 37,
      "start_frame": 13273,
      "end_frame": 13439,
      "start": 442.43333333333334,
      "end": 447.96666666666664
    },
    {
      "pred_rally": 38,
      "start_frame": 13686,
      "end_frame": 13843,
      "start": 456.2,
      "end": 461.43333333333334
    },
    {
      "pred_rally": 39,
      "start_frame": 13883,
      "end_frame": 13982,
      "start": 462.76666666666665,
      "end": 466.06666666666666
    },
    {
      "pred_rally": 41,
      "start_frame": 14491,
      "end_frame": 14646,
      "start": 483.03333333333336,
      "end": 488.2
    },
    {
      "pred_rally": 42,
      "start_frame": 14701,
      "end_frame": 14969,
      "start": 490.03333333333336,
      "end": 498.96666666666664
    },
    {
      "pred_rally": 43,
      "start_frame": 14994,
      "end_frame": 15171,
      "start": 499.8,
      "end": 505.7
    },
    {
      "pred_rally": 45,
      "start_frame": 15668,
      "end_frame": 15735,
      "start": 522.2666666666667,
      "end": 524.5
    }
  ],
  "conditional_metrics_note": "Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.",
  "no_matches_reason": null
}
```
