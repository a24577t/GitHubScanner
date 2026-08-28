# Slice 3 Architecture Consolidation — Record

**Type:** consolidation record (the binding post-slice architecture gate for
Vertical Slice 3 — Secret Scanning Control Family). Owner-authorized
2026-08-28; **preparation only — no repository authority changes until owner
review and acceptance.** Input set: the complete T1–T7 consolidation inputs
enumerated in STATUS's T7 completed-work entry, plus retrospective-audit
findings F1–F3. Base: merged main `6cea6f9`; regression baseline 347/347
(Python 3.12.10). All existing ADRs and MADRs retain their accepted status
unchanged; nothing here edits an accepted decision in place.

## 1. Architecture consistency review

Artifacts reviewed: ADR-0001..0009, MADR-0001..0004, the Slice 3
specification and validation matrix, `CONTEXT.md`, the Security Controls
roadmap, the two committed Slice 3 validation records, and STATUS.

- **Consistent:** ADR-0008's five-plane model ↔ ADR-0009's three-element
  realization ↔ the accepted Slice 3 specification ↔ `CONTEXT.md`'s
  scope-constrained glossary ↔ the shipped `controls.py` vocabulary. The
  Slice 3 subset exclusions (`unavailable`, `not-applicable`, the
  configuration triple) trace to grill condition 2 and ADR-0009's deferrals;
  the roadmap already records that the accepted specification supersedes its
  planning leads for Slice 3. No contradiction, duplicated concept, or
  terminology drift found between accepted decision artifacts.
- **Resolved here (planning staleness):** the roadmap's *Current capability*
  / *Current limitation* / roadmap-table rows predate Slice 3 completion
  (218-test suite, "secret scanning … not observed", SS/PP rows at
  "Specification accepted"). Updated in this change set to the completed
  state — planning artifact refresh, no decision content changed.
- **Resolved here (matrix editorial, T7 finding 1 / audit-confirmed):**
  matrix row V52's Expected column lists only the visibility-kind
  applicability outcome; the chained control's deterministic outcome under
  the same evidence is `applicability-unknown` · `secret-scanning-availability-unknown`
  (spec chain rule 3; both pinned in-suite). An append-only editorial
  clarification is added to the matrix. The specification governs; the
  implementation already follows it — no behavior implicated.
- **Recorded reconciliation (T4 carry — owner-clarified product objective
  vs ADR-0001):** the clarified objective — *corporate security standard →
  expected repository control state → observed repository control state →
  conformance determination → actionable gap* — is exactly ADR-0008's
  five-plane derivation: deterministic evaluation over committed evidence
  and committed policy artifacts. ADR-0001's rejected alternative was a
  hosted governance *product/service* in place of the deterministic CLI;
  ADR-0008's boundary paragraph already records that it "does not reopen
  ADR-0001's rejection of a governance product." **No conflict exists and
  no ADR edit is needed**; the objective is realizable entirely inside the
  accepted architecture once the policy-definition decision (§7) is made.

## 2. ADR / MADR review

ADRs 0001–0009 and MADRs 0001–0004: purposes, dependencies, and terminology
re-verified against the glossary and each other; no superseded statements,
no overlaps, no status changes — all remain **accepted**, none edited. One
clarification affecting MADR-0004's reading is preserved solely as input to
a separate owner-governed methodology refinement decision: see F1 in §5.

## 3. Domain model (`CONTEXT.md`)

Reviewed; consistent with the implemented slice. Every term (`Security
Control`, `Observation`, `Applicability`, `Applicability Chain`,
`Operational State`, `Resource Descriptor`) now has a shipped, test-pinned
realization; the Applicability Chain definition matches the implemented
chain exactly (availability, never enablement, never collapsed). No new
concepts introduced; no edit required; the owner-directed scope constraint
(ADR-0008 domain concepts only) remains honored.

## 4. Glossary review

One definition per term; avoid-lists intact; ADR/spec usage consistent.
Audit finding F2 (dual work-item granularity — tickets vs slice — in
STATUS/lifecycle usage) is a *methodology* vocabulary note, outside
`CONTEXT.md`'s product-domain scope; routed in §5.

## 5. Methodology / process items — routed separately (no methodology text changed here)

These are recommendations for owner-gated methodology mechanisms; this
record proposes text but changes nothing:

- **F1 (audit; methodology-refinement input — no MADR edit or append
  proposed here):** for the limit case where the reconciliation change set
  *is* the Status Artifact, MADR-0004's authority-ordering sentence reads in
  tension with its canonical-location clause. This record changes and
  proposes to change nothing in MADR-0004; the drafted clarification below
  is preserved solely as **input to a separate owner-governed methodology
  refinement decision**, to be taken (or declined) through the methodology's
  own mechanisms at the owner's cadence: *"Where a zero-diff gate's
  reconciliation change set is itself the Status Artifact, the finding
  record it carries is the committed finding record; the authority-ordering
  rule bars STATUS summaries from substituting for that record, not the
  record from residing there."*
- **F2 (audit; editorial to the lifecycle model's evolvable decomposition
  topology):** one sentence acknowledging slice-internal ticket-set usage of
  the Milestone-Complete predicate alongside the phase-level definition —
  or a glossary line distinguishing *work item (slice)* from *ticket*.
  Owner decision; no urgency (both usages are true under established
  repository usage).
- **F3 (audit; process):** for future verification-only tickets, one
  owner-authored PR comment at each acceptance event would give S8/S11
  acceptances a trace independent of the artifacts they accept. Adoption is
  the owner's call; no artifact change proposed.
- **MO-001 / MO-002 (methodology-validation observations):** recorded,
  unadjudicated. Adjudication is human-owned (validation charter); they
  await an owner-cadence MVR review and are **not** dispositioned by this
  record.

## 6. Carry-forward dispositions (complete input set)

"Ticket D" is the proposed test-infrastructure issue defined in §8 —
tracked work, authorized by nothing in this record. Existing tickets #59
(traversal unification), #60 (closed-vocabulary ownership), #61 (offline
report regeneration) are the Slice 2 closeout issues; scope additions below
are proposed as cross-reference comments at acceptance.

| # | Input (source) | Class | Disposition |
|---|---|---|---|
| T1-1 | Exact-count sweep recommendation (STATUS T1) | Implementation/test | **Ticket D** scope. |
| T1-2 | Spec-text editorial aside (STATUS T1; content in the T1 S10 record, PR #77) | Editorial | Disposition-preserved; content recoverable from the PR #77 footprint (MADR-0004 Class II, pre-dating its acceptance-forward scope). No excavation; no action. |
| T2-1 | `_NAME` regex duplication / validation-pattern harmonization (incl. `validate_controls`/`validate_table` parallelism; Standards-axis confirmation at T7) | Implementation | **#60** scope addition (vocabulary/validation ownership). |
| T2-2 | Name-derived chain-reason note for any future second chain | Product architecture (local design, stands) | Recorded; travels with **#60**'s reason-vocabulary reification — a second chain target must revisit literal ownership before shipping. |
| T3-1 | Stale `observed/controls/` document parity (control removal mirrors descriptor-removal semantics) | Implementation | Stands as settled practice; recorded, no action. |
| T4-1 | `derive.py` document-assembly duplication (`run_summary` vs `derive_observed`) | Implementation | **#59** scope addition (traversal/assembly unification). |
| T4-2 | Reason-vocabulary reification | Implementation | Stands with **#60** (already its subject). |
| T4-3 | Markdown `assertIn` membership-assertion editorial | Implementation/test | **Ticket D** scope. |
| T4-4 | Owner-clarified product objective → policy-definition input; ADR-0001 phrasing reconciliation | Product architecture | Reconciliation **recorded in §1**; objective feeds the §7 decision surface. No ADR edit. |
| T5-1 | `mixed_estate` docstring imprecision | Implementation/test | **Ticket D** scope. |
| T5-2 | Windows MAX_PATH sensitivity of committed validation trees | Environment/doc | **Resolved here** — operational note added to `validation-environment.md`. |
| T6-1 | Optional V45 rejection-probe strengthening | Product architecture (Architecture Proposal, optional) | Presented for owner decision; recommendation: **decline for now** — record as an available strengthening at any future validation run; the accepted matrix wording is satisfied. No artifact change. |
| T6-2 | Derive/report offline-regeneration cleanup | Implementation | Stands with **#61** (already its subject). |
| T6-3 | Raw `permissions` blocks + ~175 KB `/meta` payload | Product architecture (accepted by design) | Stands under ADR-0001 verbatim retention; per-run growth noted; no action. |
| T7-1 | V52 Expected-column editorial | Editorial (spec artifact) | **Resolved here** — append-only matrix clarification. |
| T7-2 | Fake-server/socket/subprocess flake class + `test_derive.py:49` missing-stderr diagnostic | Implementation/test | **Ticket D** (primary scope). |
| T7-3 | Bucket-increment idiom duplication (`derive._fanout_summary` / `summary._plane`) | Implementation | **#59** scope addition (with T4-1). |
| S-1 | Cross-evidence-shape additivity proof assignment | Product architecture | Stands — assigned to the next implemented roadmap control's slice (grill condition 1; ADR-0009); restated in the refreshed roadmap. |
| S-2 | #26 Observation Target Model deferral | Product architecture | Stands — decision at the first org-scoped-target slice. |
| S-3 | Cleanup tickets #59/#60/#61 | Implementation | Stand open, owner-scheduled only; scope-addition comments proposed in §8. |
| S-4 | #62 roadmap tracking | Planning | Stands; Slice 3 completion cross-reference proposed in §8. |
| F1–F3 | Retrospective-audit findings | Methodology/process | Routed in §5; no product-architecture impact. |

Every input above is dispositioned; none authorizes work in this change set
beyond the three "Resolved here" documentation edits.

## 7. Policy-definition decision surface (owner judgment — no decision made here)

ADR-0008 makes a policy artifact class the prerequisite for every control's
Policy Expectation and Conformance planes. The surface, per its three
accepted expectation tokens:

- **A — Committed policy artifact class (in-repo declarative policy):**
  repository-class → expected control states; deterministic evaluation over
  committed policy + committed evidence. Fully realizes
  `explicit-requirement`; honors ADR-0001's boundary. Requires a decision
  phase (grill) for the artifact class shape: per-control vs per-class
  layering, scoping/matching rules, precedence, and where policy lives
  (this repository vs a consumer-owned repository — disposability and
  product-boundary question).
- **B — Observed platform configuration as expectation source:**
  organization security configurations realize
  `inherited-organization-expectation` with no new artifact class — but is
  blocked on #26 and the org-configuration control, and covers only what
  the platform expresses; a corporate standard beyond platform features
  still needs A.
- **C — Hybrid (A + B, staged):** `explicit-requirement` from committed
  artifacts, `inherited-organization-expectation` from observed
  configuration where available, `no-expectation-defined` as the default —
  the shape ADR-0008's vocabulary already anticipates. A can ship first; B
  joins after #26.
- **D — Defer further:** continue observation-side slices (Dependency
  Graph, Dependabot pair, Security Policy need no policy decision); the
  clarified product objective's conformance half stays unrealized
  meanwhile.

**Tradeoff for the owner:** A/C opens the decision phase now and unlocks the
clarified end-to-end objective on already-shipped controls; D maximizes
near-term observation coverage first. B alone under-delivers the corporate
standard. No alternative is selected here.

## 8. Proposed closeout actions (texts; executed only at owner acceptance)

- **#59 comment:** add scope — `derive.py` document-assembly duplication
  between `run_summary` and `derive_observed` (T4 carry) and the shared
  bucket-increment counting idiom (`derive._fanout_summary`,
  `summary._plane`; T7 carry).
- **#60 comment:** add scope — `_NAME` regex and table-validation pattern
  harmonization (`resources.validate_table` / `controls.validate_controls`,
  T2 carry); chain-reason literal ownership note for any future second
  chain target (T2 carry).
- **#62 comment:** record Slice 3 complete (SS + PP implemented; canonical
  ADR-0009 pattern proven same-surface; cross-shape proof assigned to the
  next implemented control's slice).
- **Ticket D (new) — Test-infrastructure hardening (validation-only, no
  production change):** harden the fake-server/subprocess tests against
  load-induced socket flakes (observed in `test_taxonomy`,
  `test_derive.py::TokenSecrecy`, `test_collect_fanout.py::test_envelope_extensions…`);
  add `result.stderr` to the bare returncode assert (`test_derive.py:49`);
  correct the `mixed_estate` docstring's V50–V56 claim; strengthen the
  Markdown-preservation membership assertions (T4 editorial); add the
  exact-count sweep (T1). Normal S6→S7 path, owner-scheduled only.

## 9. This change set's review findings (MADR-0004)

Owner final review of the prepared package (⟦G-Accept⟧ review, 2026-08-28)
surfaced two findings; both were resolved in the prepared package before
adjudication. Provenance for both: gate — Slice 3 Architecture
Consolidation; work item — this consolidation change set; revision — the
prepared (pre-commit) package on `feat/slice-3-architecture-consolidation`
over base `6cea6f9`, corrected in place 2026-08-28.

| # | Classification | Finding (statement) | Evidence | Disposition |
|---|---|---|---|---|
| C1 | Repository Inconsistency (within the change set) | The refreshed roadmap declared Slice 3 complete while its own Sequencing guidance still listed Secret Scanning and Push Protection as near-term candidates — the same document simultaneously presenting both controls as implemented and as future candidates. | `docs/planning/security-controls.md`: the prepared *Current capability* / roadmap-table edits ("Implemented (Slice 3 complete)") versus the untouched "near-term candidates — Secret Scanning, Push Protection, …" sentence. | Fixed in the prepared package — both controls removed from the candidate list with an explicit implemented-no-longer-candidates clause; remaining candidate ordering preserved. |
| C2 | Repository Inconsistency (within the change set) | The record's F1 item recommended a clarifying append to accepted MADR-0004, contradicting this consolidation's own boundary (all ADRs/MADRs preserved as accepted; nothing edited or appended in place) and pre-empting the owner-governed methodology mechanism. | `docs/consolidation/slice-3-architecture-consolidation.md` §5 F1 as first prepared ("Recommended clarifying append … MADR-0002 append-only model") and the aligned §2 sentence ("recommended … against MADR-0004"), versus the authorization's boundary. | Fixed in the prepared package — F1 rerouted: the record changes and proposes to change nothing in MADR-0004; the drafted clarification text is preserved solely as input to a separate owner-governed methodology refinement decision; §2 aligned. |

Any further findings from the remaining review chain append here at their
adjudication.

## 10. Gate outcome

Prepared on `feat/slice-3-architecture-consolidation` (working tree only —
no commit, no push, no PR, per the preparation-only authorization).
Authority changes only at owner review and acceptance (⟦G-Accept⟧). STATUS
reconciliation, closeout actions, next-slice selection, the
policy-definition decision, and any phase-gate/baseline consideration all
remain owner decisions after acceptance.
