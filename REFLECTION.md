# Backend Reflection

## 1. What is the single weakest part of your submission, and why did you leave it that way?

The weakest part of my submission is its robustness beyond the provided dataset.

I deliberately chose a lightweight architecture using a normalized JSON catalog loaded into memory, rather than introducing a database for the core data. This simplified reproducibility, testing, and implementation, but introduced trade-offs: the API requires a restart to reflect regenerated data, and sorting the entire catalog in memory for each request would become inefficient with a larger dataset.

The normalization pipeline also relies on dataset-specific assumptions, particularly when converting suspicious duration values from seconds to milliseconds without authoritative unit metadata.

I left these limitations in place because I prioritized the mandatory requirements, edge-case correctness, automated tests, and documented engineering decisions within the assignment's time constraints. Persistent ratings and production-oriented infrastructure were deliberately deferred rather than implemented incompletely.

## 2. Where did AI save you the most time, and where did it cost you time or nearly lead you wrong?

AI saved me the most time during implementation and verification. ChatGPT helped structure the engineering decisions, while Codex translated the approved policies into the normalization pipeline, FastAPI endpoints, and automated tests.

Codex's independent review was particularly useful because it identified the need to validate individual source values before resolving conflicts between overlapping records. It also highlighted subtle sorting requirements involving null values and stable tie-breaking.

However, AI assistance introduced its own overhead. I spent considerable time evaluating alternatives, checking recommendations, and confirming that proposed fixes were justified. For example, clamping invalid measurements initially appeared convenient, but I rejected it because it could produce misleading rankings. A later concern about the `httpx2` dependency also required verification before concluding that the dependency was appropriate.

This reinforced the importance of treating AI output as a proposal to evaluate rather than an unquestionable implementation decision.

## 3. What surprised you about the data? What did you decide not to fix, and why?

The most surprising issue was that the same `duration_ms` column contained values apparently expressed in different units. Three records contained values of 158, 270, and 356, while most other durations were already plausible milliseconds.

I used a documented, conditional conversion rule and retained the original values and conversion reasons in a separate audit trail. I deliberately avoided treating these inferred corrections as independently verified measurements.

Another interesting case was the presence of two songs titled `Perfect` with different IDs. I preserved both rather than merging records based on title similarity.

I also chose not to clamp invalid audio measurements, estimate missing valence values, or automatically merge records with different IDs. These decisions sacrifice some apparent completeness but avoid introducing unsupported information.

## 4. If this went to production Monday and real users hit it, what would break first?

The first operational limitation would likely be data freshness.

The API loads a normalized catalog snapshot at startup. If the underlying dataset changes, running instances continue serving the previous version until restarted. For a static take-home dataset this is acceptable, but a production service would require a more deliberate data-refresh strategy.

As the catalog grows, repeatedly sorting the full dataset in memory and scanning records for title matches would also become increasingly expensive.

My next priorities would be persistent catalog storage, controlled data ingestion and refresh, database-backed filtering and pagination where appropriate, stronger observability, and tests covering changes to incoming data schemas. I would introduce these incrementally rather than adding infrastructure without a demonstrated requirement.
