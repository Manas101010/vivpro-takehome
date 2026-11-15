"""Read and query the generated song catalog."""

import json
import unicodedata
from enum import Enum
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "normalized_songs.json"


class SortField(str, Enum):
    ID = "id"
    TITLE = "title"
    DANCEABILITY = "danceability"
    ENERGY = "energy"
    MOOD = "mood"
    ACOUSTICNESS = "acousticness"
    TEMPO = "tempo"
    DURATION_MS = "duration_ms"
    NUM_SECTIONS = "num_sections"
    NUM_SEGMENTS = "num_segments"
    VALENCE = "valence"


def load_catalog():
    try:
        songs = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError(
            f"Could not load {CATALOG_PATH}. Run scripts/normalize.py to generate the catalog."
        ) from error
    if not isinstance(songs, list):
        raise RuntimeError(f"Expected a JSON array of songs in {CATALOG_PATH}")
    return songs


def title_key(title):
    folded = unicodedata.normalize("NFC", title).casefold()
    return " ".join(unicodedata.normalize("NFC", folded).split())


def search(songs, query_key):
    matches = [
        song for song in songs
        if song["title"] is not None and title_key(song["title"]) == query_key
    ]
    return sorted(matches, key=lambda song: song["id"])


def paginate(songs, page, size, field, descending):
    # Stable sorting retains ascending IDs on ties, even for descending sorts.
    by_id = sorted(songs, key=lambda song: song["id"])
    present = [song for song in by_id if song[field] is not None]
    missing = [song for song in by_id if song[field] is None]
    if field == SortField.TITLE:
        present.sort(key=lambda song: title_key(song[field]), reverse=descending)
    else:
        present.sort(key=lambda song: song[field], reverse=descending)
    ordered = present + missing
    start = (page - 1) * size
    total = len(songs)
    return {
        "items": ordered[start:start + size],
        "total": total,
        "page": page,
        "size": size,
        "total_pages": (total + size - 1) // size,
    }
