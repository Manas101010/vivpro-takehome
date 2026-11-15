"""Build the normalized song catalog and its audit from the two source exports."""

import json
import math
import re
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SOURCE_FILES = ("songs_part1.json", "songs_part2.json")
SCORE_FIELDS = ("danceability", "energy", "acousticness", "valence")
COUNT_FIELDS = ("num_sections", "num_segments")
FIELDS = (
    "title", "danceability", "energy", "mood", "acousticness", "tempo",
    "duration_ms", "num_sections", "num_segments", "valence",
)
NUMERIC_STRING = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?")
MISSING = object()


def parse_value(field, raw):
    """Return the normalized value and an audit reason for any change."""
    if raw is MISSING:
        return None, "missing_key"
    if raw is None:
        return None, "explicit_null"
    if field == "title":
        if not isinstance(raw, str) or not raw.strip():
            return None, "invalid_title"
        title = raw.strip()
        return title, "trimmed_title" if title != raw else None

    reason = None
    value = raw
    if isinstance(raw, str):
        token = raw.strip()
        if token.casefold() == "n/a":
            return None, "missing_placeholder"
        if NUMERIC_STRING.fullmatch(token) is None:
            return None, "invalid_numeric_string"
        try:
            value = float(token) if any(mark in token for mark in ".eE") else int(token)
        except ValueError:
            return None, "invalid_numeric_string"
        reason = "numeric_string"
    if type(value) not in (int, float):
        return None, "invalid_numeric_type"
    if isinstance(value, float) and not math.isfinite(value):
        return None, "nonfinite_number"
    if field in SCORE_FIELDS and not 0 <= value <= 1:
        return None, "score_out_of_range"
    if field == "tempo":
        if value == 0:
            return None, "zero_tempo_unavailable"
        if value < 0:
            return None, "negative_tempo"
    if field == "mood" and value not in (0, 1):
        return None, "invalid_mood"
    if field in COUNT_FIELDS and (value < 0 or value != int(value)):
        return None, "invalid_count"
    if field == "duration_ms":
        if 30 <= value <= 600:
            return value * 1000, "inferred_seconds_to_milliseconds"
        if not 30000 <= value <= 600000:
            return None, "unresolved_duration_unit"
    if field == "mood" or field in COUNT_FIELDS:
        value = int(value)
    return value, reason


def audit_raw(value):
    """Keep malformed values representable in strict JSON."""
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite_number": repr(value)}
    if isinstance(value, list):
        return [audit_raw(item) for item in value]
    if isinstance(value, dict):
        return {key: audit_raw(item) for key, item in value.items()}
    return value


def normalize(sources):
    """Normalize ordered (filename, column maps) pairs with higher priority first."""
    catalog = {}
    selected = {}
    events = []
    occurrences = {}
    source_rows = {}
    for filename, columns in sources:
        ids = columns["id"]
        source_rows[filename] = len(ids)
        for index in sorted(ids, key=int):
            song_id = ids[index]
            if not isinstance(song_id, str) or not song_id.strip():
                raise ValueError(f"{filename} row {index} has an invalid song ID")
            song = catalog.setdefault(song_id, {"id": song_id, **dict.fromkeys(FIELDS)})
            winners = selected.setdefault(song_id, {})
            location = {"source": filename, "row_index": index}
            occurrences.setdefault(song_id, []).append(location)
            for field in FIELDS:
                if field not in columns:
                    # A source-wide schema omission is recorded once below.
                    continue
                raw = columns[field].get(index, MISSING)
                value, reason = parse_value(field, raw)
                evidence = {
                    **location, "raw": None if raw is MISSING else audit_raw(raw),
                    "normalized": value,
                }
                if reason:
                    events.append({"id": song_id, "field": field, "reason": reason, **evidence})
                if value is None:
                    continue
                if field not in winners:
                    song[field] = value
                    winners[field] = evidence
                elif value != song[field]:
                    events.append({
                        "id": song_id, "field": field, "reason": "valid_values_conflict",
                        "selected": winners[field], "alternative": evidence,
                    })
        for field in FIELDS:
            if field not in columns:
                events.append({
                    "source": filename, "field": field, "reason": "missing_column",
                    "row_indices": sorted(ids, key=int), "raw": None,
                })

    songs = [catalog[song_id] for song_id in sorted(catalog)]
    audit = {
        "source_rows": source_rows,
        "total_source_rows": sum(source_rows.values()),
        "unique_ids": len(songs),
        "duplicates": [
            {"id": song_id, "rows": occurrences[song_id]}
            for song_id in sorted(occurrences)
            if len(occurrences[song_id]) > 1
        ],
        "events": events,
    }
    return songs, audit


def main():
    sources = [
        (filename, json.loads((DATA_DIR / filename).read_text(encoding="utf-8-sig")))
        for filename in SOURCE_FILES
    ]
    songs, audit = normalize(sources)
    for filename, content in (
        ("normalized_songs.json", songs),
        ("normalization_audit.json", audit),
    ):
        output = json.dumps(content, ensure_ascii=False, indent=2, allow_nan=False)
        (DATA_DIR / filename).write_text(output + "\n", encoding="utf-8", newline="\n")
    print(
        f"{audit['total_source_rows']} source rows -> {len(songs)} unique IDs "
        f"({len(audit['duplicates'])} repeated IDs)"
    )


if __name__ == "__main__":
    main()
