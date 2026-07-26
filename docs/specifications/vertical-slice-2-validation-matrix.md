# Vertical Slice 2 — Normative Validation Matrix

**Status:** approved (architecture grill, 2026-07-26). Companion to
[vertical-slice-2-repository-configuration-collector.md](vertical-slice-2-repository-configuration-collector.md).

Field key per row: **Mode** live | offline | both | cond (conditionally
live-verifiable). **Cred** S = standing PAT, R = restricted PAT, F = fake.
**Expected** = response class → taxonomy state · deterministic reason. Raw
evidence is always the verbatim envelope+body at the documented path; report
effect is the corresponding state/wait/failure aggregate. **St** M =
mandatory, C = conditional, D = deferred. A live run never validates
offline-only rows.

| ID | Rule / capability | Mode | Fixture / input | Cred | Expected | Projection / report effect | St |
|----|-------------------|------|-----------------|------|----------|----------------------------|----|
| V01 | Protection collected with real values | both | standard-repo | S | 200 object → collected · collected | Field values projected; counts | M |
| V02 | Canonical affirmative absence pin | live | unprotected-repo | S | 404 pinned message → absent · absence-message-matched | absent entry; absence count | M |
| V03 | Empty-repository response class | live | empty-repo | S | Pinned by run → per ADR-0006 rules | Distinct class recorded; never auto-joins absence set | M |
| V04 | Archived-state compatibility | live | archived-repo | S | Corroborates V02 or diverges | Divergence = review evidence, not auto-redefinition | M |
| V05 | Fork compatibility | live | Hello-World | S | Corroborates V02 or diverges | Same | M |
| V06 | Rulesets non-empty inventory | both | standard-repo | S | 200 [1 ruleset] → collected | count 1; summary fields | M |
| V07 | Rulesets empty listing | both | any other repo | S | 200 [] → collected | count 0 (value, never absent) | M |
| V08 | Envelope/header shapes, live | live | all live requests | S | Allowlisted headers only | Envelopes verbatim; no token material | M |
| V09 | Standing-credential record | live | run metadata | S | Success | Documented vs configured vs observed recorded in validation-environment.md | M |
| V10 | Live insufficient authorization | cond | standard-repo protection | R | 403/404 pinned → inaccessible · authorization-denied or absence-rule-unmatched-404 | No absent/unsupported fabrication; gap recorded if R not provisionable | C |
| V11 | Parent-exclusion request contract | both | rulesets requests | S | Raw URL proves includes_parents=false | Only repo-owned summaries project | M |
| V12 | Parent-exclusion behavior | cond | org ruleset provisioned | S | Org ruleset absent from repo projection | Verified against known fixture state; else recorded limitation | C |
| V13 | Absence message case variation | offline | fake 404 variant | F | → inaccessible · absence-rule-unmatched-404 | Reason distinguishes from V19 | M |
| V14 | Absence message text variation | offline | fake 404 variant | F | Same as V13 | Same | M |
| V15 | 404 missing message field | offline | fake | F | Same as V13 | Same | M |
| V16 | 404 non-string message | offline | fake | F | Same as V13 | Same | M |
| V17 | 404 malformed JSON | offline | fake | F | Same as V13 | Same | M |
| V18 | Shape-valid unrecognized 404 | offline | fake | F | Same as V13 | Same | M |
| V19 | Explicit 401/403 denial | offline | fake | F | → inaccessible · authorization-denied | Continuation of unaffected collection | M |
| V20 | Malformed 2xx body | offline | fake | F | → failed · shape-invalid | Failure itemized | M |
| V21 | Primary park then success | offline | fake clock | F | One park, recorded, then collected | Park count/seconds in report | M |
| V22 | Park then renewed exhaustion | offline | fake clock | F | → failed after single park (attempt consumed) | Termination reason recorded | M |
| V23 | Reset beyond maximum park | offline | fake clock | F | → failed · rate_limit_reset_exceeds_maximum_park | No clamp; no early retry | M |
| V24 | Remaining-zero, missing reset | offline | fake | F | Retry-After or bounded fallback · unusable-rate-limit-reset | Reason preserved | M |
| V25 | Remaining-zero, unparseable reset | offline | fake | F | Same as V24 | Same | M |
| V26 | Retry-After precedence over reset | offline | fake | F | Retry-After path taken; no park | Distinct wait category | M |
| V27 | Retry-After beyond maximum | offline | fake | F | → failed · retry-after-exceeds-maximum | Bounded transport failure | M |
| V28 | Markerless 403 | offline | fake | F | No park; → inaccessible via taxonomy | No rate-limit wait recorded | M |
| V29 | Attempts exhaust on 5xx | offline | fake | F | → failed · transport-failed | Attempts = MAX_ATTEMPTS | M |
| V30 | Report wait derivation | offline | rows V21–V29 evidence | F | All categories/durations derived from retained evidence | Planned ≠ attempts preserved | M |
| V31 | Pagination-drift duplicate ID | offline | fake two-page dup | F | First eligible occurrence wins; one visit | Single projection entry | M |
| V32 | Eligibility edges | offline | boolean/string/missing id, bad identity | F | Not targets; no repair | Inventory semantics unchanged; no descriptor state | M |
| V33 | Missing default_branch | offline | fake item without field | F | No request → unknown · missing-required-input | rulesets still observed for that repo | M |
| V34 | Duplicate-ID directories | offline | crafted evidence tree | F | Structural conflict · structural-conflict | No winner; no apparently valid observation | M |
| V35 | Path/envelope ID disagreement | offline | crafted tree | F | Same as V34 | Same | M |
| V36 | Annotation safety edges | offline | reserved/trailing-dot/oversized names | F | ID-only directory; states unaffected | Addressing never alters evidence | M |
| V37 | Rulesets multi-page + cap breach | offline | fake pages | F | Drain; breach → incomplete · pagination-cap | Valid pages still contribute | M |
| V38 | Discovery equivalence | offline | same raw pages | F | Collection plan == offline rederivation (ordered set) | Canonical-rule proof | M |
| V39 | Coverage under incomplete inventory | offline | truncated inventory | F | coverage.inventory_state carries inventory vocabulary | Descriptor states never converted | M |
| V40 | Slice-1-tree compatibility | offline | Slice 1 run tree | F | New projections derive all-unknown/empty; org artifacts byte-stable | Historical derivability preserved | M |
