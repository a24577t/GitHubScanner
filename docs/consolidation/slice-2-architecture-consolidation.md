# Slice 2 Architecture Consolidation — Record

**Type:** consolidation record (the binding post-slice architecture gate for
Vertical Slice 2). Owner-authorized 2026-07-30; input set: the accepted
Architecture Consolidation Review (themes A–G), the recorded T7/T8/T9
carry-forwards, the S10/S11 (T10) observations, and the owner-directed
Security Control requirement with its two accepted refinements (Security
Control as the first-class seam; enumerated control roadmap). Base:
merged main `0da2265`; regression baseline 218/218 (Python 3.12.10).

## Decisions ratified in this change set

- [ADR-0008 — Security Control architectural seam](../adr/0008-security-control-model.md)
  (product architecture; themes and owner direction, Refinement 1).
- [MADR-0004 — Canonical persistence model for review findings](../../.ai/repository/methodology/adr/0004-review-finding-persistence.md)
  (methodology; Theme G, architectural decision only — no implementation
  vehicle selected).
- Consequential: Review Discipline gains its finding-persistence clause.

## Planning ratified in this change set

- [Security Controls — Capability Roadmap](../planning/security-controls.md)
  (owner direction, Refinement 2: eight enumerated Security Control seams;
  current capability / limitation / target / non-goals / dependencies /
  sequencing guidance).

## Carry-forward dispositions

Every recorded consolidation input, with its disposition. "Ticket A/B/C"
are the proposed future-work issues defined below — tracked work, authorized
by nothing in this record.

| # | Input (source) | Disposition |
|---|---|---|
| T7-1 | Refused waits surface as termination statistics, never wait figures (STATUS T7) | Stands as accepted architecture practice (ADR-0007: a refusal is never slept). No action. |
| T7-2 | Additive execution keys as the planned≠attempts mechanics (STATUS T7) | Stands. No action. |
| T7-3 | `_planned` walk parallels `collect`/`projections` traversals (STATUS T7) | **Ticket A** (traversal unification). |
| T7-4 | `SINGLE_ARTIFACTS`/`REFUSED_OUTCOMES` restate vocabulary exposed only as literals (STATUS T7) | **Ticket B** (closed-vocabulary ownership). |
| T8-1 | Spec "sorted by ruleset `id`" lacks the malformed-id tiebreak (owner-routed editorial) | **Resolved here** — editorial clarification appended to the Slice 2 specification. |
| T8-2 | `_item_key` docstring silent on bool-id sorting | **Ticket B** (documentation item within vocabulary/ordering cleanup). |
| T8-3 | Equal-key page-split tie could carry a comment at `_classify_drain` | **Ticket B**. |
| T8-4 | Dispositioned S10 recommendations: projection-dict shape ×3; `count`/`length` kind vocabulary; test-side `ITEM_SUMMARY` copy | Recorded, no change — dispositions stand. |
| T9-1 | No offline CLI path regenerates `reports/` | **Ticket C** (offline report regeneration). |
| T9-2 | V10 gap record lacked the "safely provisionable" rationale clause | **Resolved here** — validation-environment edit. |
| T9-3 | `unprotected-repo` inventory-row arrow readable against emptiness-is-a-value | **Resolved here** — validation-environment edit. |
| T9-4 | Closing coverage sentence overstated offline V12 coverage | **Resolved here** — validation-environment edit. |
| T9-5 | T9 commit-message re-derive phrasing omits the reports scoping | Not fixable (immutable commit); recorded here — the phrasing is superseded by T9-2..4's corrected text and Ticket C's scope statement. |
| QG-1/QG-2 | T10 S10/S11 non-blocking observations, content unrecorded | Formally recorded **disposition-preserved / content-transient** per MADR-0004 (non-retroactive; no reconstruction). Motivating example for MADR-0004. |
| Review §3 | Fan-out walk implemented three times (`collect`/`projections`/`summary`) | **Ticket A**. |
| Review §3 | Closed vocabularies restated as literals (states, reasons, wait tokens, `unknown` sentinel, absence-message dual pin, header-allowlist overlap) | **Ticket B** (the absence-message dual pin is its highest-value item — drift hazard for the re-pin rule). |
| Review §3 | `taxonomy` depends upward on `transport` for constants/predicates | **Ticket B** scope note (shared-vocabulary module resolves the direction). |
| Review §3 | Rate-limit precedence evaluated twice (live vs. retained inputs) | Recorded as deliberate architecture (E1-Q3: derivation reads retained evidence only). No unification without a decision — any change is an Architecture Proposal. |
| Review §3 | Page-glob/path construction repeated; duplicate inventory-page load in `derive`; structural report computed twice | **Ticket A** (the pre-approved `evidence_paths.py` split is the natural vehicle). |
| Review §3 | `collect.py` re-implements body parsing; 2xx predicate ×6 | **Ticket A/B** overlap; listed in both scopes, implemented once. |
| Review §3 | No packaging metadata (`PYTHONPATH=src`) | Recorded, no action — revisit if distribution ever becomes scope. |
| Review §3 | Test-fixture import coupling (two hub modules) | Recorded, no action — growth constraint noted for future test planning. |
| Strict/tolerant | Strict derivation vs. type-deep tolerant reporting scans (T7 repair) | Recorded as settled practice: entry evidence strict, tree scans tolerant with scan-only tolerance. Stands. |
| Descriptor evolution | Multi-request combination semantics (ADR-0004 deferral; candidates #28 and Code Scanning per ADR-0008) | Deferral stands; trigger unchanged (first composite/multi-request slice). |
| Theme E | Issue #26 — Observation Target Model evaluation at this gate | **Evaluated**: the Security Configuration control (ADR-0008, roadmap) is the first concrete organization-scoped evidence source, making generalization necessary rather than speculative. Decision deferred to the slice that first needs an org-scoped target, with #26 as its vehicle. #26 stays open; cross-reference proposed below. |
| Theme F | Domain modeling | Gated: begins only after this consolidation is owner-accepted, with explicit owner authorization (`/domain-modeling` → `CONTEXT.md`). |
| V10 / V12 | Standing validation gap and limitation | Stand as recorded; V12's trial route expires 2026-08-28 (sequencing input for #2/#3 in the roadmap). |

## Three-class durability record (motivating evidence for MADR-0004)

Observed at the Architecture Consolidation Review over Slice 2's gates:

| Class | Definition | Observed instances |
|---|---|---|
| I | Full content in durable artifacts | T5/T6/T7/T8/T9 findings and observations (PR bodies #46/#49/#51/#53/#55); E1 refinements and carried planning notes promoted into the specification |
| II | Content recoverable from remediation footprint only | T3 S10 findings (resolutions in ticket commits); T8 run-1 editorials (fix commit `c472164`) |
| III | Disposition preserved; content transient | T2's two dispositioned judgement calls; T6 run-2's three declined judgement calls; **T10's QG-1/QG-2** (zero-diff gate — the limit case) |

Repository-observable statement: retained fidelity varied by gate, with no
explicit architectural rule defining the required persistence level; fidelity
correlated with diff size. MADR-0004 defines the rule from acceptance forward.

## This change set's review findings (MADR-0004 applied)

Populated at review completion; this consolidation gate adjudicates a
documentation/governance diff, so its findings persist here by construction.

- Standards axis: no findings surviving to adjudication.
- Spec axis (owner direction as originating requirement): no findings
  surviving to adjudication.
- Regression: full suite re-run on the change set — 218/218 OK (docs-only
  diff; production tree byte-identical to `0da2265`).

## Proposed closeout issues (texts; created at owner acceptance, not before)

**Ticket A — Evidence-tree traversal and path unification.**
One shared target×descriptor walk and one artifact-path builder consumed by
`collect`, `projections`, and `summary` (pre-approved `evidence_paths.py`
split as vehicle); removes the triplicated fan-out walk, repeated page globs,
duplicate inventory-page load in `derive`, double structural-report
computation, and `collect.py`'s reimplemented body parsing. Behavior-preserving
refactor; byte-identity of observed documents and reports proven in-suite.
Sources: T7-3; Review §3. Normal S6→S7 path; no architecture change.

**Ticket B — Closed-vocabulary ownership.**
Single ownership for the closed sets: taxonomy states, deterministic reasons,
wait outcome/category tokens, the `unknown` sentinel, the absence-message pin
(single-sourced from the descriptor), and the header-allowlist relationship;
resolves the `taxonomy`→`transport` constant dependency direction; includes
the `_item_key` bool-id docstring note and the `_classify_drain` tie comment.
Behavior-preserving; byte-identity proven in-suite. Sources: T7-4, T8-2,
T8-3; Review §3.

**Ticket C — Offline report regeneration.**
A CLI path regenerating `reports/` from retained evidence plus the engine
(ADR-0001 derivability made operational for reports); scope includes the run
selection rule and byte-identity acceptance against collect-time reports.
Source: T9-1 (Quality Gate recommendation, carried to this gate).

**Planning issue — Security Controls capability roadmap (tracking).**
Points at `docs/planning/security-controls.md` and ADR-0008; tracks the
roadmap's decision-phase prerequisites (#2/#3 facts, policy-definition model,
combination semantics, #26) and records slice selections as they are made.
Cross-references proposed on existing issues (no closures, no repurposing):
**#26** — evaluation outcome above; **#27** — narrower related projection,
stays open, noted as a Secret Scanning evidence-surface input; **#28** —
noted as co-candidate trigger (with Code Scanning) for combination semantics.

## Gate outcome

Consolidation prepared on `feat/architecture-consolidation`; authority changes
only at owner review and merge (⟦G-Accept⟧). Domain modeling and any slice
work remain gated behind that acceptance.
