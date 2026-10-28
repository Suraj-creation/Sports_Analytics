# Part2 annotations and Test7 video review

This note records a limited visual inspection, not human-reviewed exhaustive shot ground truth or a measured model accuracy result. Existing annotation files were not changed.

## Source and method

The public Drive `Test7_Full.mp4` was downloaded to the server's ignored `data/task2-review/` directory. It is 664,899,136 bytes; SHA-256 `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`. `ffprobe` reports H.264, 1920×1080, 30 fps, 10,725 video frames and 357.5 s duration. This recording shows broadcast singles, not representative amateur doubles. We decoded frames in presentation order with OpenCV, sampled every 15 frames over the first 40 s, and every 5 frames over frames 385–460 (12.833–15.333 s). This sampling is insufficient to establish every racket contact, shuttle landing or shot family.

## Opening rally and conflicting winner labels

- The opening video identifies the far player as Tai Tzu-ying and the near player as Carolina Marín. The physical arena scoreboard at frame 0 shows 0–0. A jersey close-up at frame 495 (16.5 s) identifies Marín; the broadcast scoreboard at frame 510 (17.0 s) reads Tai 0, Marín 1. No intervening cut is visible in the sampled frames of the opening rally before a brief post-rally close-up; short cuts between samples cannot be ruled out. This supports Marín as winner of the opening rally.
- The first rally in `Part2/dataset/Test7_Full/Test7_Full.csv` is listed at 6–15 s with winner `Player A` and score A:B 0:1. The local legacy reference `legacy/pipeline/vjepa_setup/dataset/labels/Test7_Full.csv` lists the same span and score with winner `Player B`.
- Sampled frames show the rally ending around 13.7–14.2 s. The footage reviewed did not establish the exact landing or fault with enough confidence, and the A/B-to-athlete mapping is undocumented. The physical winner is supported as Marín by the score change, but the A/B winner-label conflict remains **unresolved**; the scoreboard alone does not determine which file's `Player A`/`Player B` convention is correct. Do not overwrite or silently combine the versions.

## Edited timeline

The broadcast scoreboard reads Tai 0 / Marín 1 at frames 510 and 900 (17.0 and 30.0 s) and Tai 2 / Marín 5 by frame 1005 (33.5 s), across a visible cut. The change is incompatible with a continuous sequence of scored rallies in that interval. Consequently, treat this as an edited recording and do not assume the CSV's consecutive-row scores represent every point in the original match. Score jumps do not themselves prove a particular winner label wrong.

## Annotation coverage and limitations

The local Part2 dataset contains eight match directories: Test1, Test2, Test3, Test4, Test6, Test7, Test9 and Test10. Their primary match CSVs contain 440 rows including 15 blank rows. Each nonblank row supplies a rally time span and fields such as winner, reason, score and one `ball_types` value; these are not exhaustive per-shot contact timestamps, per-shot hitter identities or four-player labels. Labels contain variations mixed with shot families and at least one outcome-like value in `ball_types`; retain raw values until a reviewed taxonomy is applied. The supplied trajectory, player-detection, rally and win-prediction CSVs include generated outputs and do not automatically become human-reviewed truth.

For exact matching start/end strings, Part2 versus the local legacy reference contains 6 winner disagreements among 32 matched Test1 spans, 8 among 21 Test3 spans, 1 among 40 Test6 spans and 1 among 31 Test7 spans. These comparisons locate review cases; they do not determine which version is correct, and do not include intervals with changed timestamps. Record reviewer decisions and evidence in a separate versioned annotation artifact after reviewing corresponding footage; preserve both source versions. Use recording-separated evaluation and do not treat these labels as a contact-level shot benchmark without further annotation.
