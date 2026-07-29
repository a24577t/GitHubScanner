# Vertical Slice 2 — Repository Configuration Collector

**Status:** approved (architecture grill, 2026-07-26). Governing decisions:
[ADR-0001](../adr/0001-collector-architecture-three-evidence-layers.md),
[ADR-0002](../adr/0002-evidence-state-taxonomy.md),
[ADR-0003](../adr/0003-explicit-environment-targeting.md),
[ADR-0004](../adr/0004-repository-resource-observation-model.md),
[ADR-0005](../adr/0005-target-discovery-evidence-addressing.md),
[ADR-0006](../adr/0006-taxonomy-evidence-rules.md),
[ADR-0007](../adr/0007-bounded-execution-waits.md).
Normative validation matrix: [vertical-slice-2-validation-matrix.md](vertical-slice-2-validation-matrix.md).

## Purpose

Extend collection from organization-scoped endpoints to repository-scoped
configuration under the Repository Resource Observation Model (ADR-0004),
preserving every Slice 1 invariant: verbatim append-only raw evidence,
byte-identical offline derivation, one taxonomy state per targeted resource,
affirmative absence, token secrecy, partial evidence as evidence. Two
descriptors ship: `default-branch-protection` (primary — exercises absence
anchoring, required inputs, and the full uncertainty ladder) and
`repository-rulesets` (additivity proof — orthogonal in shape, pagination,
absence semantics, and inputs). ADR-0004's falsifiable claim is an acceptance
criterion: adding the second descriptor must touch only descriptor, projection,
tests, and fixtures.

## CLI contract

Unchanged from Slice 1. `--max-pages` caps every paginated listing
independently (inventory and each repository's rulesets drain); a breach marks
that one listing `incomplete`, never truncates silently. Exit 0 for every
orderly run including partial evidence; non-zero only when the run frame cannot
be established (unchanged conditions).

## Resource descriptors

### default-branch-protection

Observes only the protection object of the branch identified as the
repository's default branch in the current run's repository inventory. It makes
no claim about protection on any other branch and no claim that protection is
required. `collected` means the protection object and its GitHub-defined
configuration were collected; `absent` means GitHub affirmatively indicated no
protection object exists for that branch; both are observational and carry no
compliance implication; an approved exception never alters the observed state.

- Request: `GET /repos/{full_name}/branches/{default_branch}/protection`;
  required input `default_branch` (per-repository, from inventory evidence).
- Shape: object. Absence anchor (ADR-0006): 404 + shape-valid JSON + string
  `message` exactly matching the fixture-pinned absence message (currently
  `Branch not protected`; re-pinned by each validation run).
- Projection fields: `branch`, `enforce_admins`,
  `required_pull_request_reviews` (`required_approving_review_count`,
  `require_code_owner_reviews`, `dismiss_stale_reviews`),
  `required_status_checks` (`strict`, `contexts_count`),
  `required_linear_history`, `required_conversation_resolution`,
  `required_signatures`, `allow_force_pushes`, `allow_deletions`; undetermined
  values are `unknown`.

### repository-rulesets

Observes the inventory of rulesets defined on the repository — the listing's
summary information only. It makes no claim about rule contents, conditions,
bypass actors, or effective enforcement. Organization-owned rulesets are a
different resource and are excluded by descriptor coherence: the request
explicitly excludes parent rulesets (`includes_parents=false`; exact parameter
behavior pinned by the validation run). An empty listing is `collected` with
`count: 0` — emptiness is a value, never `absent`.

- Request: paginated listing drain of `GET /repos/{full_name}/rulesets`,
  `per_page=100`; no required per-repository input.
- Shape: object array. Projection: `count` plus `{id, name, target,
  enforcement, created_at}` per ruleset, sorted by ruleset `id`.
- Per-ruleset detail is deferred — the designated first multi-request
  descriptor candidate (ADR-0004).

## Collection model

1. Org-scoped stage unchanged (`/user`, `/meta`, `/orgs/{org}`, inventory
   drain).
2. Target discovery per ADR-0005's canonical rule, shared verbatim by
   collection planning and offline rederivation (equivalence-tested).
3. Iteration: sequential, repositories ascending by `id`, descriptors in table
   order.
4. Execution through the existing transport (ADR-0007 waits). Envelopes gain
   `repo` (`{id, full_name}`), `resource` (descriptor name), `branch` where
   applicable, and the existing page fields for list resources.
5. A target missing a descriptor's required input receives no request and no
   fabricated artifact for that descriptor; it derives `unknown` with reason
   `missing-required-input`. Other descriptors still observe it.
6. Failures on one repo-resource never stop the run; the run frame is never
   re-evaluated during fan-out. Filesystem path-creation failures are recorded
   collection failures, not crashes.

**Collection-failure recording (ratified clarification, E1, 2026-07-27):** in
item 6, "recorded collection failures, not crashes" means the failure is
surfaced loudly at run time and collection continues with later work; no
synthetic or fabricated raw-evidence artifact is created; the expected
artifact remains absent, and that absence is the durable repository trace,
from which T6 may derive `unknown`. This clarifies the existing layout and
evidence rules; it is not a new failure-artifact design.

**Required-input usability (ratified refinement, E1, 2026-07-26):** a required
descriptor input is usable only when it is a non-empty string; `None`, empty
strings, and non-string values are missing. Degenerate values are never
coerced, repaired, or used to fabricate request paths.

**Envelope transport-evidence retention (ratified refinement, E1, 2026-07-29):**
raw collection envelopes may retain two additional allowlisted
transport-evidence fields. The refinement is additive and exists solely to make
V30's report visibility derivable from retained evidence; it preserves V40
compatibility and token secrecy, and introduces no new taxonomy semantics —
the derived-entry closed reason set and the E1-Q3 transport-termination
mapping are unchanged.

1. `wait_records` — the already-ratified closed 10-field wait-record schema,
   preserved exactly in the order transport produced the records; the records'
   `rate_limit_headers` never exceed the existing response-header allowlist.
   Absent in pre-refinement evidence trees and read as an empty list.
2. `termination_reason` — the structured transport result's wait-bound
   termination reason, retained only when one exists; never synthesized for
   successful completion. Readers treat legacy absence and an explicit null
   equivalently.

## Artifact layout

```
<out>/
  evidence/raw/<run-id>/
    meta.json  user.json  org.json  repos.page-<n>.json      # unchanged
    repos/<repo-id>[-<name-annotation>]/
      default-branch-protection.json
      repository-rulesets.page-<n>.json
  observed/
    org.json  repositories.json                              # unchanged
    default-branch-protection.json                           # latest-only
    repository-rulesets.json                                 # latest-only
  reports/<run-id>.json  <run-id>.md
```

Annotation-safety rule (scanner-defined, deliberately conservative — not
asserted as GitHub's contract): include `-<name>` verbatim only when the name
matches `^[A-Za-z0-9_.-]{1,100}$` and does not end with `.`; otherwise the
directory is `<repo-id>` alone. Maximum assumed annotation length: 100.
Operators should prefer a shallow `--out` and enable long-path support on
Windows; portability of arbitrary output roots is not guaranteed.

**Unrecognized-directory reporting (ratified refinement, E1, 2026-07-26):**
directory names the scanner could not have written are surfaced through
`unrecognized_directories` reporting. This is reporting, never a third
structural-conflict class: ADR-0005's conflict classes remain limited to
(1) duplicate-ID directories and (2) path/envelope repository-ID
disagreement. T6 inherits this distinction.

Observed per-resource files: top level `{run_id, state, coverage, repositories}`.
`coverage` = `{"basis": "eligible-discovered-repositories", "inventory_state":
<inventory listing state>, "eligible_target_count": <n>}` — it qualifies the
target set and never converts descriptor states. `repositories` entries:
`{id, full_name, state, reason, ...projected fields}`, sorted by `id`.
Serialization rules unchanged: UTF-8, LF, sorted keys, envelope timestamps only.

## Taxonomy application and reasons

Per ADR-0006. Canonical deterministic reasons (closed set for this slice):
`collected`, `absence-message-matched`, `absence-rule-unmatched-404`,
`authorization-denied` (explicit 401/403), `shape-invalid`, `transport-failed`,
`pagination-cap`, `missing-required-input`, `structural-conflict`,
`rate_limit_reset_exceeds_maximum_park`, `retry-after-exceeds-maximum`,
`unusable-rate-limit-reset`. Every derived repo-resource entry carries exactly
one. No composite per-repository state exists; a per-resource-type rollup uses
the Slice 1 listing rule (first non-`collected` state encountered).

**Derivation-evidence refinements (ratified, E1, 2026-07-29):** three
clarifications for derived repo-resource entries. (1) The closed reason set
gains `raw-evidence-absent`, carried exactly and only when a target's required
inputs are present but the expected raw-evidence artifact is absent (the
recorded-collection-failure trace; every entry when deriving a Slice-1 tree);
the exactly-one-reason invariant is unchanged. (2) Structural evidence
conflicts (ADR-0005) derive `unknown` · `structural-conflict`: `unknown`
covers both insufficient trustworthy evidence and mutually conflicting
evidence that prevents selecting a valid observation; `structural-conflict`
remains limited to evidence-integrity conflicts. (3) Transport termination
maps to derived classification deterministically from retained evidence only
(envelope status, allowlisted rate-limit headers, `captured_at`): a final
record carrying affirmative rate-limit markers (status 429, or 403 with a
`retry-after` header or `x-ratelimit-remaining` of zero) derives `failed` with
reason `retry-after-exceeds-maximum` when Retry-After is parseable and exceeds
its maximum, else `rate_limit_reset_exceeds_maximum_park` when remaining is
zero with a parseable reset whose computed park (`max(0, reset −
captured_at_epoch) + slack`) exceeds the maximum park, else
`unusable-rate-limit-reset` when remaining is zero with a missing or
unparseable reset, else `transport-failed` (markers within bounds: attempts or
renewed-exhaustion terminated). Markerless 401/403 remain `inaccessible` ·
`authorization-denied`; other non-2xx transport outcomes remain `failed` ·
`transport-failed`.

## Transport and waits

Per ADR-0007. Slice 2 constants (proposed values — owner review):
`MAX_ATTEMPTS = 3` (unchanged), Retry-After maximum 60 s (unchanged), primary
park slack 5 s, maximum primary park 3900 s. Report visibility, derived from
retained evidence only: planned logical requests; actual attempts; completed
and failed logical requests; primary-park count and seconds; Retry-After wait
count and seconds; other retry-wait count and seconds; maximum single wait;
first and last capture timestamps; wait-bound termination counts and reasons.

**Wait-termination evidence vocabulary (ratified refinement, E1, 2026-07-26):**
a parked logical request that again affirmatively reports primary exhaustion
terminates with structured-result `termination_reason`
`rate_limit_renewed_exhaustion` and primary-park wait-record `outcome`
`renewed-exhaustion`. Both tokens are transport wait-evidence vocabulary only;
neither joins the derived-entry closed reason set. T6 remains responsible for
mapping transport termination into derived-entry classification.

## Module structure

| Module | Owns | Must not |
|---|---|---|
| `resources.py` | Descriptor table: names, path templates, shapes, required inputs, absence anchors, projection specs (predominantly declarative) | Discovery, transport, taxonomy execution, persistence, aggregation |
| `targets.py` | Canonical discovery rule; evidence addressing (directory keys, annotation safety, structural validation) — separate sections/APIs | Let annotation affect eligibility or identity |
| `taxonomy.py` | Classification, absence matching, deterministic reasons | Read directories, execute requests, write projections, aggregate |
| `transport.py` | Attempts, precedence, bounded waits, wait records, structured results | Assign taxonomy states |
| `collect.py` | Orchestration only: inventory → targets → descriptors → transport → raw persistence | Derive, aggregate, reimplement shared rules |
| `derive.py` | Evidence loading, structural validation invocation, classification invocation, projections, coverage, summary | Network, wall clock |
| `report.py` | Report assembly from derived facts | Reinterpret raw responses; bypass evidence validation |

Approved conditional splits (perform before continuing when a file reaches
~280 lines, independent testability degrades, or unrelated mechanics
accumulate; never cross 300 without the exception process): `targets.py` →
`targets.py` + `evidence_paths.py`; `derive.py` → `derive.py`/`projections.py`
+ `summary.py`. Line estimates are planning evidence, not acceptance criteria.
Tests are planned by behavioral domain — at minimum `test_targets.py`,
`test_taxonomy.py`, `test_resources.py`, `test_transport_waits.py`, plus scoped
growth of the existing modules and `fake_github.py` — under the same 300-line
directive, split by contract and scenario domain.

## Validation

The normative matrix (companion file) is binding: every scenario carries its
mode (live / offline / both / conditional), fixture, credential profile,
expected response class, raw evidence, taxonomy state, deterministic reason,
projection, report effect, and status. A successful live run is never evidence
for offline-only rows.

**Live-run classes and evidence authority (ratified clarification,
2026-07-29):** two live run classes exist: the validation run (T9) and
reconnaissance runs — owner-authorized, bounded, read-only, executed from
merged `main` at a pinned SHA, under the same credential discipline as the
validation run (documentation-first provisioning; no silent credential-type
substitution, no permission broadening, and no reduction of required
validation coverage; divergences recorded). Matrix-row acceptance occurs only
at the T9 validation run; no earlier evidence, live or committed, accepts any
row. All pinning of live-observed values — the absence message ("re-pinned by
each validation run"), parameter behavior ("pinned by the validation run"),
and response classes ("pinned by run", V03) — is validation-run authority
exclusively; reconnaissance runs never pin or re-pin, and any observed
divergence from a pinned value routes through halt-don't-decide to
owner-ratified review per ADR-0006's taxonomy-classification-change rule.
Every committed run record declares its grade (`reconnaissance` or
`validation`); reconnaissance records carry the non-acceptance statement
inline, including any credential observations they record.

**Fixtures (GHScannerLab; owner-provisioned before the run; scanner is
read-only):** `standard-repo` (protected default branch: one required approving
review; one repository-owned ruleset), `unprotected-repo` (new; active, has
commits, no protection — the canonical absence pin), `empty-repo` (new; no
commits — distinct response class, never auto-joining the absence set),
`archived-repo` and fork `Hello-World` (compatibility corroboration only —
disagreement is real evidence requiring review), all non-`standard-repo` repos
(empty rulesets listings). One organization-owned ruleset when the plan
permits (conditional parent-exclusion behavioral validation).

**Credentials (documentation-first):** standing validation PAT — fine-grained,
read-only, scoped to GHScannerLab; documented permissions: repository
Administration: read (protection), Metadata: read (rulesets). Record
separately: documented permissions, configured permissions, repository access,
live observed outcomes, divergences. No claim of a universally minimal set. If
a documented configuration cannot access a required endpoint: stop that path,
retain safe evidence, record the divergence, request an owner decision — never
silently substitute a classic PAT, broaden permissions, or reduce scope. A
second restricted PAT (Metadata access, intentionally lacking Administration:
read) is required when safely provisionable, used only to pin live
insufficient-authorization behavior; otherwise the live denial scenario is an
explicit recorded validation gap and offline tests carry it. No token values,
authorization headers, or reusable credential material are ever committed.

**Parent exclusion:** mandatory request-contract validation (raw evidence
proves `includes_parents=false`; offline tests prove only repository-owned
summaries project) plus conditional behavioral validation (pre-provisioned org
ruleset excluded from the projection, verified against known fixture state).
If the plan prevents provisioning, record the limitation in
`docs/validation/validation-environment.md`, mark behavioral exclusion
conditionally unvalidated, and revisit via wayfinder tickets #2/#3.

## Tasks (dependency order; each red-first TDD, existing tests never regress, diff scoped to the task)

- **T1 — `resources.py`:** descriptor table structure + `default-branch-protection`
  entry + projection. AC: table integrity; projection of known bodies yields the
  exact field set with `unknown` for missing values.
- **T2 — `taxonomy.py`:** extraction from `derive.py`; descriptor-anchored
  classification + reasons. AC: matrix rows V13–V20; all existing
  classification behavior preserved.
- **T3 — `transport.py` waits:** ADR-0007 precedence, park, wait records.
  AC: matrix rows V21–V29 (fake clock).
- **T4 — `targets.py`:** canonical discovery + addressing + structural
  validation. AC: rows V31–V36, V38.
- **T5 — Fan-out collection (`default-branch-protection`):** layout, envelope
  extensions, missing-input rule, token-secrecy scan over new artifacts.
  AC: scaffold exactness; orderly continuation; V33.
- **T6 — Derivation:** per-resource projections, coverage blocks, summary
  generalization. AC: byte-identical offline derive; V39–V40.
- **T7 — Report:** aggregates + wait visibility. AC: V30; report size
  independent of estate size (failures excepted).
- **T8 — `repository-rulesets`:** second descriptor. **Architectural AC: the
  diff touches only `resources.py`, tests, and fixtures** — zero changes to
  `collect.py`, `derive.py` engine code, `targets.py`, `taxonomy.py`,
  `transport.py`, `report.py`; failure returns the design to review. Functional
  AC: V06–V07, V11, V37. **Test-plan notes (carried from the T5 Quality Gate,
  2026-07-29; planning notes, not T5 defects):** (1) dedicated coexistence
  coverage for multiple descriptors on a repository missing one descriptor's
  required input; (2) an explicit object-envelope assertion that list-only
  fields are absent.
- **T9 — Fixtures + live validation run:** owner provisions fixtures and PATs
  per this spec; run `collect` + `derive`; commit the self-contained tree under
  `docs/validation/runs/`; update `validation-environment.md` (inventory,
  credential record, any gaps) in the same change set. AC: rows V01–V12 as
  marked; token scan clean; committed tree re-derives byte-identically.
- **T10 — Slice completion:** independent quality gate, /code-review
  (Standards + Spec + conformance), owner merge, Status reconciliation, and the
  post-slice gate sequencing (consolidation → domain model) per the accepted
  methodology.

## Non-goals

Compliance evaluation or any judgment of collected configuration; organization-
and enterprise-scoped rulesets and settings; plan-gated GHAS endpoints (await
tickets #2/#3); GraphQL; concurrency; write operations; dashboards, databases,
scheduling, governance products (ADR-0001).

## Deferred and tracked future work

Binding deferrals live in their governing ADRs (0004: hierarchy, multi-request;
0006: per-repository `unsupported`; 0007: budgets, pacing, resume, CLI
controls). Tracker issues created at acceptance closeout — each stating its
governing reference, deferral reason, reopening trigger, and boundary against
premature implementation: (1) Observation Target Model consideration
(generalization beyond repositories, evaluated at post-Slice-2 consolidation);
(2) `security_and_analysis` projection — the current repository inventory
collection includes the `security_and_analysis` object when present; future
projection opportunity, no new collection; (3) per-ruleset detail — designated
first multi-request descriptor candidate.
