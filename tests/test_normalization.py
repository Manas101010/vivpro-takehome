import json

import pytest

from scripts import normalize as normalizer


@pytest.fixture(scope="module")
def source_data():
    return normalizer.normalize([
        (filename, json.loads((normalizer.DATA_DIR / filename).read_text(encoding="utf-8-sig")))
        for filename in normalizer.SOURCE_FILES
    ])


def test_source_totals_and_distinct_titles(source_data):
    songs, audit = source_data
    assert audit["source_rows"] == {"songs_part1.json": 16, "songs_part2.json": 13}
    assert audit["total_source_rows"] == 29
    assert len(audit["duplicates"]) == 4
    assert audit["unique_ids"] == len(songs) == len({song["id"] for song in songs}) == 25
    assert {song["id"] for song in songs if song["title"] == "Perfect"} == {
        "0tgVpDi06FyKpA1z0VMD4v", "7dNsHhGeGU5MV01r06O8gK",
    }
    assert "4 walls" in {song["title"] for song in songs}


def test_actual_conflict_and_valence(source_data):
    songs, audit = source_data
    song = next(song for song in songs if song["title"] == "Never Gonna Give You Up")
    assert song["danceability"] == 0.727
    assert song["valence"] == 0.44
    assert sum(song["valence"] is not None for song in songs) == 13
    assert sum(song["valence"] is None for song in songs) == 12
    assert [event for event in audit["events"] if event["reason"] == "valid_values_conflict"] == [{
        "id": song["id"], "field": "danceability", "reason": "valid_values_conflict",
        "selected": {
            "source": "songs_part1.json", "row_index": "13", "raw": 0.727, "normalized": 0.727,
        },
        "alternative": {
            "source": "songs_part2.json", "row_index": "1", "raw": 0.74, "normalized": 0.74,
        },
    }]


def test_actual_missing_invalid_and_converted_values(source_data):
    songs, audit = source_data
    by_id = {song["id"]: song for song in songs}
    events = {
        (event["source"], event["row_index"], event["field"]): event
        for event in audit["events"] if "row_index" in event
    }
    expected = [
        (1, "0", "danceability", "0.521", 0.521, "numeric_string"),
        (1, "0", "tempo", "108.73", 108.73, "numeric_string"),
        (1, "2", "energy", None, None, "missing_key"),
        (1, "10", "energy", "N/A", None, "missing_placeholder"),
        (1, "6", "acousticness", None, None, "explicit_null"),
        (1, "3", "danceability", 1.42, None, "score_out_of_range"),
        (1, "8", "tempo", 0, None, "zero_tempo_unavailable"),
        (2, "7", "acousticness", -0.05, None, "score_out_of_range"),
        (2, "5", "duration_ms", 158, 158000, "inferred_seconds_to_milliseconds"),
        (2, "9", "duration_ms", 270, 270000, "inferred_seconds_to_milliseconds"),
        (2, "11", "duration_ms", 356, 356000, "inferred_seconds_to_milliseconds"),
    ]
    for part, row, field, raw, value, reason in expected:
        event = events[(f"songs_part{part}.json", row, field)]
        assert (event["raw"], event["normalized"], event["reason"]) == (raw, value, reason)
        assert by_id[event["id"]][field] == value


def test_valid_source_wins_per_field_with_file_local_indices():
    songs, audit = normalizer.normalize([
        ("part1.json", {
            "id": {"10": "same", "2": "other"},
            "title": {"2": "Other", "10": " Café "},
            "energy": {"10": False, "2": 0.9},
            "tempo": {"10": 120},
        }),
        ("part2.json", {
            "id": {"2": "same"}, "energy": {"2": 0.5}, "tempo": {"2": 0},
        }),
    ])
    other, same = songs
    assert other["energy"] == 0.9
    assert (same["title"], same["energy"], same["tempo"]) == ("Café", 0.5, 120)
    assert [event["raw"] for event in audit["events"] if event["reason"] == "invalid_numeric_type"] == [
        False,
    ]


@pytest.mark.parametrize(("raw", "expected"), [
    (0, None), (-1, None), (29, None), (30, 30000), (600, 600000), (601, None),
    (29999, None), (30000, 30000), (600000, 600000), (600001, None),
])
def test_duration_bands(raw, expected):
    assert normalizer.parse_value("duration_ms", raw)[0] == expected


@pytest.mark.parametrize(("field", "raw", "expected"), [
    ("energy", True, None), ("energy", float("nan"), None),
    ("tempo", float("inf"), None), ("tempo", -4, None), ("tempo", 1000, 1000),
    ("mood", 2, None), ("num_sections", -1, None), ("num_segments", 1.5, None),
    ("num_segments", 100000, 100000),
])
def test_field_specific_validation(field, raw, expected):
    assert normalizer.parse_value(field, raw)[0] == expected


def test_regeneration_is_byte_identical(tmp_path, monkeypatch):
    for filename in normalizer.SOURCE_FILES:
        (tmp_path / filename).write_bytes((normalizer.DATA_DIR / filename).read_bytes())
    monkeypatch.setattr(normalizer, "DATA_DIR", tmp_path)
    outputs = [tmp_path / name for name in ("normalized_songs.json", "normalization_audit.json")]
    normalizer.main()
    first = [path.read_bytes() for path in outputs]
    normalizer.main()
    assert [path.read_bytes() for path in outputs] == first
