---
status: proposed
---

# Decision-Gated Implementation Lifecycle

**Status: proposed** (draft for review). A *design* under [MADR-0001](adr/0001-repository-authoritative-continuity.md) and [MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md); it elaborates the **In Implementation** state and the **Refinement excursion** of the [Lifecycle Model](lifecycle-model.md) and may evolve without reopening either axiom.

**Scope.** Agent-neutral and role-neutral ([P1](principles.md)): this lifecycle governs **every contributor** — human or implementation agent — identically. It is not an instruction to an assistant; it is how work crosses from decision to code in this repository. A concrete project appears only as a marked *Example*.

## Governing principle

**No governance or system-architecture decision is made during implementation.** Implementation *executes* decisions already ratified in an authoritative artifact — an ADR, the accepted architecture, or an approved specification. It may freely make **local implementation-design decisions** — naming, internal structure, helper extraction, algorithm and data-structure choices, the arrangement of code behind a seam — **provided they preserve the approved architecture, its invariants, its published contracts, and externally observable behavior.**

A choice crosses the line — and must leave implementation for the decision phase — when it would **change or resolve** any of:

- an architectural **invariant** or a **contract** (a seam's interface, a closed set, an evidence or serialization guarantee);
- **externally observable behavior** the architecture or specification fixes;
- an **open question** the authoritative artifacts leave unanswered at a genuine decision point (authority, applicability, aggregation, integrity, and the like).

The test is not "is this hard?" but "**does the authoritative record already settle it?**" If yes → implement. If no → it is a governance or architecture decision, and it goes through the decision phase, not the keyboard.

## Phases (one responsibility each)

Described by function; the GHES project's current tool for each is named in brackets as an *Example*, never as part of the definition — tools are the current implementations of these transitions ([lifecycle-model.md](lifecycle-model.md), "Relationship to prompts").

| Phase | Responsibility | Example tool |
|---|---|---|
| **Decision** | Resolve open governance/architecture questions; reusable and re-enterable | Wayfinder (+ grilling / domain-modeling / research) |
| **Ratify** | Record each decision authoritatively | ADR / specification |
| **Slice** | Split the decided build into shippable vertical slices | to-tickets |
| **Shape** | Place seams; choose module depth | codebase-design |
| **Build** | Implement the confirmed seam, red → green | TDD |
| **Verify — diff** | Does the diff meet standards and match its spec | code-review |
| **Verify — architecture** | Did the diff stay within ratified architecture, or cross into an unratified decision | Architecture Conformance Review (below) |

## Normal flow

```
Decision ─► Ratify (ADR / Spec) ─► Slice ─► ┌── per slice ────────────────────────────────┐
                                            │ Shape ─► Build ─► Verify-diff ─► Verify-arch │─► Merge
                                            └─────────────────────────────────────────────┘
```

Each slice runs against an already-ratified baseline. If nothing unratified surfaces, it flows straight through to Merge.

## The decision phase is re-enterable

The Decision phase is not a one-time front step. It is entered from two places:

1. **At the front** — charting a large, foggy effort before any slice exists.
2. **Mid-implementation** — whenever a slice uncovers a governance or architecture question the authoritative record does not settle. This is the [Lifecycle Model](lifecycle-model.md)'s **Refinement excursion**: a self-loop on *Phase Active*, triggered from within work-item activity, that records an append-only refinement and updates the architecture artifacts **without** editing an accepted baseline in place.

Re-entry is a normal, expected move — not a failure. While it is open the slice is *pending the decision*, and the engine's interim behavior **fails loud** (never silently resolves) until the decision lands.

## Exception flow (halt → decide → ratify → resume)

```
   a governance/architecture question surfaces
   (raised during Build, or caught at Architecture Conformance Review)
                     │
                     ▼
        HALT the slice   ──►  Decision phase (one question)
        (do NOT decide        resolve via the Decision-phase tools
         it locally)                    │
                                        ▼
                        Ratify: ADR refinement / spec update
                        (authoritative baseline advances — Refinement excursion)
                                        │
                                        ▼
                        Resume the slice at the interrupted phase
                        (the work item never left In Implementation; it paused
                         and now continues — cf. the Remediation destination
                         principle, by analogy only),
                        re-running Verify-diff and Verify-architecture
```

The decision is ratified in an authoritative artifact **before** code resumes — it never lives only in a commit message or a code comment. Throughout, the work item **remains in *In Implementation*** — it does **not** enter the formal *Remediation* state; it **pauses** while the governing decision is ratified in the appropriate authoritative artifact, then **resumes at the interrupted phase**. The Lifecycle Model's Remediation *destination* rule — "its destination is the interrupted state, not the nearest stable state" — is invoked here only as an **analogous principle**, not as the lifecycle mechanism governing this case.

> *Example (GHES).* A governed-evaluation slice surfaced a question the authoritative ADRs did not answer — how authority selection behaves when a candidate binding's scope applicability is itself `Unknown`. The slice did **not** invent an answer: it failed loud, recorded the question as a decision ticket, and deferred. At the next slice's entry the Decision phase resolved it (a grill-with-docs review of the governing ADRs); the resolution was ratified as a refinement ADR and a specification update; only then did implementation resume. This is one instance of the Refinement excursion, alongside the earlier architecture-version refinements raised during specification review.

## Architecture Conformance Review

**Purpose: detection, not redesign.** This gate asks one question the diff-level review does not: *did this change create architecture that no authoritative artifact ratifies?* — a behavior at a genuine decision point (an invariant, a contract, a closed set, an observable guarantee, or an open architectural question) with nothing behind it in the ADRs, the accepted architecture, or the approved specification.

- **Verify — diff** (code-review) checks the change against the *existing* standards and the *existing* spec.
- **Architecture Conformance Review** checks whether the change **conforms to** the ratified architecture, or silently *extended* it.

On finding a crossing it does **not** bless, refine, or design the decision in review — it **halts the slice and re-enters the Decision phase** (the exception flow). Its job is to make an ad hoc governance/architecture decision impossible to merge, by catching it at the gate and routing it to the phase that owns it. A slice that made no such crossing passes to Merge.

**Checklist.** The review passes only when every item is confirmed against the authoritative artifacts (the ADRs, the accepted architecture, and the approved specification):

- [ ] The change **conforms to** the accepted architecture, ADRs, specifications, and invariants.
- [ ] **No unresolved governance or architecture decision** was made during implementation (only local implementation-design choices, per the governing principle).
- [ ] **Contracts and externally observable behavior** remain consistent with the authoritative artifacts.
- [ ] Any **newly discovered architectural question** was **halted, ratified** in an authoritative artifact, **and only then implemented** (never decided at the keyboard).
- [ ] With the above confirmed, the implementation is **eligible to proceed to Merge**.

Any unchecked item is a crossing: halt the slice and re-enter the Decision phase (the exception flow) rather than resolving it in review.

*Deferred (operationalization).* This gate is performed as a review activity defined by the checklist above; a dedicated Architecture Conformance Review **skill/prompt** is a deferred methodology enhancement — the phase-to-tool mappings are evolvable design, and no new skill is introduced here.

**On the name.** *Conformance* over *Compliance*: "Compliance" is a load-bearing term in this project's own product domain (the compliance dimension; `PolicyOutcome` values), and reusing it for a process gate would overload it. "Conformance" states the gate's job precisely — does the implementation conform to the ratified architecture — without colliding with product vocabulary.

## Traceability

- The governing principle and the halt-don't-decide rule implement **[P1](principles.md)** (human-owned decisions) and the methodology's **decision/design separation** (the MADR register versus design documents).
- The re-entry path **is** the Lifecycle Model's **Refinement excursion** — a work-item-scoped activity causing a project-scoped, append-only architecture refinement (MADR-0002). During it the work item stays in *In Implementation* and resumes at the interrupted phase; the Remediation *destination* rule is cited only as an analogous principle, not as the governing mechanism.
- "No ad hoc architecture decision merges" is enforced as a transition postcondition: Architecture Conformance Review is a precondition of Merge.
- The phase-to-tool mappings are **evolvable design** — the named tools are the current implementations of these transitions; nothing foundational depends on a specific tool.
