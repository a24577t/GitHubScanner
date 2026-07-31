# Security Control realization model

**Status:** accepted

Security Controls (ADR-0008) are realized through three fixed elements — the
canonical pattern every roadmap control imitates:

1. **Evidence realization by dedicated-request descriptor.** A control's
   evidence is collected by ordinary ADR-0004 resource descriptors — real API
   requests with per-repository retained artifacts. Controls sharing one
   evidence surface share one descriptor (one request, one taxonomy state,
   one projection covering every sharing control's fields, designed once).
   Zero-request ("projection-only") controls deriving from another
   collection's evidence are rejected: they fall outside ADR-0004's
   descriptor definition, forfeit per-repository classification fidelity,
   and their sole virtue is implementation convenience.
2. **Control-definition layer.** Controls are reviewed in-code declarative
   data, validated at import time, each naming its evidence descriptor, the
   projected field it reads, and its applicability rule. Control-plane
   evaluation is pure, deterministic, first-match-wins over derived
   descriptor entries, with closed per-plane vocabularies and exactly one
   deterministic reason per conclusion. Ambiguity degrades toward
   `unknown` / `applicability-unknown` (the ADR-0006 direction lifted to the
   control planes): disablement only from an affirmative status; an
   affirmative `enabled` status self-evidences applicability while
   `disabled` establishes nothing about it; applicability chains key on
   availability, never enablement.
3. **Control-observation documents.** One latest-only observed document per
   control (`observed/controls/<control>.json`, house shape), entries in
   canonical discovery order, every conclusion citing its retained
   descriptor evidence (`{resource, state, reason}` + document `run_id`;
   ADR-0005 addressing identifies the artifact — paths are never evidence).
   The document's top-level state is the evidence-plane rollup (Slice 1
   listing rule over cited evidence states) only; control-plane output
   aggregates as closed-vocabulary distribution counts. No estate-level
   operational state exists anywhere — such a collapse is a policy judgment
   and belongs to the gated Conformance plane.

## Consequences

- Additivity: a control joining an already-collected evidence surface
  touches only its control definition, tests, and fixtures; a control
  needing new evidence adds its descriptor by the T8-proven path. Slice 3's
  Push Protection criterion proves the same-surface case only; the
  cross-evidence-shape proof is assigned to the next roadmap control.
- Existing resource documents, engine modules, and prior outputs remain
  byte-identical when controls are added.
- *Deferred:* an `unavailable` operational-state rule, until an affirmative
  plan/product discriminator exists (wayfinder #2/#3); a `not-applicable`
  evidence rule, until affirmative inapplicability evidence exists for some
  control; multi-descriptor (composite) control combination semantics, which
  remain ADR-0004's deferred decision triggered by the first composite
  control.
- *Rejected:* zero-request projection-only controls; extending resource
  observed documents with control-plane fields; any rollup of operational
  state or applicability across repositories.
