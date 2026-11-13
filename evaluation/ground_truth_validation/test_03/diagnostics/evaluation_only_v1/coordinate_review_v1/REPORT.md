# Test 3 original coordinate review

Source SHA: `d587569affa3b4fcabab0ea6b97ecd278af15675ce5cba36c79298bb6d0db5fa`. This is annotation/source diagnosis only; no running predictions were accessed. Original files were rehashed unchanged after extraction.

Ten original source frames were decoded at exact native PTS: 0, 6, 300, 1594, 4204, 4207, 4208, 6000, 8100 and 8403. The source is 1920×1080, 30 fps, 8,414 frames. Each source image was resized once to 1280×720 using INTER_AREA; annotation coordinates were drawn unchanged, with no fitted spatial or temporal correction. Source pixel, PTS, PNG, original CSV/JSON and video hashes are retained in [frame_metadata.json](frame_metadata.json).

The original CSV frame columns each span zero-origin frames 0–8413. The sampled player crosses fall at bottom/foot locations on near and far athletes. This supports the existing `bbox_bottom_center` diagnostic convention. Original boxes and their generator are unavailable: exact point construction and foot localization accuracy remain unverified. Slots are anonymous observations, with no stable named-player or team binding established.

At declared court frame 4207, TL/TR/BR/BL follow the inner singles sidelines and baselines. The certificate therefore uses the existing `outer_singles_floor_corners` convention: the outer rectangle of the singles playing area, not the doubles outer sidelines. Net endpoints are image geometry only. This is a qualitative camera/corner meaning check, not precise click accuracy or an all-frame calibration certificate.

The filled shuttle points use image X right/Y down in the same 1280×720 canvas. The top airborne point at frame 6000 supports that basis. Other samples are ambiguous or demonstrably suspicious: frame 4204 places the legacy point over the racket in a close-up, and frame 8403 places it around the court-logo area. Visibility/confidence and the filename do not establish physical presence or original-versus-filled provenance. No physical shuttle labels were created.

The source itself edits from a 17:15 scoreboard close-up at 4204 to the opening 14:0 wide view at 4207. The nearly repeated player points near frame 0 and 4207 agree with those actual source scenes. This is source chronology, not evidence for a fitted CSV offset. Exact edit timing within the sparse interval and all-frame annotation alignment remain unassessed.

Reviewed panels: [early](early_source_and_legacy.jpg), [mid/court](mid_source_and_legacy.jpg), [late](late_source_and_legacy.jpg). Left is source resized; right adds unchanged legacy coordinates. All ten raw and overlay PNGs are retained, including [court4207](frame_04207_legacy_overlay.png), [close-up4204](frame_04204_legacy_overlay.png), [airborne6000](frame_06000_legacy_overlay.png), and [late8403](frame_08403_legacy_overlay.png).

The [coordinate certificate](diagnostic_coordinate_binding.json) permits generated-reference point/court agreement comparisons under the existing methodology. It does not supply physical AP/mAP, IDF1/HOTA, contact timing, shot classes, scoring or winner ground truth. Unsupported meanings and accuracy remain unknown.
