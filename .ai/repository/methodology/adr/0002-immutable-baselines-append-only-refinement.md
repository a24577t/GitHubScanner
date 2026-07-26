---
status: accepted
register: methodology
---

# MADR-0002 — Immutable Baselines and Append-Only Refinement

Principle P5 (*Refinement over rewrite*) presupposes that architecture is published as baselines and refined between them, but no architectural decision established that. This ADR records the enduring decision P5 depends on. It is deliberately narrow: it governs only how accepted architecture is published and evolved, and says nothing about lifecycle topology — phases, work items, milestones, state machines, counters, and transitions are design (`lifecycle-model.md`) and may evolve freely around this decision.

## Decision

**Architecture evolves through immutable published baselines and append-only refinements.**

1. **Architecture is published as immutable, versioned baselines.** A baseline is an accepted, versioned snapshot of the architecture. Once published, a baseline is never edited.
2. **Between baselines, further accepted architectural decisions are recorded as append-only refinements** — new decision records that advance an architecture version.
3. **Accepted architecture is never modified in place.** Neither a baseline nor an accepted decision is edited; a correction or clarification is a new record that supersedes or refines the prior one.
4. **A future baseline consolidates accumulated refinements** into a new immutable, versioned snapshot.

## Scope

This ADR decides only the publication and evolution of accepted architecture. It intentionally establishes nothing about phases, work items, milestone predicates, state machines, version counters, or any lifecycle topology. Those are design and belong to the lifecycle model, which is free to evolve around this decision.

## Considered options

**Edit accepted architecture in place** — rejected. It destroys the append-only decision record: a reader can no longer see what was decided, when, or why it changed. Editing an accepted decision is the governance equivalent of rewriting published evidence.

**Republish a baseline for every accepted decision** — rejected. It churns baselines and conflates "a decision was accepted" with "the architecture was re-snapshotted." Refinements accumulate cheaply between baselines; a baseline is published deliberately, not per decision.

## Consequences

- **P5 (Refinement over rewrite) is grounded in this decision** rather than presupposing it.
- Forward navigation is carried by the *next* baseline: because an accepted baseline is never edited, it cannot point forward to a later refinement, so the consolidating baseline records the linkage.
- The lifecycle model's Refinement transition, its baseline and architecture-version counters, and its baseline-publication transition are implementations of this decision. The specific topology around them is not decided here and may change.
- This decision is project-independent and agent-neutral.
