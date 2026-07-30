# Slice 3 Architecture Grill — Input Materials

**Type:** planning artifact — the input package for the Slice 3 Architecture
Grill (Skill Execution Map S4). Owner-directed durable capture (2026-07-31) of
the session-prepared grill materials and the domain-modeling scope constraint.
**Standing:** the frozen proposal below is owner-approved *direction*; it
becomes ratified architecture only through the grill → ⟦G-Verdict⟧ → S5
consolidation → ⟦G-Accept⟧ chain. This document decides nothing and
authorizes no grill, domain-modeling, specification, or implementation work;
the grill convenes only with explicit repository-owner authorization.

## Frozen proposal

**Slice 3 — Secret Scanning Control Family.** One approved slice
specification covering two Security Controls under
[ADR-0008](../adr/0008-security-control-model.md):

1. **Secret Scanning** — establishes the canonical Security Control
   realization (the reference pattern later controls imitate);
2. **Secret Scanning Push Protection** — follows as the additivity-proof
   control, carrying a falsifiable architectural acceptance criterion: adding
   the second control touches only its control definition, projection, tests,
   and fixtures.

Strict implementation ordering inside the slice: Secret Scanning first;
Push Protection only after the pattern is gate-validated. The applicability
chain (push protection is meaningful only where secret scanning is available)
is designed once, in the single slice specification.

**Planes in scope:** Observation, Applicability, Operational State
(observation side of ADR-0008's boundary) only.

**Out of scope:** Policy Expectation; Conformance; organization-level
configuration; all other Security Controls; alert inventory; secret
inventory; vulnerability inventory; malware detection.

## Fixed invariants — out of grill scope

Already ratified; the grill evaluates against them and never reopens them:
ADR-0001 evidence layers and derivability; ADR-0002 seven-state taxonomy and
affirmative absence; ADR-0003 explicit targeting and token discipline;
ADR-0004 descriptor model and its T8-proven additivity claim; ADR-0005
canonical discovery and evidence addressing; ADR-0006 taxonomy evidence rules
(degradation direction fixed); ADR-0007 bounded waits; ADR-0008 planes,
closed vocabularies, evidence rules, and the observation/governance boundary;
MADR-0004 review-finding persistence; observation-first architecture.

## Slice-boundary comparison (owner-directed; grill Question Q1)

Criteria fixed by the owner: architectural clarity, Security Control pattern
reuse, testability, long-term maintainability — never implementation
convenience.

- **Option 1 — one bounded slice, both controls co-designed and
  co-implemented.** Clarity: the boundary is the control family; the
  applicability chain is designed once and cannot become an afterthought.
  Weakness: the pattern is never frozen and then challenged — no falsifiable
  additivity criterion, because nothing is held back to test it.
- **Option 2 — Secret Scanning as the canonical first implementation; Push
  Protection immediately following after the pattern is validated.** Yields
  the reference realization and the strongest pattern test (a T8-style
  falsifiable additivity AC), catching pattern defects before replication
  across the eight roadmap seams. Weakness: if Push Protection were also
  *specified* later, the applicability chain risks retrofit rework.
- **Synthesis (recommendation):** separate the boundary from the ordering —
  **one approved slice specification covering both controls (Option 1's
  boundary), with Option 2's strict implementation ordering inside it.**
  Structurally the shape Slice 2 proved (T1–T7 built the engine on the first
  descriptor; T8 added the second under a falsifiable architectural AC),
  lifted from "second descriptor" to "second Security Control." The grill
  attacks this synthesis first; if it survives, both options are honored.

## Open architectural questions (the grill resolves; closeout does not)

- **Q1 — Slice boundary and implementation ordering:** adopt, amend, or split
  the synthesis above.
- **Q2 — Evidence realization (projection-only vs. dedicated request):** the
  `security_and_analysis` object already arrives in committed inventory
  evidence. Is a projection-only Security Control admissible under ADR-0004
  (descriptor defined as "one or more API requests"), or does control
  coherence require a dedicated request? Field visibility varies by
  credential, so the evidence rule must distinguish *field absent in the
  inventory body* (→ `unavailable`/`unknown`, per affirmative-evidence
  discipline) from *affirmatively disabled*. The slice's sharpest question.
- **Q3 — Affirmative applicability evidence:** what affirmatively establishes
  `applicable` vs. `applicability-unknown` for plan-gated features while
  wayfinder #2/#3 facts are incomplete; degradation direction fixed — never
  guess.
- **Q4 — Reachable operational-state subsets:** which of ADR-0008's eight
  values each control can actually produce, with the evidence rule per value
  (`partially-configured` likely unreachable for both — pin the subset).
- **Q5 — Observed-document shape:** do per-resource observed documents gain
  applicability/operational-state fields, or is a control-observation
  document class introduced? Serialization and byte-identical-derivability
  invariants apply either way.
- **Q6 — Rollup and coverage semantics** for control-level output: reuse of
  the Slice 1 listing rule, or a control-specific rule.
- **Q7 — Validation matrix and fixture feasibility:** which states are
  live-pinnable on GHScannerLab (Free-plan public repositories permit real
  enable/disable of these features — to be confirmed at fixture
  provisioning); credential requirements; conditional rows pending #2/#3
  (trial-route expiry 2026-08-28 as a scheduling input).

## Domain-modeling scope constraint (owner-directed, binding on S5)

When domain modeling runs (S5, alongside specification consolidation, after
an owner-approved grill verdict), its scope is intentionally narrow — only
the domain concepts ADR-0008 requires:

- Security Control; Observation; Applicability; Operational State; evidence
  descriptors; and the relationships among those concepts.

Explicitly excluded: API clients; collectors; transport; DTOs;
GitHub-specific implementation plumbing; production implementation. Those
belong after the domain model has been reviewed and accepted.

## Governance and stop conditions

Skill Execution Map path: S4 Architecture Grill (this input package) →
⟦G-Verdict⟧ (owner approves, conditions, or rejects the verdict) → S5
`to-spec-repo-owner` + `domain-modeling` (under the scope constraint above) →
⟦G-Accept⟧ (owner review, acceptance PR, owner merge, STATUS reconciled) →
S6 `to-tickets` → S7–S11 per ticket → ⟦G-Merge⟧ each. Each Security Control
in `docs/planning/security-controls.md` remains an independent architectural
seam regardless of the Slice 3 selection.
