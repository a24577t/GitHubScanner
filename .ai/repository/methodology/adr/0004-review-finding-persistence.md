---
status: accepted
---

# MADR-0004 — Canonical persistence model for review findings

**Status: accepted.** Project-independent and agent-neutral (P1, P6); a
concrete project appears only as a marked *Example*. This decides the
persistence model [MADR-0003](0003-dual-mode-evidence-transport.md) left open:
governed review artifacts must be "durable and auditable," but no rule defined
the required persistence level. It is **forward-looking**: it governs future
review findings and neither requires nor permits reconstruction of historical
finding content from any non-repository source (MADR-0001).

**Motivating evidence.** The repository exhibits gate-dependent variation in
review-finding durability. The recorded post-slice consolidation analysis
identified three observed durability classes: full content preserved in
durable artifacts; content indirectly recoverable from remediation footprint
(fix commits and diffs); and disposition preserved with supporting text
existing only in transient review sessions. Retained fidelity correlated with
diff size — gates adjudicating little or no code change retained the least,
although such gates are exactly where findings are the only work product.
> *Example (GitHubScanner): the Slice 2 consolidation record
> (`docs/consolidation/slice-2-architecture-consolidation.md`) carries the
> three-class evidence table; the T10 gate observations QG-1/QG-2 are the
> recorded disposition-only limit case.*

## Decision

- **Scope.** Every review finding that survives to gate adjudication —
  accepted, dispositioned, deferred, or carried forward — at any Repository
  Gate's review chain.
- **Required fidelity.** Full content: the finding's statement, its Review
  Discipline classification, its evidence citation, its disposition, and its
  provenance (gate, work item, revision). A finding fully resolved *within* a
  review cycle before adjudication may instead persist as its remediation
  footprint (the fixing commits), provided the resolution is traceable to it.
- **Canonical location.** A committed artifact within the change set the gate
  adjudicates. A gate adjudicating no production diff carries its findings in
  its reconciliation change set — durable finding records by construction,
  independent of diff size.
- **Authority ordering.** Committed finding record → pull-request/review
  bodies → Status Artifact summaries. The Status Artifact carries
  dispositions, never sole finding content.
- **Non-retroactive.** Applies from acceptance forward. Historical
  footprint-only and disposition-only records stand as recorded;
  disposition-preserved / content-transient is their permanent, honest status.
- **Separation from implementation.** This is the architectural decision only.
  Record templates, directory conventions, tooling, and any interaction with
  the deferred REP / claim-register implementation set (MADR-0003; tracked
  future work) are separate, later implementation decisions — none is selected
  or implied here. Until a convention exists, the model is satisfied by
  committing the finding content in the adjudicated change set in any
  readable, citable form.

## Consequences

- The Review Discipline gains a finding-persistence clause pointing here; gate
  reviewers apply it as part of review completion.
- Zero-diff gates produce durable finding records by construction.
- No implementation vehicle is chosen; the deferred MADR-0003 implementation
  set is neither reopened nor implied by this decision.
