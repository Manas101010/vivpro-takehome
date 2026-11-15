# Normalization decisions

- **D01 — Identity.** Reconstruct rows by each export's own index keys. Merge on exact song ID. Keep different IDs with the same title, including both `Perfect` records.
- **D02 — Conflicts.** Parse and validate each source value before resolving its field. The first valid value wins, with Part 1 taking precedence over Part 2 when both are valid and disagree. If an export repeats an ID, the lower source index has precedence among its valid values. Audit each conflict with both raw values, source filenames, and row indices. Part 1 precedence is a deterministic tie-breaker with no source-quality claim.
- **D03 — Types and display.** Parse unambiguous decimal and scientific numeric strings. Trim title edges while preserving display case, accents, and punctuation. Audit conversions and title trimming.
- **D04 — Missing values.** Retain songs and use null when no valid measurement exists. Distinguish absent keys, explicit nulls, and the `N/A` placeholder in audit events. Record a source-wide column omission once with its affected row indices.
- **D05 — Ranges.** Use inferred inclusive `[0, 1]` bounds for danceability, energy, acousticness, and valence. Mood accepts `0` or `1`. Tempo must be positive, with zero treated as unavailable. Section and segment counts must be nonnegative integers. Tempo and counts have no upper cap. Reject booleans and nonfinite numbers. Invalid measurements become null if no valid fallback exists, with the original value and reason audited.
- **D06 — Duration.** For these exports, infer seconds in inclusive `30–600` and multiply by 1,000. Accept `30,000–600,000` as milliseconds, inclusive. Values outside both bands remain unresolved and are audited. The short band can misclassify genuine subsecond clips, and no upstream unit metadata confirms the inference. Every conversion carries its raw value and source location in the audit.
- **D07 — Valence.** Keep valid values from Part 2, including on overlapping IDs. Use null when neither source supplies a valid measurement.
- **D08 — Title lookup.** Normalize both query and title with NFC, case folding, and whitespace collapse, then match the entire normalized title. Preserve display titles in responses.

The catalog is ordered by exact ID. Source priority, numeric row order, field order, and fixed UTF-8 JSON formatting keep both artifacts reproducible.

## API decisions

- **API-R01 — Listing.** `GET /songs` uses one-based pages, with defaults of page 1 and size 10, and caps size at 100. Invalid inputs return 422. Pages beyond the end return an empty list with accurate metadata. An empty catalog has zero pages.
- **API-R02 — Search.** `GET /songs/search?title=...` applies D08 and returns full records in exact ID order, including both `Perfect` matches. An unknown title returns an empty result. Missing or whitespace-only input returns 422. A separate search route makes multiple matches explicit.
- **API-R03 — Sorting.** Sort the complete catalog before slicing a page. Compare numbers numerically, IDs by exact code-point order, and titles by their D08 comparison keys. Nulls go last in either direction, and equal keys retain ascending exact IDs. ID ascending is the default. Sorting in memory on each request is straightforward for this small catalog.
- **API-R05 — Verification.** Test the real generated catalog and use isolated fixtures for numeric ordering, nulls, ties, and empty results.

The backend loads the generated JSON into memory when the app starts, using a path anchored to the project. Regeneration takes effect after restart. SQLite ratings remain deferred.
