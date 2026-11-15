# PR review

**Request changes.** The listing skips the first page by default, sorts only within each page, and can crash on a valid nullable field. Title lookup silently hides additional matches. These failures break mandatory listing, sorting, and lookup behavior. Ratings are a should-have, and duration statistics are extra scope.

The evidence below comes from the read-only review of the supplied fixture. Reproductions called the original functions directly, using the real catalog or in-memory inputs. HTTP behavior was inferred from the route definitions.

## Blockers

1. **Sort runs after pagination** (`review/buggy_api.py:35–39`, reproduced). Given titles `Z, Perfect, Perfect, A` and a physical first slice of two rows, the handler returns `Perfect, Z`. The globally sorted first slice is `A, Perfect`. Sort the full catalog before slicing.
2. **Sorting crashes on valid null measurements** (`review/buggy_api.py:38–40`, reproduced). Sorting the supplied normalized catalog by `valence` raises `TypeError` when Python compares a float with null. Handle nulls explicitly in both directions and compare populated values according to the field type.
3. **Lookup hides duplicate titles and misses common title variants** (`review/buggy_api.py:43–49`, reproduced). The first exact `Perfect` match wins, hiding the second record. A query such as `" perfect "` returns a miss. Normalize titles and queries consistently for case and spacing, and return every matching record.
4. **The default page skips the first records** (`review/buggy_api.py:33–37`, reproduced). With `page=1` and `size=2`, the slice starts at index 2, skipping indices 0 and 1. Negative sizes can also return unexpected slices. Align the default and offset with the documented page origin and validate page and size before slicing.

## Major

5. **Concurrent cold loads can duplicate the catalog** (`review/buggy_api.py:21–29`, reproduced). Two concurrent calls both passed the empty-cache check and appended the same source row to the shared list. Later requests can report inflated totals and duplicate songs. Load and publish a complete shared snapshot once at startup.
6. **Catalog loading depends on the launch directory** (`review/buggy_api.py:21–29`, reproduced from the repository root). The loader raised `FileNotFoundError` for `songs.json`. This checkout has `data/normalized_songs.json`. A separately supplied file or launch directory could make the fixture work as intended. Document the expected artifact location and resolve it independently of the current working directory. Read it as UTF-8 and validate its shape when loading.
7. **Sort parameters are unvalidated** (`review/buggy_api.py:33–39`, reproduced). An unknown field raises `KeyError` on a populated page, while an unrecognized direction silently sorts ascending. An empty page can hide the invalid field because no key is evaluated. Validate the field against declared attributes and restrict the direction to `asc` or `desc` before querying.
8. **Ratings accept invalid input and target ambiguous titles** (`review/buggy_api.py:55–62`, reproduced). A zero-star rating updates both `Perfect` rows, and rating an unknown title still reports success. The mutation also changes the cached song records served to other requests. Validate the 1–5 range, resolve a single existing song by ID before writing, and store ratings separately from catalog records.
9. **Rating state is worker-local** (`review/buggy_api.py:52–62`, inferred). Ratings persist across ordinary requests handled by one running worker. A restart clears them and different workers can disagree. Document single-worker behavior or use shared durable storage if restarts or multiple workers must be supported.

## Minor

10. **Lookup has inconsistent response shapes** (`review/buggy_api.py:43–49`, response bodies reproduced, HTTP status inferred). A hit returns a bare song, while a miss returns an error object with the route's default HTTP 200. Use a consistent results envelope with an empty list, or document a 404 for a single-resource lookup.
11. **The optional duration average fails on empty or incomplete data** (`review/buggy_api.py:65–72`, empty and null cases reproduced, absent-key case inferred). An empty catalog divides by zero, a null duration fails arithmetic, and an absent field raises `KeyError`. Average valid durations using their count and define the empty result, or omit the endpoint.
