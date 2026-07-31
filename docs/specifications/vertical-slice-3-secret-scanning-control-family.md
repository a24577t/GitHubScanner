# Vertical Slice 3 — Secret Scanning Control Family

**Status:** approved (architecture grill verdict PASS WITH CONDITIONS,
owner-approved at ⟦G-Verdict⟧ 2026-07-30 as Decision S4-SLICE3-01; accepted
at ⟦G-Accept⟧ via the Slice 3 acceptance PR). Governing decisions:
[ADR-0001](../adr/0001-collector-architecture-three-evidence-layers.md),
[ADR-0002](../adr/0002-evidence-state-taxonomy.md),
[ADR-0003](../adr/0003-explicit-environment-targeting.md),
[ADR-0004](../adr/0004-repository-resource-observation-model.md),
[ADR-0005](../adr/0005-target-discovery-evidence-addressing.md),
[ADR-0006](../adr/0006-taxonomy-evidence-rules.md),
[ADR-0007](../adr/0007-bounded-execution-waits.md),
[ADR-0008](../adr/0008-security-control-model.md),
[ADR-0009](../adr/0009-security-control-realization.md) (proposed with this
specification). Grill input package:
[slice-3-architecture-grill.md](../planning/slice-3-architecture-grill.md).
Normative validation matrix:
[vertical-slice-3-validation-matrix.md](vertical-slice-3-validation-matrix.md).

## Purpose

Realize the first two Security Controls under ADR-0008 — **Secret Scanning**
(the canonical control realization) and **Secret Scanning Push Protection**
(the additivity-proof control) — as one bounded slice covering the
observation-side planes only: Observation, Applicability, Operational State.
Strict implementation ordering inside the slice: Secret Scanning first; Push
Protection only after the pattern is gate-validated. Every Slice 1–2 invariant
is preserved: verbatim append-only raw evidence, byte-identical offline
derivation, one taxonomy state per targeted resource, affirmative absence,
token secrecy, partial evidence as evidence.

## Grill conditions (binding; owner-imposed at ⟦G-Verdict⟧, 2026-07-30)

1. **Same-evidence-surface limit of the additivity proof.** T5's architectural
   acceptance criterion proves control-pattern additivity on a *shared*
   evidence surface only; the cross-evidence-shape proof is explicitly
   assigned to the next roadmap control's slice and is not claimed here.
2. **`unavailable` excluded.** Neither control may derive Operational State
   `unavailable` in this slice; admission requires a future affirmative
   discriminator (wayfinder #2/#3 facts) as an append-only reviewed
   refinement. Field absence and plan ambiguity degrade to `unknown` /
   `applicability-unknown`, never to a definite conclusion.
3. **Issue #27 disposition at acceptance closeout.** Its reopening trigger
   (Slice 3 scoping) has fired; the owner disposes it (close or re-scope) at
   closeout, recording the dedicated-request decision and the rejection of
   projection-only realization.
4. **Canonical realization.** The control-definition layer, control-observation
   document class, and dedicated-request evidence realization specified here
   are the canonical ADR-0008 realization pattern (ADR-0009); the six
   remaining roadmap controls imitate it.
5. **Validation partition preserved.** The matrix keeps the grill's
   unconditional / conditional / optional partition with V10/V12 recorded-gap
   mechanics; the 2026-08-28 trial-route expiry is scheduling input only,
   never a slice dependency.

**Factual correction (owner-directed at ⟦G-Verdict⟧):** no enablement
operation has ever occurred on any fixture — retained evidence
(run `20260730T162522Z`) shows only affirmative `disabled` values. Public-fixture
enablement of both controls is therefore a **mandatory provisioning-time
validation obligation** (rows V44–V46), not a confirmed fact.

## CLI contract

Unchanged from Slice 2. The new descriptor participates in the existing
fan-out; `--max-pages` semantics are unaffected (the descriptor is a
single-object request).

## Resource descriptor

### security-and-analysis

Observes only the repository metadata object's `visibility` field and
`security_and_analysis` surface as returned for the repository itself. It
makes no claim about any other repository metadata, no claim about
organization security configuration, and no claim about scanning activity,
alerts, or findings. Emptiness or absence of the `security_and_analysis`
object in a collected body is undetermined data, never disablement
(ADR-0008: absence of evidence is never evidence of disablement).

- Request: `GET /repos/{full_name}`; no required per-repository input.
- Shape: object. No absence anchor (`absence_message: None`): a discovered
  repository's metadata object has no affirmative-absence class; a 404
  derives `inaccessible` · `absence-rule-unmatched-404` per ADR-0006.
- Projection fields: `visibility`; `security_and_analysis` →
  `secret_scanning` (`status`), `secret_scanning_push_protection`
  (`status`). Undetermined values are `unknown`. The projection carries both
  controls' status fields from T1 so that T5 adds no descriptor change
  (condition 1's shared surface, designed once).
- The response surface visible under the standing credential is unpinned by
  any prior run (Slices 1–2 never issued this request); the validation run
  pins it (row V42) before any matrix row is accepted.

## Control definitions (ADR-0009 layer)

Controls are reviewed in-code declarative data in `controls.py`, validated at
import time exactly as the descriptor table is. Each control declares: `name`,
`descriptor` (the evidence descriptor it consumes), the projected status
field path it reads, and its applicability rule. Controls consume the
descriptor's derived resource-document entries — never raw evidence, never
the network.

### secret-scanning

Reads `security_and_analysis.secret_scanning.status` from the projected
entry.

### secret-scanning-push-protection

Reads `security_and_analysis.secret_scanning_push_protection.status`.
Applicability chains on secret-scanning availability (below). Added only in
T5, under the architectural acceptance criterion.

## Control-plane rules (closed vocabularies; exactly one state and one reason per plane per entry)

Evaluation is deterministic, first match wins, over the descriptor entry for
the same target in the same run.

**Operational State** — subset pinned for both controls:
`{enabled, disabled, inaccessible, unknown}`. `configured`,
`not-configured`, `partially-configured` are unreachable (boolean-enablement
controls); `unavailable` is excluded per condition 2.

1. Entry state `collected`, status exactly `"enabled"` → `enabled` ·
   `affirmative-status-enabled`.
2. Entry state `collected`, status exactly `"disabled"` → `disabled` ·
   `affirmative-status-disabled`.
3. Entry state `collected`, any other status (field absent, non-string, or
   unrecognized value; never coerced) → `unknown` · `status-undetermined`.
   The absent/unrecognized distinction remains recoverable from raw
   evidence; the projected seam does not preserve it and the closed reason
   set deliberately does not split it.
4. Entry state `inaccessible` → `inaccessible` · `evidence-inaccessible`.
5. Any other entry state (`failed`, `unknown`, including
   `raw-evidence-absent` and `structural-conflict` trees) → `unknown` ·
   `evidence-unavailable`.

**Applicability** — subset pinned for both controls:
`{applicable, applicability-unknown}`. `not-applicable` is unreachable this
slice: no affirmative inapplicability evidence exists for these controls.

`secret-scanning`:

1. Entry `collected`, own status `"enabled"` → `applicable` ·
   `affirmative-enabled-status` (an affirmatively enabled control
   self-evidences applicability; deliberately asymmetric — `"disabled"`
   establishes nothing about applicability).
2. Entry `collected`, `visibility` exactly `"public"` → `applicable` ·
   `public-repository-visibility` (rests on the platform availability fact
   proven affirmatively by the mandatory enablement obligation, row V44).
3. Entry `collected`, `visibility` in `{"private", "internal"}` →
   `applicability-unknown` · `visibility-not-public` (plan-gated; #2/#3
   facts incomplete — never guess).
4. Entry `collected`, `visibility` otherwise undetermined →
   `applicability-unknown` · `visibility-undetermined`.
5. Entry not `collected` → `applicability-unknown` · `evidence-unavailable`.

`secret-scanning-push-protection` (the applicability chain, designed once):

1. Entry `collected`, own status `"enabled"` → `applicable` ·
   `affirmative-enabled-status`.
2. secret-scanning applicability for the same target is `applicable` →
   `applicable` · `secret-scanning-available` (chained on availability,
   never on enablement, and never collapsed into one boolean).
3. Otherwise → `applicability-unknown` ·
   `secret-scanning-availability-unknown`.

The planes are independent conclusions: Push Protection's Operational State
derives from its own field even where its applicability is unknown.

## Control-observation documents

One latest-only observed document per control:
`observed/controls/<control-name>.json` — a new document class; existing
resource documents remain byte-identical. Top level
`{run_id, state, coverage, repositories}` (the house shape):

- `run_id` — the derived run.
- `state` — the Slice 1 listing rule applied to the entries' **evidence**
  states (the cited descriptor-entry taxonomy states). This is the
  evidence-plane rollup only; no operational-state or applicability rollup
  exists anywhere (a collapse would encode a policy judgment — Conformance
  territory, out of scope).
- `coverage` — reused verbatim: `{"basis":
  "eligible-discovered-repositories", "inventory_state": <inventory listing
  state>, "eligible_target_count": <n>}`; qualifies, never converts.
- `repositories` — entries ascending by repository `id` (canonical discovery
  order): `{id, full_name, applicability, applicability_reason,
  operational_state, operational_state_reason, evidence}`.

**Evidence-citation form** (every conclusion cites retained evidence,
ADR-0008): the per-entry `evidence` object is
`{"resource": "security-and-analysis", "state": <taxonomy state>, "reason":
<deterministic reason>}` — naming the descriptor evidence the conclusions
derive from and its classification; with the document's `run_id` and
ADR-0005 evidence addressing this identifies the exact retained artifact.
Paths are never embedded (paths are never evidence).

Serialization rules unchanged: UTF-8, LF, sorted keys, envelope timestamps
only; byte-identical offline rederivation from raw evidence alone.

## Reporting

Per-control aggregates join the report, estate-independent: applicability
counts, applicability-reason counts, operational-state counts,
operational-state-reason counts (closed vocabularies only). No estate-level
operational state is rendered. Existing per-descriptor aggregates cover the
new descriptor through the generic engine. The Slice-2 tolerant reporting
scan's type-deep contract applies to every new aggregate input (T7 lesson).

## Module structure

| Module | Owns | Must not |
|---|---|---|
| `resources.py` | `security-and-analysis` descriptor + projection (declarative) | Control vocabulary, plane rules |
| `controls.py` (new) | Control-definition table; pure control-plane rule evaluation (applicability, operational state, closed reasons); import-time table validation | Network, filesystem, taxonomy execution, aggregation, report rendering |
| `derive.py` | Orchestrate control-document emission from resource-document entries | Re-read raw evidence for control planes; embed rules |
| `summary.py` | Per-control distribution aggregates (type-deep tolerant) | Plane rule evaluation |
| `report.py` | Control aggregate rendering | Reinterpret evidence or conclusions |

Approved conditional split (perform before continuing when a file reaches
~280 lines or unrelated mechanics accumulate; never cross 300 without the
exception process): control-document assembly out of `derive.py` →
`control_documents.py`. Tests planned by behavioral domain — at minimum
`test_controls.py`, `test_derive_controls.py`, `test_report_controls.py`,
plus scoped growth of existing modules and `fake_github.py`.

## Validation

The normative matrix (companion file) is binding; rows carry the
unconditional / conditional / optional partition (condition 5). Matrix-row
acceptance occurs only at the T6 validation run under the Slice 2 ratified
live-run-classes clarification (validation-run authority; reconnaissance
never pins). **Mandatory provisioning-time obligations** (owner-executed
before the run; the scanner remains read-only): enable Secret Scanning and
Push Protection on `standard-repo`; enable Secret Scanning alone on
`unprotected-repo` (push protection left disabled); all other fixtures remain
untouched as affirmative-`disabled` pins. The enablement operations
themselves are validation evidence: they prove public-repository,
Free-plan enablement capability affirmatively (the platform fact behind
applicability rule 2) and pin the coupled transition (push protection enable
requires secret scanning enabled). If any obligation proves impossible at
provisioning, that is a blocking architectural finding routed to the owner —
not a recorded gap — because applicability rule 2 rests on it.

**Credentials (documentation-first, unchanged discipline):** the standing
fine-grained validation PAT; documented permission expectation for this
descriptor: Metadata: read. The restricted PAT (V48) and a private-repository
fixture (V49) are conditional: provisioned when safely possible, otherwise
explicit recorded validation gaps carried exactly as V10/V12 were. The
2026-08-28 trial-route expiry is scheduling input only; no row depends on
GHAS surfaces.

## Tasks (dependency order; each red-first TDD, existing tests never regress, diff scoped to the task)

- **T1 — `security-and-analysis` descriptor:** table entry + projection (both
  status fields + visibility). AC: projection rows V50–V51 at the resources
  seam; existing observed/report outputs byte-identical; diff touches only
  `resources.py`, tests, fixtures (T8 precedent).
- **T2 — `controls.py` + secret-scanning:** control table, plane rules,
  closed vocabularies, import-time validation. AC: rows V43–V44 offline
  analogs, V47, V50–V54 at the controls seam.
- **T3 — control-observation documents:** emission, citations, coverage,
  evidence-plane rollup. AC: V53, V57, V58, V60 (byte-identical
  rederivation; Slice-1/2-tree compatibility: control entries derive
  `evidence-unavailable`, existing documents byte-stable).
- **T4 — report aggregates:** per-control distributions. AC: V59;
  estate-independence; type-deep tolerance.
- **T5 — `secret-scanning-push-protection`:** **architectural AC (condition
  1): the diff touches only the push-protection control definition in
  `controls.py`, tests, and fixtures — zero changes to `resources.py`,
  `derive.py`, `projections.py`, `summary.py`, `report.py`, or any other
  engine module; no new request. Failure returns the design to review. The
  criterion proves same-evidence-surface additivity only.** Functional AC:
  chain rows V55–V56; V45–V46 offline analogs.
- **T6 — fixtures + live validation run:** owner executes the provisioning
  obligations; run `collect` + `derive`; commit the self-contained tree under
  `docs/validation/runs/`; update `validation-environment.md` (fixture
  inventory, credential record, enablement-operation record, any gaps) in
  the same change set. AC: live rows V41–V49 as marked, V62; token scan
  clean; committed tree re-derives byte-identically.
- **T7 — slice completion:** S10 three-axis review, independent S11 Quality
  Gate, owner merge, STATUS reconciliation, post-slice consolidation inputs
  carried forward.

## Non-goals

Policy Expectation and Conformance planes (await the policy-definition
decision); organization-level security configuration (#26); all other
Security Controls; alert, secret, vulnerability, and malware inventory;
`unavailable` operational state (condition 2); `not-applicable`
applicability; GHAS trial surfaces; GraphQL; write operations beyond the
owner's out-of-band fixture provisioning.

## Deferred and tracked future work

Binding deferrals live in their governing decisions (ADR-0009: `unavailable`
discriminator, cross-shape additivity proof, `not-applicable` evidence rule).
At acceptance closeout: dispose issue #27 (condition 3); record the
cross-shape additivity assignment on the roadmap's next-control planning.
