"""Spatial scoreboard regressions from real model observations, not GT point labels.

India proxy SHA: 018df5d81dbb60c692805acf558992554e4a24b29fc8e64ea28fd0857bd1ac49
Frames3000/4500 contain a two-row board plus unrelated court sponsor text.
No media, scores from labels, models or downloaded annotations are required.
"""

import pytest

from bai_badminton.perception.scoreboard import parse_scoreboard

OBSERVATIONS = {
    0: {
        "type": "RapidOCROutput",
        "txts": ["NOIAOPEN", "INODIA PEN", "YONEX", "0", "HS"],
        "scores": [0.81073, 0.61765, 0.99994, 0.99962, 0.99952],
        "boxes": [
            [[0.0, 68.0], [65.0, 66.0], [66.0, 96.0], [0.0, 98.0]],
            [[426.0, 80.0], [500.0, 81.0], [500.0, 113.0], [425.0, 112.0]],
            [[345.0, 128.0], [424.0, 129.0], [423.0, 161.0], [344.0, 159.0]],
            [[196.0, 143.0], [207.0, 143.0], [207.0, 157.0], [196.0, 157.0]],
            [[551.0, 138.0], [575.0, 138.0], [575.0, 159.0], [551.0, 159.0]],
        ],
    },
    800: {
        "type": "RapidOCROutput",
        "txts": ["NDIAOPEN", "INAIAPEN", "YONEX", "0", "HS"],
        "scores": [0.8192, 0.76327, 0.99993, 0.99966, 0.9996],
        "boxes": [
            [[0.0, 68.0], [65.0, 65.0], [66.0, 95.0], [0.0, 98.0]],
            [[425.0, 80.0], [501.0, 80.0], [501.0, 113.0], [425.0, 113.0]],
            [[344.0, 128.0], [424.0, 129.0], [423.0, 161.0], [344.0, 159.0]],
            [[197.0, 143.0], [206.0, 143.0], [206.0, 156.0], [197.0, 156.0]],
            [[551.0, 138.0], [575.0, 138.0], [575.0, 159.0], [551.0, 159.0]],
        ],
    },
    1600: {
        "type": "RapidOCROutput",
        "txts": ["NDIAOPEN", "INDIAPEN", "YONEX", "HS"],
        "scores": [0.8335, 0.69889, 0.99993, 0.99946],
        "boxes": [
            [[0.0, 67.0], [66.0, 66.0], [66.0, 96.0], [0.0, 97.0]],
            [[426.0, 81.0], [500.0, 81.0], [499.0, 113.0], [426.0, 112.0]],
            [[343.0, 128.0], [424.0, 129.0], [423.0, 161.0], [343.0, 160.0]],
            [[551.0, 138.0], [575.0, 138.0], [575.0, 159.0], [551.0, 159.0]],
        ],
    },
    3000: {
        "type": "RapidOCROutput",
        "txts": ["VONEX-SUNRISE", "LOH K.Y.", "2", "NDIAOPEN", "SEN", "0", "INDIA OPEN", "2", "0", "YONEX", "HS"],
        "scores": [0.96778, 0.97366, 0.99999, 0.8515, 0.99997, 0.99992, 0.96985, 0.99986, 0.9995, 0.99993, 0.99954],
        "boxes": [
            [[420.0, 11.0], [504.0, 15.0], [503.0, 47.0], [419.0, 44.0]],
            [[283.0, 44.0], [342.0, 44.0], [342.0, 60.0], [283.0, 60.0]],
            [[417.0, 44.0], [430.0, 44.0], [430.0, 61.0], [417.0, 61.0]],
            [[0.0, 67.0], [65.0, 66.0], [66.0, 96.0], [0.0, 97.0]],
            [[283.0, 65.0], [316.0, 65.0], [316.0, 82.0], [283.0, 82.0]],
            [[417.0, 65.0], [430.0, 65.0], [430.0, 82.0], [417.0, 82.0]],
            [[427.0, 83.0], [499.0, 83.0], [499.0, 111.0], [427.0, 111.0]],
            [[194.0, 127.0], [205.0, 127.0], [205.0, 141.0], [194.0, 141.0]],
            [[196.0, 143.0], [207.0, 143.0], [207.0, 157.0], [196.0, 157.0]],
            [[345.0, 129.0], [423.0, 129.0], [423.0, 160.0], [345.0, 159.0]],
            [[551.0, 138.0], [575.0, 138.0], [575.0, 159.0], [551.0, 159.0]],
        ],
    },
    4500: {
        "type": "RapidOCROutput",
        "txts": ["LOH K.Y.", "2", "NDAIOPEN", "SEN", "1", "INDIAOPEN", "2", "YONEX", "HS"],
        "scores": [0.89151, 0.99999, 0.69151, 0.99997, 0.99975, 0.77362, 0.99995, 0.99994, 0.99926],
        "boxes": [
            [[283.0, 44.0], [342.0, 44.0], [342.0, 60.0], [283.0, 60.0]],
            [[417.0, 44.0], [430.0, 44.0], [430.0, 61.0], [417.0, 61.0]],
            [[0.0, 66.0], [65.0, 64.0], [66.0, 96.0], [0.0, 98.0]],
            [[283.0, 65.0], [316.0, 65.0], [316.0, 82.0], [283.0, 82.0]],
            [[419.0, 66.0], [427.0, 66.0], [428.0, 80.0], [420.0, 81.0]],
            [[426.0, 81.0], [499.0, 83.0], [499.0, 113.0], [425.0, 111.0]],
            [[197.0, 127.0], [206.0, 129.0], [204.0, 140.0], [195.0, 139.0]],
            [[343.0, 128.0], [424.0, 130.0], [423.0, 160.0], [342.0, 159.0]],
            [[551.0, 138.0], [575.0, 138.0], [575.0, 159.0], [551.0, 159.0]],
        ],
    },
}


@pytest.mark.parametrize("frame,current", [(3000, 0), (4500, 1)])
def test_real_corner_separates_board_from_court_sponsor_text(frame, current):
    raw = OBSERVATIONS[frame]
    result = parse_scoreboard(raw["boxes"], raw["txts"], raw["scores"], frame)
    assert result is not None
    reading, bounds = result
    assert reading.rows == (("LOH K.Y.", 2), ("SEN", current))
    assert reading.frame_idx == frame
    assert bounds[0] >= 270 and bounds[2] <= 440 and bounds[3] <= 90


@pytest.mark.parametrize("frame", [0, 800, 1600])
def test_real_absent_names_and_court_miniscore_are_not_a_board(frame):
    raw = OBSERVATIONS[frame]
    assert parse_scoreboard(raw["boxes"], raw["txts"], raw["scores"], frame) is None


def box(x, y, w=70, h=20):
    return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]


def read(items):
    return parse_scoreboard([item[0] for item in items], [item[1] for item in items], [0.95] * len(items), 12)


def rows(names=("ALPHA", "BETA"), scores=("8", "7"), x=10):
    return [
        item
        for i, (name, score) in enumerate(zip(names, scores, strict=True))
        for item in [(box(x, 10 + 30 * i), name), (box(x + 180, 10 + 30 * i, 20), score)]
    ]


@pytest.mark.parametrize("reverse", [False, True])
def test_multiple_plausible_boards_abstain_independent_of_order(reverse):
    items = rows() + rows(("GAMMA", "DELTA"), ("11", "10"), x=400)
    if reverse:
        items.reverse()
    assert read(items) is None


def test_three_aligned_score_rows_are_not_silently_trimmed_to_two():
    assert read(rows(("ALPHA", "BETA", "GAMMA"), ("8", "7", "6"))) is None


@pytest.mark.parametrize("bad", ["31", "45", "12:45", "unavailable"])
def test_invalid_current_score_does_not_fall_back_to_finished_game(bad):
    items = rows(scores=(bad, "7"))
    items.insert(1, (box(140, 10, 20), "21"))
    assert read(items) is None


@pytest.mark.parametrize("names", [("A. ALPHA / B. BETA", "C. GAMMA / D. DELTA"), ("ONE", "A MUCH LONGER NAME")])
def test_single_and_doubles_names_keep_tokens_and_right_aligned_name_columns(names):
    items = []
    for i, name in enumerate(names):
        width = 6 * len(name)
        items.extend([(box(180 - width, 10 + 30 * i, width), name), (box(220, 10 + 30 * i, 20), str(9 - i))])
    result = read(items)
    assert result is not None
    assert result[0].rows == tuple((" ".join(name.replace("/", " ").split()), 9 - i) for i, name in enumerate(names))


def test_a_numeric_column_left_of_names_is_not_a_scoreboard():
    items = [(box(10, 10, 20), "2"), (box(10, 40, 20), "1"), (box(150, 10), "ALPHA"), (box(150, 40), "BETA")]
    assert read(items) is None


def test_clock_or_digit_logo_cannot_link_distant_unaligned_names():
    items = [
        (box(10, 10), "12:45"),
        (box(300, 10), "LIVE"),
        (box(10, 90), "2"),
        (box(150, 90), "YONEX"),
        (box(10, 120), "1"),
        (box(300, 120), "HSBC"),
    ]
    assert read(items) is None


@pytest.mark.parametrize("scale", [0.5, 1.0, 2.0])
@pytest.mark.parametrize("reverse", [False, True])
def test_numeric_fields_belong_to_nearest_names_not_broadcast_logos(scale, reverse):
    items = []
    for row, (name, score) in enumerate([("ALPHA", "9"), ("BETA", "12")]):
        y = 10 + 30 * row
        items.extend([(box(0, y, 50), "NETWORK"), (box(150, y, 70), name), (box(280, y, 20), score)])
    items = [([[x * scale, y * scale] for x, y in points], text) for points, text in items]
    if reverse:
        items.reverse()
    result = read(items)
    assert result is not None
    assert result[0].rows == (("ALPHA", 9), ("BETA", 12))
    assert result[1][0] >= 150 * scale


def test_logo_pair_cannot_use_athlete_scores_when_current_column_is_missing():
    items = []
    for row, name in enumerate(["ALPHA", "BETA"]):
        y = 10 + 30 * row
        items.extend([(box(0, y, 50), "NETWORK"), (box(150, y, 70), name)])
    items.extend([(box(250, 10, 50), "16 21"), (box(250, 40, 80), "21 5 12")])
    assert read(items) is None


def test_actual_test2_model_missing_current_digit_cannot_lock_to_logo():
    # Exact fixed-crop model output, source frame22924; these are observations,
    # not annotation labels. Top row's current digit was not recognized.
    texts = ["Ba", "SXFI", "AXELSEN", "16 21", "LIVE", "ANTONSEN", "21 5 12", "YONEX", "16219"]
    bounds = [
        (511, 1, 575, 66),
        (87, 43, 165, 66),
        (284, 45, 350, 61),
        (412, 43, 477, 64),
        (87, 64, 166, 87),
        (284, 66, 362, 83),
        (411, 65, 493, 84),
        (353, 136, 437, 165),
        (90, 148, 160, 174),
    ]
    items = [(box(x0, y0, x1 - x0, y1 - y0), text) for text, (x0, y0, x1, y1) in zip(texts, bounds, strict=True)]
    assert read(items) is None


def test_complete_current_column_keeps_actual_names_and_excludes_logo_from_roi():
    items = [
        (box(87, 43, 78, 23), "SXFI"),
        (box(284, 45, 66, 16), "AXELSEN"),
        (box(412, 43, 81, 21), "16 21 9"),
        (box(87, 64, 79, 23), "LIVE"),
        (box(284, 66, 78, 17), "ANTONSEN"),
        (box(411, 65, 82, 19), "21 5 12"),
    ]
    result = read(items)
    assert result is not None
    assert result[0].rows == (("AXELSEN", 9), ("ANTONSEN", 12))
    assert result[1] == (284.0, 43.0, 493.0, 84.0)
