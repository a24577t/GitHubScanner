# Methodology Validation

**Subsystem charter (design document).** The artifacts under `.ai/methodology/validation/` are
validation *evidence*, not accepted methodology. Nothing here changes the methodology; adoption
of any observation is a separate, human-owned decision made through the mechanisms named under
[Authority boundaries](#authority-boundaries).

## Purpose

Methodology Validation validates the methodology by the act of practising it — the mirror of
Phase 2's Architecture Validation Sequence, which validates the architecture by building the
slices. The same implementation work that stresses the architecture also stresses Bootstrap, the
Decision-Gated Implementation Lifecycle, review discipline, and the STATUS/continuity model. This
subsystem gives that evidence a durable, repository-resident home and a disciplined path from
**evidence → adjudication → authority**, keeping the three strictly separate so evidence is never
mistaken for a decision.

## Artifacts and relationships

- **Observations** — [`observations.md`](observations.md). Immutable, append-only, evidence-first
  records of the methodology in practice, each under a stable `MO-NNN` identifier. An observation
  states verifiable evidence and its observed impact only — no disposition and no remedy.
- **Reviews** — [`reviews/`](reviews/). Append-only review records (`MVR-NNN`), one per human-owned
  review event. A review references immutable `MO-NNN` identifiers and assigns each a disposition
  (accepted / declined / deferred / superseded) with rationale, pointing to the resulting decision
  artifact where accepted.

An observation is written once and never edited. A review never edits an observation; it
references it by identifier. **The review records are the sole source of an observation's
disposition** — there is no separate status field and no derived register. An observation that no
review references is simply unadjudicated.

## Authority boundaries

- **Anyone may contribute observations.** Any implementation or review participant — human or
  agent — may append an observation.
- **Observations carry no methodology or design authority.** Recording an observation asserts
  nothing about the methodology and changes nothing; it is evidence awaiting review.
- **Adjudication is human-owned.** Only a human review (principle P1) may assign a disposition to
  an observation.
- **Accepted changes gain authority only through the repository's existing methodology
  mechanisms** — a Methodology ADR (MADR under `.ai/methodology/adr/`) for an axiom or accepted
  decision, or an edit to an evolvable design document (the lifecycle model, the methodology
  principles, or the Decision-Gated Implementation Lifecycle). Authority never originates in this
  subsystem: a review record only points to that decision; it does not constitute it.

## Lifecycle

1. **Observe** — a participant appends an immutable observation. Low ceremony; no authority.
2. **Accumulate** — observations accrue between reviews; the methodology is not changed
   mid-validation, so the evidence survives to be weighed together.
3. **Review and convert together** — at a human-owned cadence (for example a phase gate or a
   baseline boundary), a review adjudicates a batch and records dispositions in an append-only
   review record. An observation may be recorded **`Accepted` only when the resulting
   authoritative methodology artifact already exists or is created in the same reviewed change
   set** — through the existing decision/design mechanisms above — so the immutable review points
   to an artifact that already exists. Until conversion is ready, the observation stays
   **`Deferred`** or unadjudicated. A review record is never amended later merely to add the
   authoritative-artifact pointer.
4. **Trace** — observations and reviews together preserve the path from evidence to any resulting
   decision, permanently.
