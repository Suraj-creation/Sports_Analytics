
import pandas as pd
import numpy as np

# =========================
# FILE PATHS - ADJUST AS NEEDEDr
# =========================
DETECTED_CSV = "analysis/Test1_Full_rev_T.csv"  # Your detected rallies
GROUND_TRUTH_CSV = "analysis/Test1_Full_rev_GT.csv"  # Your ground truth

# GT annotations are whole-second rounded; allow ±0.5s tolerance at b

GT_TOLERANCE_SEC = 0.5


# =========================
# TIME CONVERSION UTIL
# =========================
def time_to_sec(t):
    """Convert a time value to seconds.
    Accepts numeric types or strings in MM:SS or H:MM:SS form.
    """
    if isinstance(t, str):
        # split on colon and compute total seconds
        parts = t.split(":")
        parts = [float(p) for p in parts]

        if len(parts) == 2:
            m, s = parts
            return m * 60 + s

        elif len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s

        else:
            # fallback to float conversion
            return float(t)

    return float(t)


# =========================
# LOAD DATA
# =========================
print("Loading data...")

detected_df = pd.read_csv(DETECTED_CSV)
gt_df = pd.read_csv(GROUND_TRUTH_CSV)

# convert time columns to seconds (create new numeric columns)
detected_df["start_sec"] = detected_df["Start_Time"].apply(time_to_sec)
detected_df["end_sec"] = detected_df["End_Time"].apply(time_to_sec)

gt_df["start_sec"] = gt_df["Start (sec)"].apply(time_to_sec)
gt_df["end_sec"] = gt_df["End (sec)"].apply(time_to_sec)

# Extract start and end times in seconds
detected_rallies = list(
    zip(
        detected_df["start_sec"].values,
        detected_df["end_sec"].values
    )
)

ground_truth = list(
    zip(
        gt_df["start_sec"].values,
        gt_df["end_sec"].values
    )
)

print(f"Detected Rallies: {len(detected_rallies)}")
print(f"Ground Truth Rallies: {len(ground_truth)}")


# =========================
# IOU CALCULATION
# =========================
def calculate_iou(pred_start, pred_end, gt_start, gt_end):
    """
    Calculate Intersection over Union (IOU) for temporal segments
    """

    # Calculate intersection
    intersection_start = max(pred_start, gt_start)
    intersection_end = min(pred_end, gt_end)
    intersection = max(0, intersection_end - intersection_start)

    # Calculate union
    union_start = min(pred_start, gt_start)
    union_end = max(pred_end, gt_end)
    union = union_end - union_start

    # Calculate IOU
    iou = intersection / union if union > 0 else 0

    return iou, intersection, union


# =========================
# METRICS CALCULATION
# =========================
def calculate_metrics(
    detected_rallies,
    ground_truth_rallies,
    iou_threshold=0.5
):
    """
    Calculate precision, recall, and F1 score based on IOU matching.
    Uses greedy best-match approach: each detection matches to its best GT.
    """

    matched_gt = set()
    matched_pred = set()
    iou_scores = []

    for i, (pred_start, pred_end) in enumerate(detected_rallies):

        best_iou = 0
        best_gt_idx = -1

        for j, (gt_start, gt_end) in enumerate(ground_truth_rallies):

            iou, _, _ = calculate_iou(
                pred_start,
                pred_end,
                gt_start - GT_TOLERANCE_SEC,
                gt_end + GT_TOLERANCE_SEC
            )

            if iou > best_iou:
                best_iou = iou
                best_gt_idx = j

        if best_iou >= iou_threshold:
            matched_pred.add(i)
            matched_gt.add(best_gt_idx)
            iou_scores.append(best_iou)

    # Calculate metrics
    true_positives = len(matched_pred)
    false_positives = len(detected_rallies) - true_positives
    false_negatives = len(ground_truth_rallies) - len(matched_gt)

    precision = (
        true_positives / len(detected_rallies)
        if len(detected_rallies) > 0 else 0
    )

    recall = (
        true_positives / len(ground_truth_rallies)
        if len(ground_truth_rallies) > 0 else 0
    )

    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0 else 0
    )

    mean_iou = np.mean(iou_scores) if iou_scores else 0

    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'mean_iou': mean_iou,
        'matched_gt': matched_gt,
        'matched_pred': matched_pred,
        'iou_scores': iou_scores
    }


# =========================
# PRINT DETECTED RALLIES
# =========================
print("\n" + "=" * 80)
print("DETECTED RALLIES")
print("=" * 80)

for i, (start, end) in enumerate(detected_rallies):

    duration = end - start

    print(
        f"Detected Rally {i+1:2d}: "
        f"{start:7.2f}s - {end:7.2f}s "
        f"(Duration: {duration:6.2f}s)"
    )


# =========================
# PRINT GROUND TRUTH RALLIES
# =========================
print("\n" + "=" * 80)
print("GROUND TRUTH RALLIES")
print("=" * 80)

for i, (start, end) in enumerate(ground_truth):

    duration = end - start

    print(
        f"GT Rally {i+1:2d}: "
        f"{start:7.2f}s - {end:7.2f}s "
        f"(Duration: {duration:6.2f}s)"
    )


# =========================
# IOU MATRIX
# =========================
print("\n" + "=" * 80)
print(
    f"IOU MATRIX "
    f"(Detected vs Ground Truth, "
    f"GT ±{GT_TOLERANCE_SEC}s tolerance)"
)
print("=" * 80)

# Print header
print(f"{'':20}", end="")

for j in range(len(ground_truth)):
    print(f"GT_{j+1:2d}     ", end="")

print()

# Print matrix
iou_matrix = []

for i, (pred_start, pred_end) in enumerate(detected_rallies):

    print(f"Detected_{i+1:2d}        ", end="")

    row = []

    for j, (gt_start, gt_end) in enumerate(ground_truth):

        iou, _, _ = calculate_iou(
            pred_start,
            pred_end,
            gt_start - GT_TOLERANCE_SEC,
            gt_end + GT_TOLERANCE_SEC
        )

        row.append(iou)

        print(f"{iou:6.4f}  ", end="")

    print()

    iou_matrix.append(row)


# =========================
# METRICS AT DIFFERENT THRESHOLDS
# =========================
print("\n" + "=" * 80)
print("METRICS AT DIFFERENT IOU THRESHOLDS")
print("=" * 80)

thresholds = [0.3, 0.5, 0.7]

metrics_summary = []

for threshold in thresholds:

    metrics = calculate_metrics(
        detected_rallies,
        ground_truth,
        iou_threshold=threshold
    )

    metrics_summary.append({
        'iou_threshold': threshold,
        'true_positives': metrics['true_positives'],
        'false_positives': metrics['false_positives'],
        'false_negatives': metrics['false_negatives'],
        'precision': round(metrics['precision'], 4),
        'recall': round(metrics['recall'], 4),
        'f1_score': round(metrics['f1_score'], 4),
        'mean_iou': round(metrics['mean_iou'], 4)
    })

    print(f"\n--- IOU Threshold: {threshold} ---")
    print(
        f"TP: {metrics['true_positives']}, "
        f"FP: {metrics['false_positives']}, "
        f"FN: {metrics['false_negatives']}"
    )

    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1_score']:.4f}")
    print(f"Mean IoU:  {metrics['mean_iou']:.4f}")


# =========================
# SAVE METRICS SUMMARY
# =========================
metrics_df = pd.DataFrame(metrics_summary)

metrics_summary_path = "analysis/rally_metrics_summary.csv"

metrics_df.to_csv(metrics_summary_path, index=False)

print(f"\n✓ Metrics summary saved to: {metrics_summary_path}")


# =========================
# DETAILED IOU RESULTS
# =========================
iou_results = {
    'detected_rally': [],
    'detected_start_sec': [],
    'detected_end_sec': [],
    'detected_duration_sec': [],
    'best_match_gt': [],
    'gt_start_sec': [],
    'gt_end_sec': [],
    'gt_duration_sec': [],
    'iou_score': []
}

for i, (pred_start, pred_end) in enumerate(detected_rallies):

    best_iou = 0
    best_gt_idx = -1

    for j, (gt_start, gt_end) in enumerate(ground_truth):

        iou, _, _ = calculate_iou(
            pred_start,
            pred_end,
            gt_start - GT_TOLERANCE_SEC,
            gt_end + GT_TOLERANCE_SEC
        )

        if iou > best_iou:
            best_iou = iou
            best_gt_idx = j

    iou_results['detected_rally'].append(i + 1)

    iou_results['detected_start_sec'].append(round(pred_start, 2))
    iou_results['detected_end_sec'].append(round(pred_end, 2))

    iou_results['detected_duration_sec'].append(
        round(pred_end - pred_start, 2)
    )

    if best_gt_idx >= 0:

        gt_start, gt_end = ground_truth[best_gt_idx]

        iou_results['best_match_gt'].append(best_gt_idx + 1)

        iou_results['gt_start_sec'].append(round(gt_start, 2))
        iou_results['gt_end_sec'].append(round(gt_end, 2))

        iou_results['gt_duration_sec'].append(
            round(gt_end - gt_start, 2)
        )

    else:

        iou_results['best_match_gt'].append(None)
        iou_results['gt_start_sec'].append(None)
        iou_results['gt_end_sec'].append(None)
        iou_results['gt_duration_sec'].append(None)

    iou_results['iou_score'].append(round(best_iou, 4))

iou_df = pd.DataFrame(iou_results)

iou_csv_path = "analysis/rally_iou_detailed_matches.csv"

iou_df.to_csv(iou_csv_path, index=False)

print(f"✓ Detailed IOU matches saved to: {iou_csv_path}")


# =========================
# CREATE REVIEW / EVALUATION CSV
# =========================
status_list = []
reason_list = []
matched_gts = set()

LABEL_IOU_THRESHOLD = 0.5

for i, row in iou_df.iterrows():

    iou = row['iou_score']
    gt_idx = row['best_match_gt']

    if pd.notna(gt_idx) and iou >= LABEL_IOU_THRESHOLD:

        status_list.append("TP")
        reason_list.append("Valid Match (IoU >= 0.5)")

        matched_gts.add(int(gt_idx))

    else:

        status_list.append("FP")

        if iou == 0:

            reason_list.append(
                "FP - Spurious / Fake (No GT match)"
            )

        else:

            det_dur = row['detected_duration_sec']
            gt_dur = row['gt_duration_sec']

            if gt_dur > 0 and det_dur / gt_dur < 0.6:

                reason_list.append(
                    "FP - Rally Split (Detection too short)"
                )

            elif gt_dur > 0 and det_dur / gt_dur > 1.5:

                reason_list.append(
                    "FP - Rally Merge (Detection too long)"
                )

            else:

                reason_list.append(
                    "FP - Late Start / Early End (Timing off)"
                )

labeled_df = detected_df.copy()

labeled_df["Evaluation_Status"] = status_list
labeled_df["Detailed_Reason"] = reason_list
labeled_df["Matched_GT_Rally"] = iou_df['best_match_gt']
labeled_df["IoU_Score"] = iou_df['iou_score']


# =========================
# APPEND FALSE NEGATIVES
# =========================
fn_rows = []

for j, (gt_start, gt_end) in enumerate(ground_truth):

    gt_idx = j + 1

    if gt_idx not in matched_gts:

        fn_row = {
            col: "" for col in labeled_df.columns
        }

        # Calculate max IoU for this GT
        max_iou_for_gt = 0.0
        overlapping_detections = 0

        for pred_start, pred_end in detected_rallies:

            iou, inter, union = calculate_iou(
                pred_start,
                pred_end,
                gt_start - GT_TOLERANCE_SEC,
                gt_end + GT_TOLERANCE_SEC
            )

            if inter > 0:

                overlapping_detections += 1

                if iou > max_iou_for_gt:
                    max_iou_for_gt = iou

        if overlapping_detections >= 2:

            reason = (
                "FN - Rally Split Victim "
                "(Multiple fragments, none >= 0.5)"
            )

        elif overlapping_detections == 1:

            reason = (
                "FN - Timing Mismatch / Merged "
                "(Detected but IoU < 0.5)"
            )

        else:

            reason = "FN - Completely Missed by System"

        fn_row["Evaluation_Status"] = "FN"
        fn_row["Detailed_Reason"] = reason
        fn_row["Matched_GT_Rally"] = gt_idx

        fn_row["start_sec"] = gt_start
        fn_row["end_sec"] = gt_end

        fn_row["IoU_Score"] = round(max_iou_for_gt, 4)

        fn_row["Start_Time"] = (
            f"{int(gt_start // 60):02d}:"
            f"{gt_start % 60:05.2f}"
        )

        fn_row["End_Time"] = (
            f"{int(gt_end // 60):02d}:"
            f"{gt_end % 60:05.2f}"
        )

        fn_rows.append(fn_row)

if fn_rows:

    labeled_df = pd.concat(
        [labeled_df, pd.DataFrame(fn_rows)],
        ignore_index=True
    )


# =========================
# CLEAN TEMP COLUMNS
# =========================
if "start_sec" in labeled_df.columns:

    labeled_df = labeled_df.drop(
        columns=["start_sec", "end_sec"]
    )


# =========================
# REORDER COLUMNS
# =========================
front_cols = [
    "Evaluation_Status",
    "Detailed_Reason",
    "Matched_GT_Rally",
    "IoU_Score"
]

cols = front_cols + [
    c for c in labeled_df.columns
    if c not in front_cols
]

labeled_df = labeled_df[cols]


# =========================
# SAVE REVIEW CSV
# =========================
labeled_out_path = DETECTED_CSV.replace(
    ".csv",
    "_Evaluated.csv"
)

labeled_df.to_csv(labeled_out_path, index=False)

print(
    f"✓ Labeled Detected Rallies "
    f"(TP/FP/FN) saved to: {labeled_out_path}"
)


# =========================
# SUMMARY STATS
# =========================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"Total Detected Rallies:      {len(detected_rallies)}")
print(f"Total Ground Truth Rallies: {len(ground_truth)}")

print(
    f"Matched (IoU >= 0.5):      "
    f"{metrics_summary[1]['true_positives']}"
)

print(
    f"Unmatched Detections:      "
    f"{metrics_summary[1]['false_positives']}"
)

print(
    f"Missed Ground Truth:       "
    f"{metrics_summary[1]['false_negatives']}"
)

print("=" * 80)
