# AI-Assisted Engineering Methodology

**Status: accepted.** This directory defines the engineering process by which AI assistants and a human architect build software across many sessions, without depending on any assistant's conversation memory.

## Project-independence and agent-neutrality

The methodology is **project-independent**. It is being authored inside the GHES Governance repository because that is the first project applying it, but GHES is an *implementation example*, never a dependency ([P6](principles.md)). Every document here references a concrete project only as a marked *Example*. The intended seam is that this directory could move to its own repository without architectural change.

It is also **agent-neutral**. It names no AI assistant and assumes no permanent role: roles are assigned by the human architect and may change at any time ([P1](principles.md)). Only a prompt intentionally written for one consumer may name that consumer.

## The decision / design separation

- **The axioms** — the `adr/` register.
  - [`adr/0001-repository-authoritative-continuity.md`](adr/0001-repository-authoritative-continuity.md) (MADR-0001). Repository-Authoritative Continuity: the repository is authoritative, continuity is achieved through it and verified independently, the repository prevails; private conversation bootstrap is out of scope.
  - [`adr/0002-immutable-baselines-append-only-refinement.md`](adr/0002-immutable-baselines-append-only-refinement.md) (MADR-0002). Architecture evolves through immutable published baselines and append-only refinements; accepted architecture is never edited in place. Deliberately silent on lifecycle topology.
- **The design** — [`lifecycle-model.md`](lifecycle-model.md). One implementation of the axioms: two synchronized lifecycles (work-item and phase), coupled by the Milestone-Complete predicate, with Refinement and Remediation excursions and a session lifecycle. A design — it may evolve without reopening either decision; its Traceability section maps each construct to a decision, a principle, or evolvable design.
  - [`decision-gated-implementation-lifecycle.md`](decision-gated-implementation-lifecycle.md) — a design elaborating the *In Implementation* state and the Refinement excursion: no governance or system-architecture decision is made during implementation, the decision phase is re-enterable, and Architecture Conformance Review gates Merge. Agent-neutral; governs human and agent contributors alike.
- **The enduring constraints** — [`principles.md`](principles.md). Seven principles; several are corollaries of the ADRs (P2–P4, P7 of MADR-0001; P5 of MADR-0002).
- **The vocabulary** — [`glossary.md`](glossary.md). Project-independent terms, with `_Avoid_` guidance.
- **The decision register** — [`adr/`](adr/). Methodology ADRs (MADRs), kept separate from any project's architecture ADRs so the process evolves independently.

## Reading order

1. `README.md` (this file)
2. `adr/0001-repository-authoritative-continuity.md` — continuity axiom
3. `adr/0002-immutable-baselines-append-only-refinement.md` — baseline-governance axiom
4. `principles.md` — the enduring constraints
5. `lifecycle-model.md` — the state model (with a Traceability section)
6. `glossary.md` — vocabulary (reference alongside the others)

## Status

These documents are **accepted** as one coherent architectural unit: MADR-0001, MADR-0002, `principles.md`, `lifecycle-model.md`, `glossary.md`, and this README. Subsequent changes follow the methodology's own discipline — enduring decisions as new or refined MADRs (never edited in place, per MADR-0002); design changes in `lifecycle-model.md`. Acceptance dates and editorial history live in Git, not in these documents.

## Not yet present (deliberately)

- **No methodology Status Artifact.** Avoided until an independently versioned methodology lifecycle demonstrates a genuine need, to prevent two competing project-status artifacts.
- **No formalized prompts.** Prompts implement transitions and are written only after this model is approved; they are validated against the model, not the reverse.
- **Deferred decisions:** the refinement *publication policy* (when refinement triggers a new baseline) and the *architecture-version classification* rule remain open pending more evidence.
