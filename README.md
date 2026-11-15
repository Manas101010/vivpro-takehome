# Vivpro songs backend

The normalizer reconstructs two column-oriented exports, validates values, and reconciles 29 source rows into 25 songs by exact ID. It generates a row-oriented catalog and an audit that records source locations, conflicts, invalid values, and inferred duration conversions. FastAPI serves the catalog with global sorting, pagination, and exact title lookup after Unicode, case, and whitespace normalization. The pytest suite covers reconciliation and API behavior using both the generated catalog and isolated edge cases.

## Setup and run

Use Python 3.12 with pip. Verification used Python 3.12.3. The direct dependencies in `requirements.txt` are FastAPI and Uvicorn for serving, plus pytest and `httpx2` for tests.

From the repository root in PowerShell, with `python` pointing to Python 3.12:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -B scripts/normalize.py
.\.venv\Scripts\python.exe -B -m uvicorn app.main:app
```

The normalization command reads the two original exports in `data/` and regenerates both files:

- `data/normalized_songs.json` is the catalog loaded by the backend.
- `data/normalization_audit.json` is the reconciliation record. It captures source counts, overlapping IDs, original values, and reasons for cleaning or rejecting values.

## API examples

With the backend running, use a second PowerShell terminal:

```powershell
# Page 2 of the default ID-ascending list
Invoke-RestMethod 'http://127.0.0.1:8000/songs?page=2&size=10'

# Highest tempos across the entire catalog, with nulls last
Invoke-RestMethod 'http://127.0.0.1:8000/songs?sort_by=tempo&order=desc&page=1&size=5'

# Returns both distinct songs named Perfect
Invoke-RestMethod 'http://127.0.0.1:8000/songs/search?title=Perfect'
```

Listing returns `items`, `total`, `page`, `size`, and `total_pages`. Search returns `items` and `total`, with an empty result for an unknown title. Invalid query parameters return HTTP 422.

## Tests

Run the full suite from the repository root:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

## Scope and limitations

The backend assignment excludes the frontend. SQLite ratings are intentionally deferred. The API loads a snapshot at startup, so restart it after regenerating the catalog. Listing sorts in memory, title search matches the whole normalized title, and the duration rules are specific to these exports. See [DECISIONS.md](DECISIONS.md) for reconciliation and API trade-offs and [REVIEW.md](REVIEW.md) for the separate review of the supplied API fixture.
