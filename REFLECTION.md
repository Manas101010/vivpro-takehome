# Backend reflection

## 1. Weakest part and why it was left that way

Duration reconciliation depends on a value heuristic. The three short values look like seconds, but the export has no per-row unit metadata and a real short clip could be converted incorrectly. The submission keeps the heuristic specific to these exports and records the original value and inferred conversion for review.

## 2. Where AI saved time or added friction

ChatGPT helped organize the decision workshop, and Codex turned the approved rules into normalization, API, and test code. Codex's independent review also exposed a gap in the initial plan by making validation before reconciliation explicit. Verification took another round because the first environment lacked pytest. Later, a Starlette warning prompted a dependency change from `httpx` to `httpx2` and another test run.

## 3. What was surprising and what was left alone

The three suspicious durations were mixed into the same column as plausible millisecond values. Two distinct IDs also shared the exact title `Perfect`. The approved policy kept those IDs separate, preserved questionable measurements in the audit, and left unavailable measurements null without clamping or imputation.

## 4. What would break first in production

Catalog freshness is the first likely operational problem. The API loads its snapshot once, so regenerating the file leaves running workers serving stale data until restart. With a much larger catalog, sorting the full collection on each listing request and scanning it for title lookup would also increase latency.
