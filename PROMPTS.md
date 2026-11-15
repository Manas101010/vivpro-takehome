# AI collaboration log

The original engineer messages below are copied from the Codex chat **Verify Vivpro workspace** (`01a1e042-3bce-7c40-8863-51c5298daacf`). The notes above each prompt summarize decisions, changes, and observed results.

## P00 — Workspace verification

Codex verified the authorized root, Git root, branch, and initial status in read-only mode. P00 is a label for the original unnumbered opening prompt.

<details>
<summary>Original prompt</summary>

```text
You are assisting with my Vivpro backend take-home assignment.

Before we begin, verify the working environment.

**Authorized project root:**\
`D:\CODES\01-portfolio\vivpro-takehome`

Rules:

- READ-ONLY. Do not create, edit, delete, or move files.
- Do not initialize another repository.
- Do not switch directories to a new project.
- Do not install dependencies, commit, or push.
- Do not modify any files outside the authorized project root.
- Do not begin implementing the assignment.

Use read-only commands to report:

1. Actual current working directory.
2. Actual Git repository root.
3. Current Git branch.
4. Git working-tree status.
5. Existing top-level files and directories.
6. Whether the working directory matches the authorized project root.

If there is any mismatch, stop and explain it.

Otherwise, confirm that the workspace is ready. Then stop and wait for instructions.
```

</details>

## P01 — Requirements and data audit

Codex audited the assignment and source exports. It found four overlapping IDs, a danceability conflict, two distinct `Perfect` records, and three durations that appeared to be in seconds. The audit left policy selection to the engineer.

<details>
<summary>Original prompt</summary>

```text
# P01 — Vivpro Requirements and Data Audit

You are assisting with a Vivpro backend take-home assignment.

Working directory:\
`D:\CODES\01-portfolio\vivpro-takehome`

**Mode: READ-ONLY.**

Do not create, modify, delete, rename, commit, or push files. Do not install dependencies or implement application code.

## Source files

Read:

- `TAKE_HOME.pdf` — authoritative assignment requirements
- `data/songs_part1.json`
- `data/songs_part2.json`
- `review/buggy_api.py` — identify its existence and purpose only; detailed review will happen later

If a file is inaccessible, explicitly report that. Do not infer its contents.

## Task A — Requirements

Read the full assignment PDF.

Summarize the requirements applicable to a backend candidate (Sections 1, 2, 4, 5, and 6).

Classify each deliverable as:

- Must-have
- Should-have
- Documentation/testing requirement

Include any time-budget or submission constraints.

## Task B — Inspect the two datasets

Report:

1. Row count in each dataset.
2. Every attribute present in each source.
3. Attributes shared by both sources and attributes unique to one source.
4. Missing keys, nulls, invalid types, malformed values, and suspicious numeric ranges.
5. Suspected unit inconsistencies, with evidence.
6. Duplicate song IDs within and across sources.
7. Conflicting values for matching song IDs, including exact source indices and values.
8. Any title differences, including casing, spacing, and Unicode considerations.

For every anomaly, provide:

- Source file
- Attribute
- Row index
- Actual value or missing-value description
- Why it is suspicious
- Whether it is confirmed or requires investigation

Do not silently assume that row indices from different files identify the same song.

## Task C — Reconciliation questions

List decisions that I need to make as the engineer before normalization, including:

- Duplicate identity
- Conflict resolution
- Invalid values
- Missing values
- Unit conversion
- Additional attributes
- Preserving source information

Do not choose policies without my approval.

## Task D — Report

Provide:

1. Concise requirements checklist
2. Dataset inventory
3. Evidence-backed anomaly table
4. Duplicate and conflict analysis
5. Open engineering decisions
6. Risks or ambiguities needing clarification

Distinguish observations, assumptions, and recommendations.

Stop after the report. Do not implement anything.
```

</details>

## P02 — Independent decision review

Between P01 and P02, ChatGPT assisted an engineering workshop on D01–D08 and API-R01–R05. The engineer approved the policies and carried them into P02. They reject clamping, preserve raw invalid values, and permit duration conversion only inside explicit bands. The original workshop prompts were unavailable in the history retrieved for this log. Codex independently confirmed the overlaps and challenged the duration boundaries, clarified validation before field-by-field reconciliation, and flagged null placement and stable ties when sorting. The engineer approved those corrections in P03.

<details>
<summary>Original prompt</summary>

```text
\# P02 — Independent Technical Review of Approved Engineering Decisions\
\
\## Mode: READ-ONLY — NO IMPLEMENTATION\
\
You are reviewing my Vivpro backend take-home project.\
\
Repository: the currently opened project.\
\
Read the original assignment PDF, both source JSON files, the existing repository, and the relevant documentation.\
\
Do not modify files, install dependencies, run destructive commands, create commits, or implement anything.\
\
I have completed a data inspection and engineering-decision workshop with ChatGPT. I personally approved the policies below. Your responsibility is to independently challenge them against the actual files, identify mistakes, and produce a minimal implementation plan.\
\
Do NOT pretend these decisions originated from you. Do NOT rubber-stamp them.\
\
\## A. Approved normalization decisions\
\
\*\*D01 — Song identity\*\*\
\- Use exact song IDs to identify duplicate entries.\
\- Merge records sharing an ID.\
\- Never automatically merge different IDs solely because their titles or other attributes are similar.\
\- Preserve distinct recordings with the same title.\
\- Expected: 29 source records, 25 unique IDs, four overlaps. Verify these counts.\
\
\*\*D02 — Attribute conflicts\*\*\
\- Reconcile matching IDs field by field.\
\- If one source provides a valid value and another provides an invalid or missing value, prefer the valid value.\
\- If both valid values disagree, prefer Part 1 as a deterministic tie-breaker.\
\- Preserve conflicting raw values and source information in the audit trail.\
\- Example to verify: the overlapping "Never Gonna Give You Up" danceability values, 0.727 versus 0.74.\
\
\*\*D03 — Types and formatting\*\*\
\- Convert unambiguous numeric strings into numeric values.\
\- Trim surrounding whitespace from titles.\
\- Preserve display capitalization, accents, and punctuation.\
\- Do not invent values when parsing is ambiguous.\
\
\*\*D04 — Missing values\*\*\
\- Retain songs with missing measurements.\
\- Convert missing numeric keys, explicit nulls, and missing-value placeholders such as "N/A" to normalized null.\
\- Preserve the original condition and reason in audit information.\
\- Use another valid source measurement for the same ID if available.\
\
\*\*D05 — Invalid numeric ranges\*\*\
\- Validate numbers using documented field-specific rules.\
\- Mark invalid normalized measurements as null.\
\- Preserve raw measurements and validation failures.\
\- Do not clamp invalid values to boundary values.\
\- Treat tempo = 0 as unavailable under a documented assumption.\
\- Review whether every proposed bound is justified by the field semantics.\
\
\*\*D06 — Mixed duration units\*\*\
\- Treat duration_ms values in 30,000–600,000 as plausible milliseconds.\
\- Treat values in 30–600 as suspected seconds and convert to milliseconds by multiplying by 1,000.\
\- Flag ambiguous, nonpositive, and unsupported values.\
\- Retain original values and indicate conversions were inferred.\
\- These are dataset-specific heuristics, not universal audio limits.\
\- Verify the suspected 158, 270, and 356 values.\
\- Critically inspect boundary cases and possible false conversions.\
\
\*\*D07 — Extra valence attribute\*\*\
\- Include valence in the unified schema.\
\- Preserve valid valence measurements from Part 2, including for overlapping IDs.\
\- Use null when no valid measurement is available.\
\- Do not fabricate or impute valence.\
\- Expected: 13 available, 12 unavailable after reconciliation. Verify.\
\
\*\*D08 — Title matching\*\*\
\- Use normalized exact-title matching.\
\- Normalize Unicode using NFC, case-fold text, and collapse whitespace for comparisons.\
\- Preserve display titles after D03 cleanup.\
\- Return every matching song, including distinct IDs titled "Perfect".\
\- Do not implement fuzzy or substring matching.\
\
\## B. Approved API contract\
\
Framework: FastAPI.\
\
Catalog storage: reproducible normalized JSON file loaded by the backend. Keep a separate JSON normalization audit. No database required for the read-only catalog.\
\
\*\*API-R01 — Pagination\*\*\
\- GET /songs\
\- Query parameters: page, size\
\- One-based page numbering.\
\- Default page = 1, size = 10; maximum size = 100.\
\- Response: items, total, page, size, total_pages.\
\- Stable default order: song ID ascending.\
\- Invalid page or size: HTTP 422.\
\- Valid page beyond last page: HTTP 200 with empty items.\
\
\*\*API-R02 — Title lookup\*\*\
\- GET /songs/search?title=...\
\- Apply D08 matching rules.\
\- Return all matches as full song objects.\
\- Response: items, total.\
\- No match: HTTP 200, items = [].\
\- Missing or blank title: HTTP 422.\
\
\*\*API-R03 — Sorting\*\*\
\- Extend GET /songs with sort_by and order.\
\- Permit sorting by every declared song attribute.\
\- Support asc and desc.\
\- Sort the complete dataset BEFORE applying pagination.\
\- Null values always last in either direction.\
\- Resolve equal values deterministically using ID ascending.\
\- Default sort: ID ascending.\
\- Invalid sort fields or directions: HTTP 422.\
\- Handle numeric attributes numerically and text attributes consistently.\
\
\*\*API-R04 — Ratings (SHOULD-HAVE)\*\*\
\- PUT /songs/{id}/rating\
\- Body: integer rating from 1 through 5.\
\- Store by song ID, not title.\
\- Use SQLite for persistence across requests and restarts.\
\- Replace the previous rating when rating the same song again.\
\- Reject invalid ratings with HTTP 422.\
\- Unknown song ID: HTTP 404.\
\- Do not implement until all mandatory requirements and tests are complete.\
\- If time expires, document it as intentionally deferred.\
\
\*\*API-R05 — Tests\*\*\
Use pytest and FastAPI TestClient.\
\
Prioritize tests proving:\
1\. Correct row reconstruction and ID deduplication.\
2\. Field-by-field conflict resolution.\
3\. Numeric-string conversion, missing values, and invalid ranges.\
4\. Correct mixed-unit duration conversion.\
5\. Valence preservation.\
6\. Pagination metadata, page boundaries, and invalid input.\
7\. Global sorting before pagination.\
8\. Ascending and descending sorting with nulls last and stable ties.\
9\. Title matching across case, whitespace, Unicode, and duplicate titles.\
10\. Rating persistence and validation only if ratings are implemented.\
\
\## C. Proposed code structure\
\
\- scripts/normalize.py — normalization program\
\- data/normalized_songs.json — reproducible clean catalog\
\- data/normalization_audit.json — reconciliation evidence\
\- app/main.py — FastAPI entry point and routes\
\- app/catalog.py — lookup, sorting, pagination\
\- tests/test_normalization.py\
\- tests/test_api.py\
\- requirements.txt\
\
Prefer small, clear Python modules. Avoid unnecessary abstraction, infrastructure, or external services.\
\
The existing review/buggy_api.py is a separate PR-review assignment. Do not rewrite it.\
\
\## D. Your tasks\
\
1\. Verify the assignment requirements and actual dataset against all decisions.\
2\. Identify concrete contradictions, incorrect assumptions, and edge cases.\
3\. Separate must-fix issues from optional improvements.\
4\. Critique the API contracts and explain any correctness concerns.\
5\. Propose the smallest file-by-file implementation sequence.\
6\. Identify the critical tests that must pass before submission.\
7\. Flag anything that would be difficult to explain in a live follow-up.\
8\. Estimate implementation effort at a coarse level, without inventing exact timing.\
\
\## E. Output format\
\
Return only:\
\
1\. \*\*Verdict:\*\* Ready / Ready with corrections / Blocked.\
2\. \*\*Critical findings:\*\* Maximum five, each with evidence and proposed correction.\
3\. \*\*Decision changes required:\*\* Refer to exact D or R IDs.\
4\. \*\*Minimal implementation sequence:\*\* Maximum six steps.\
5\. \*\*Test priorities:\*\* Must-pass checks.\
6\. \*\*Scope cuts:\*\* What to omit if time runs out.\
\
Be concise. Do not generate implementation code.\
\
Stop and wait for my approval.
```

</details>

## P03 — Normalization implementation

Codex implemented the approved policies and generated the catalog and audit. Two runs yielded identical output hashes. Independent Python assertions passed, while pytest remained pending because the available interpreters lacked it and temporary installation was rejected by automatic approval review.

<details>
<summary>Original prompt</summary>

```text
# P03 — M3 Normalization Implementation

P02 reviewed our approved engineering decisions and returned "Ready with corrections."

I approve the P02 corrections. Proceed with M3 implementation only.

**Scope:**

- Implement `scripts/normalize.py`.
- Implement `tests/test_normalization.py`.
- Generate `data/normalized_songs.json`.
- Generate `data/normalization_audit.json`.
- Record D01–D08 and the material P02 corrections concisely in `DECISIONS.md`.

Use the D01–D08 specification supplied in P02. Apply these critical corrections:

1. Reconstruct each column-oriented export using its own row-index keys.
2. Parse and validate source values BEFORE merging matching IDs.
3. Resolve each field independently: prefer a valid value over invalid/missing data; prefer Part 1 only when two valid values conflict.
4. Use the documented inferred field ranges. Reject booleans and nonfinite numeric values. Avoid speculative upper caps for tempo and section/segment counts.
5. Keep invalid/missing measurements as null; preserve source, original value, row index, and reason in the audit.
6. Use inclusive duration bands: 30–600 as suspected seconds and 30000–600000 as milliseconds. Values outside these bands remain unresolved. Audit each inferred conversion.
7. Retain valence and preserve different-ID songs sharing the same title.
8. Produce deterministic, reproducible JSON outputs.

**Required verification:**

- 29 source records → 25 unique song IDs, with four overlaps.
- Both distinct "Perfect" records remain.
- "Never Gonna Give You Up" danceability resolves to 0.727, with both conflicting source values audited.
- 13 populated valence fields and 12 nulls.
- Suspected durations 158, 270, and 356 convert to milliseconds.
- Numeric-string, missing-value, invalid-range, and synthetic valid-versus-invalid conflict tests pass.
- Regenerating outputs twice yields identical content.

Run the normalization script and pytest. Report actual commands and results.

**Constraints:**

- Do not implement API endpoints, ratings, or frontend.
- Do not rewrite `review/buggy_api.py`.
- Do not commit or push.
- Do not invent earlier AI prompts in `PROMPTS.md`.
- Do not introduce unnecessary frameworks or abstractions.

**Final response:**

1. Files changed.
2. Test results and actual dataset counts.
3. Important implementation decisions.
4. Remaining issues.
5. Exact commands to reproduce the results.

Stop after M3 and wait for review.
```

</details>

## P04 — Normalization verification

The engineer explicitly authorized installing pytest in the ignored project-local virtual environment. Codex then ran the actual normalization suite. All 24 tests passed, and both generated files matched their prior hashes.

<details>
<summary>Original prompt</summary>

```text
# P04 — Finish M3 Verification

M3 implementation is complete, but pytest has not run because the available Python environment lacks pytest.

I explicitly authorize you to:

1. Create or reuse a project-local `.venv` using the available Python interpreter.
2. Install pytest and its necessary dependencies into that virtual environment only. Do not install globally.
3. Verify `.venv/` is ignored by Git.
4. Run `tests/test_normalization.py` using pytest.
5. If tests fail due to implementation defects, fix only the relevant M3 code and rerun them.
6. Run `git diff --check` and `git status --short`.
7. Confirm normalization outputs remain deterministic.

Report:

- Exact test command
- Number of tests collected, passed, failed, and skipped
- Any defects discovered and corrections made
- Files changed
- Final Git status

Do not implement M4, change unrelated files, commit, or push.

If dependency installation fails, stop and report the exact error without claiming tests passed.
```

</details>

## P05 — FastAPI implementation

Codex implemented and tested the two mandatory endpoints. The successful runs reported 24 normalization tests, 48 API tests, and 72 tests in the combined suite. Uvicorn smoke checks passed for both routes. Windows loopback access was needed for TestClient in the sandbox. A Starlette warning identified plain `httpx` as deprecated, so Codex switched to `httpx2` and reran verification.

<details>
<summary>Original prompt</summary>

```text
# P05 — M4 FastAPI Implementation and Verification

M3 has been verified: 24 normalization tests passed, both generated JSON artifacts are deterministic, and the normalized catalog contains 25 unique songs.

I authorize M4 implementation only.

## Objective

Build the mandatory FastAPI backend over the existing normalized dataset using our approved API-R01, R02, R03, and R05 decisions.

## Implementation scope

1. Create `app/catalog.py` for catalog loading, sorting, pagination, and title lookup.
2. Create `app/main.py` for FastAPI routes and input validation.
3. Create `tests/test_api.py` for contract and edge-case tests.
4. Create `requirements.txt` containing the dependencies needed to install, run, and test the backend on a clean machine.
5. Update `DECISIONS.md` with the finalized API decisions and their trade-offs.

Keep the solution small, readable, and explainable in a live interview.

## Endpoint 1 — GET /songs

Query parameters:

- page: default 1, minimum 1
- size: default 10, minimum 1, maximum 100
- sort_by: default id
- order: asc or desc, default asc

Response:

- items
- total
- page
- size
- total_pages

Required behavior:

- Sort the complete dataset BEFORE pagination.
- Allow sorting by every declared song attribute.
- Sort numeric fields numerically, not as strings.
- Sort text consistently using documented comparison rules.
- Place null values last in both ascending and descending order.
- Keep ID ascending as the deterministic tie-breaker, even in descending primary-field sorts.
- Default to exact song ID ascending.
- Invalid page, size, sort field, or order returns HTTP 422.
- An out-of-range page returns HTTP 200 with empty items and accurate metadata.
- For an empty catalog, total_pages = 0.

## Endpoint 2 — GET /songs/search?title=...

Required behavior:

- Normalize title comparisons using Unicode NFC, case folding, and whitespace collapsing.
- Apply equivalent normalization to query input and stored titles.
- Preserve original display titles.
- Return every matching song as a complete record.
- Sort multiple matches by exact song ID ascending.
- Response: items and total.
- Unknown title returns HTTP 200 with items=[] and total=0.
- Missing or whitespace-only title returns HTTP 422.
- Preserve both distinct records named "Perfect".

## Testing

Use pytest and FastAPI TestClient.

Test:

1. Default pagination and metadata.
2. First, middle, final partial, and out-of-range pages.
3. Invalid page and size parameters.
4. Global sorting before pagination.
5. Ascending and descending numeric sorting.
6. Nulls last in both directions.
7. Deterministic ID tie-breaking.
8. Sorting by every declared attribute, including valence.
9. Invalid sorting parameters.
10. Title lookup with casing, whitespace, Unicode, and duplicate titles.
11. No-match and invalid title handling.
12. Empty-catalog behavior.

Use isolated synthetic data where useful to prove edge cases without changing the real catalog.

## Environment and verification

You may use the existing project-local `.venv` and install the minimum required dependencies there only.

Run:

- M3 normalization tests
- M4 API tests
- Complete pytest suite
- git diff --check
- git status --short

Verify that the application loads the normalized JSON using a project-relative path, not an absolute Windows path.

## Constraints

- Do not modify the original JSON exports.
- Do not change M3 normalization logic unless a demonstrated defect requires it; report any such defect before changing it.
- Do not implement SQLite ratings yet.
- Do not build a frontend.
- Do not rewrite review/buggy_api.py.
- Do not fabricate or reconstruct AI prompts in PROMPTS.md.
- Do not commit or push.
- Avoid unnecessary abstractions, configuration systems, or infrastructure.

## Final report

Return:

1. Files created or changed.
2. API endpoints implemented.
3. Test counts: passed, failed, skipped.
4. Any bugs discovered and fixed.
5. Exact command to launch the backend.
6. Remaining issues and Git status.

Stop after M4 and wait for review.
```

</details>

## P06 — Independent fixture review

Codex reproduced key fixture defects with direct calls, kept HTTP effects separate as inferences, and confirmed that `requirements.txt` lists `httpx2` and the installed Starlette TestClient imports it. The dependency check inspected the existing environment.

<details>
<summary>Original prompt</summary>

```text
# P06 — M5 Independent AI Code Review

M4 is complete. The full test suite reportedly passed 72/72 tests.

Proceed with M5: review the provided `review/buggy_api.py` as a pull request.

MODE: READ-ONLY. Do not modify any files yet.

## Task

Read the entire original `review/buggy_api.py` and review its behavior against the Vivpro take-home requirements.

Identify correctness, reliability, validation, and design problems.

Prioritize substantive bugs over stylistic issues.

For every finding, report:

1. File and exact line number(s).
2. What is wrong.
3. The observable impact, including when it occurs.
4. A concise suggested fix.
5. Severity: Blocker / Major / Minor / Nit.
6. Whether the finding is confirmed by inspection, reproduced, or only suspected.

Pay particular attention to:

- Data loading and assumptions.
- Pagination boundary behavior.
- Sorting before or after pagination.
- Type-safe sorting and missing values.
- Duplicate titles and title normalization.
- Invalid inputs and HTTP responses.
- Rating correctness and persistence, if present.
- Shared mutable state or subtle behavior that happy-path tests may miss.

Do not assume the review fixture implements our approved design. Review what the code actually does.

Distinguish actual defects from differences in implementation preference.

If safe, use minimal read-only checks to support important findings. Do not rewrite or fix the supplied review fixture.

## Additional M4 dependency check

Briefly inspect `requirements.txt` and `tests/test_api.py` to clarify:

- Whether `httpx2` is actually listed.
- Whether the intended dependency is `httpx`.
- Whether the complete test environment can be reproduced from `requirements.txt`.

Report any confirmed dependency problem separately from the supplied code-review findings.

## Output

1. Ranked findings, with evidence and suggested fixes.
2. The top three issues that should influence the human PR-review decision.
3. Possible false positives or areas needing human judgment.
4. Dependency check result.
5. Any unresolved questions.

Do not write REVIEW\.md yet.\
Do not modify implementation, documentation, or tests.\
Do not commit or push.

Stop and await review.
```

</details>

## P07 — Human severity review

The engineer approved the final priority of the 11 findings, including elevating the pagination offset to blocker and qualifying the catalog path and process-local rating concerns. Codex wrote the findings in `REVIEW.md`.

<details>
<summary>Original prompt</summary>

```text
# P07 — Finalize M5 Code Review

P06 completed the read-only review of review/buggy_api.py and reported 11 findings.

I approve proceeding with REVIEW\.md, subject to the following human-reviewed severity judgments:

PR blockers:

- Sorting after pagination.
- Sorting crashes on valid null measurements.
- Title lookup hides duplicate-title matches.
- Incorrect pagination offset skips initial records.

Major:

- Invalid rating values and ambiguous title-based updates.
- Invalid sorting parameters.
- Shared-cache initialization race condition.
- Hardcoded catalog path, with severity qualified by runtime setup.
- Process-local ratings, conditionally significant for restarts or multiple workers.

Minor:

- Inconsistent lookup response shape.
- Optional duration-average endpoint failures.

Use the evidence collected during P06.

For each finding, write:

1. Exact source line(s).
2. The defect.
3. Observable impact.
4. Concise recommended fix.
5. Severity and whether the issue was reproduced or inferred.

Requirements:

- Rank findings by practical importance.
- Clearly explain why the pull request should be blocked.
- Distinguish mandatory correctness failures from optional improvements.
- Preserve uncertainty about the expected songs.json location.
- Do not incorrectly claim in-memory ratings fail to persist across ordinary requests within one worker.
- Do not rewrite or modify review/buggy_api.py.
- Keep REVIEW\.md concise but substantive.
- Do not fabricate independent discoveries or tests.
- Do not edit unrelated files, commit, or push.

After writing REVIEW\.md:

- Run git diff --check.
- Report the file changed, findings documented, and remaining concerns.
- Stop for approval.
```

</details>

## P08 — Submission documentation

The engineer requested a chronological prompt log, PowerShell reproduction instructions, and reflection drafts for their review.

<details>
<summary>Original prompt</summary>

```text
# P08 — M6 Submission Documentation

M3, M4, and M5 are complete. Codex reported 72 passing tests, and REVIEW\.md now contains 11 ranked findings.

Proceed with M6 documentation only.

## 1. PROMPTS.md — Honest AI Collaboration History

Document the actual prompts and collaboration in chronological order.

Use the real Codex conversation history for P00 through P08 wherever accessible.

Important:

- Preserve actual prompt text or provide an accurate reference to a real session export.
- Do not invent, reconstruct as verbatim, or backdate missing prompts.
- If any original prompt is inaccessible, explicitly state that rather than fabricating it.
- Record that ChatGPT assisted an engineering decision workshop covering D01–D08 and API-R01–R05, while the engineer approved the policies.
- Attribute Codex's independent P02 criticism and implementation work accurately.
- Include concise annotations explaining important turning points: rejection of clamping, conditional duration conversion, validation before reconciliation, verified test results, and confirmation of the httpx2 dependency.
- Distinguish engineer decisions, ChatGPT suggestions, Codex findings, and verified results.

Keep the log accurate and reasonably concise.

## 2. README.md — Clean-Machine Reproduction

Write a concise README containing:

- A four-sentence solution overview.
- Required Python version and dependencies.
- Windows PowerShell setup commands, including a project-local virtual environment.
- Installation using requirements.txt.
- Command to regenerate normalized JSON and the audit artifact.
- Command to start the FastAPI backend.
- Examples for pagination, sorting, and title lookup.
- Command to run all tests.
- Explanation of normalized_songs.json versus normalization_audit.json.
- Explanation that no frontend was required for the backend submission.
- Explicit note that SQLite ratings remain intentionally deferred.
- Any known limitations.

Use commands that actually match this repository.

## 3. REFLECTION.md — Backend Candidate

Draft concise answers to these four questions:

1. What is the weakest part of the submission, and why was it left that way?
2. Where did AI save time, and where did it cost time or nearly lead the engineer wrong?
3. What was surprising in the data, and what was deliberately not fixed?
4. What would break first under real production usage?

Base answers on the real project and observed development history.

Do not invent personal experiences, decisions, or test results.

Clearly mark subjective reflection answers as drafts requiring engineer review.

Do not answer the fifth lead/architect-only question.

## 4. Consistency checks

Review DECISIONS.md and REVIEW\.md for completeness without unnecessarily rewriting them.

Verify:

- Documentation matches implemented routes.
- README commands are reproducible.
- PROMPTS.md does not present reconstructed prompts as originals.
- Ratings are accurately described as deferred.
- No claims of tests or deployment beyond observed evidence.

Run git diff --check and git status --short.

Do not implement new features.\
Do not modify review/buggy_api.py.\
Do not commit or push.

Report files changed, unresolved documentation gaps, and anything requiring engineer input.

Stop after M6.
```

</details>

## P09 — Final verification and submission

The engineer approved the reflection and authorized final verification, a normal commit, and a normal push to the existing remote.

<details>
<summary>Original prompt</summary>

```text
# P09 — Final Verification, Commit, and Push

M6 documentation is complete. The engineer has reviewed and approved the reflection answers.

I authorize M7 final verification, normal Git commits, and pushing to the existing GitHub remote.

1. Remove the draft-for-review notice from REFLECTION.md.
2. Verify the required submission contents:
   - Original JSON datasets
   - Normalization code and generated outputs
   - Normalization audit
   - FastAPI implementation
   - Tests and requirements.txt
   - PROMPTS.md
   - DECISIONS.md
   - REVIEW\.md
   - REFLECTION.md
   - README.md
3. Append this actual P09 prompt to PROMPTS.md if available in the Codex session, accurately and in order.
4. Confirm the assignment PDF, ZIP archives, virtual environment, caches, and secrets will not be committed.
5. Run the full pytest suite, verify normalization regeneration, and run git diff --check.
6. Review the complete Git staging list. Stage only required submission files.
7. Create an honest commit representing the actual completed work. Do not backdate or manufacture intermediate commits.
8. Push to the existing origin/main using a normal push. Do not force-push.
9. Verify the local branch is synchronized with the remote and the Git working tree is clean.

If any critical check fails, stop and report the problem. Do not claim success.

Return only:

- Final test results
- Commit hash
- Push status
- Files committed
- Remaining blockers
- GitHub repository URL

Do not email the submission. Do not implement new features.
```

</details>
