---
status: accepted
---

# AI-Assisted Engineering Lifecycle Model

**Status: accepted.** This document is a *design*: one implementation of the axiom fixed by [MADR-0001 — Repository-Authoritative Continuity](adr/0001-repository-authoritative-continuity.md). It may evolve without reopening that decision.

The model is **project-independent and agent-neutral**. A concrete project appears only as a marked *Example*, never as part of a definition; the first project applying it is GHES Governance, and the model does not depend on it. The model names no AI assistant and assumes no permanent role — roles are assigned by the human architect and may change at any time. Only a prompt intentionally written for one consumer may name that consumer.

## Shape

The lifecycle is **not** one mutually exclusive state machine. It is two synchronized lifecycles over a set of project-wide conditions:

1. a **Work-Item Lifecycle** — the primary machine, one independent instance per work item;
2. a **Phase Lifecycle** — a coarse project-wide machine with a single dominant resting state;
3. coupled by **Milestone-Complete**, a *predicate* (not a state) over the work-item instances;
4. over project-wide **conditions/artifacts** (baseline version, architecture version, repository version) that are monotonic counters produced by transitions — not states.

Modeling these as one machine was rejected: it cannot represent two work items at different stages at once, and it forces "an architecture baseline exists" to turn off when work begins, which is false.

## Work-Item Lifecycle (one instance per work item)

> *Example (GHES): a work item is a **vertical slice**; "Vertical Slice 1 — Observe-Mode Tracer" is one instance.*

States are only those the repository can *prove* (P7). "Draft" and "Review" are one state, because no durable artifact distinguishes them — review is an activity within the draft state. "Tickets generated" is a transition, not a state.

| State | Proving artifact | Kind | In → / → Out | Remediation |
|---|---|---|---|---|
| *Not Started* | no specification for the item | transient | — → author-spec | n/a |
| Specification In Progress | spec present, `Status: Draft` | transient | author-spec → / → approve | abandon → Not Started |
| **Specification Approved** | spec `Status: Approved` | **stable** | approve → / → generate-tickets | re-open on defect → In Progress |
| In Implementation | approved spec + open tickets / PRs | transient | generate-tickets → / → verify-and-merge | failed review → stays In Implementation |
| **Work-Item Complete** | tickets closed, work merged, tests pass, Status updated | **stable** | verify-and-merge → / → feeds Milestone-Complete | regression → re-open |

Work-item instances are independent: one may be *In Implementation* while another is *Not Started*. Coexistence across instances is normal; it is not two states of one machine.

## Phase Lifecycle (one project-wide instance)

> *Example (GHES): "Phase 1 — Architecture Discovery"; "Phase 2 — Architecture Validation Sequence".*

| State | Proving artifact | Kind | In → / → Out | Remediation |
|---|---|---|---|---|
| Pre-Baseline | draft decisions, no baseline | transient | consolidate → / → phase-gate | — |
| **Phase Active** | baseline v*N* present; Status points at active work | **stable** (dominant) | publish-baseline → / → phase-gate *(when Milestone-Complete holds)* | — |
| Phase Gate | phase-gate review record | transient | Milestone-Complete → / → {Pass → publish; Fail → remediate} | Fail → remediation → Phase Active |
| Baseline Publication | baseline v*N+1* | transient | Gate(Pass) → / → release | — |
| *(Release)* | version tag **and** Status reconciled | transition | publish → / → Phase Active (next) | tag/Status mismatch → remediation |

The project spends almost all of its time in **Phase Active**. This is what "an architecture baseline exists" means as a durable condition — orthogonal to whatever the work items are doing.

## Coupling: the Milestone-Complete predicate

`Milestone-Complete(phase) := every work item in the phase is Work-Item Complete.`

It is a **predicate, not a state.** When it becomes true it *enables* the Phase Active → Phase Gate transition. It is never occupied, entered, or left.

## Project conditions (artifacts, not states)

- **Baseline version** (v1, v2, …) — produced by Baseline Publication ([MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md)).
- **Architecture version** (e.g. 1.0.x) — advanced by Refinement ([MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md)).
- **Repository version** (release tags) — produced by Release; a project-release convention, evolvable design.

These are monotonic counters recorded in repository artifacts. They parameterize states; they are not themselves states.

## Cross-cutting excursions

**Refinement** — a first-class transition implementing [MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md); a self-loop on *Phase Active* that is triggered *from within work-item activity* (for example, a specification review that exposes a gap between accepted ADRs). It records an append-only refinement, updates architecture artifacts, and advances the architecture version — **without** editing the baseline in place or republishing it. A work-item-scoped activity may thus cause a project-scoped effect; the model permits this deliberately.

> *Example (GHES): MADR-style refinements to the product architecture — ADR-0013 and ADR-0014 — were raised during specification review and advanced the architecture version without a new baseline.*

*Deferred:* the **publication policy** — when accumulated refinement justifies a new baseline versus remaining architecture-version increments only — is not fixed here. It is coupled to the (also deferred) version-classification rule and awaits more evidence.

**Remediation** — an excursion that restores the preconditions a blocked transition required. **Its destination is the interrupted state, not the nearest stable state**: remediation repairs what blocked the original transition, then work resumes where it was interrupted. The excursion is the repair; the target is the state that was blocked.

## Session Lifecycle (one per working session)

`Not Started → Bootstrapping → { Context Established | Bootstrap Failed } → Working → { Clean Close | Handoff Emitted } → Ended`

- **Bootstrapping** runs *verifiable* preconditions over repository state (MADR-0001). Success → *Context Established*; failure → *Bootstrap Failed* → Remediation, never Working.
- **Working** performs transitions on the repository and its work items.
- **Clean Close** is permitted only under the continuity rule below; otherwise the session emits a Repository Continuity Artifact.

## Continuity mechanisms and synchronization

The methodology defines exactly two continuity mechanisms:

1. **Authoritative repository artifacts** — durable, permanent, the single source of truth.
2. **Repository Continuity Artifact** — a *committed*, non-authoritative project artifact that carries **only the uncommitted in-flight intent needed to resume a transient state**: what a session was doing and what remains, pointing at committed work rather than restating it. It disappears once that intent becomes committed authoritative state.

**Inter-session and inter-consumer synchronization flows only through these two.** One consumer's reasoning reaches the project only when the human architect converts it into authoritative repository artifacts. Per MADR-0001 (D3): a Repository Continuity Artifact may carry only information *not yet represented in the authoritative record*, and where it conflicts with committed repository state, the repository prevails and the discrepancy is surfaced.

**A Repository Continuity Artifact must never become a second representation of committed repository history.** Accepted architecture, specifications, ADRs, released versions, and the record of refinements since the last baseline are **authoritative repository content** — carried by the Status Artifact and the accepted decision register (see [MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md)), never by a continuity aid. Committed history belongs exclusively to authoritative artifacts; a continuity aid that summarized it would duplicate the authoritative record and could drift from it.

**Out of scope — conversation bootstrap.** A consumer may privately restore its own conversational context by whatever means it chooses (a *Conversation Continuity Artifact*: never authoritative, never repository state, never an inter-consumer channel). The lifecycle **neither defines nor depends on** it — another consumer may have no equivalent, or a different mechanism entirely. It is not a synchronization mechanism and plays no part in this model.

## Stable vs transient, and the continuity rule

Stability is evaluated **per machine**: within its own lifecycle, a state is stable or transient. The **stable** states are *Phase Active* (phase machine) and *Specification Approved* and *Work-Item Complete* (work-item machine); every other state is transient.

**Resumability is a conjunction, not a single state.** The *project* is resumable — and a session may clean-close — only when the phase machine is at a stable state, **every** work-item instance is at a stable state or *Not Started*, and the continuity rule below holds. One work item mid-transition makes the project non-resumable even if the phase and every other work item are stable; a session ending then must emit a Repository Continuity Artifact for that work item.

> **Continuity rule (ratified).** A session may close *without* emitting a Repository Continuity Artifact only when the repository is internally consistent, all durable work is committed, and the Status Artifact accurately represents the current state and next objective. Otherwise the session must emit one. Repository artifacts remain authoritative over every Repository Continuity Artifact.

## Universal postcondition

Every transition that returns the repository to a **stable** state carries one shared postcondition: **leave the Status Artifact accurate** (current state, next objective, version counters reconciled). This is stated once here rather than repeated per transition; a transition that violates it leaves the repository in a state the next bootstrap's verification will reject.

> *Example (GHES): a release that tagged a new repository version without reconciling the Status Artifact's recorded version violated this postcondition and produced state drift.*

## Status Artifact: last-stable-state semantics

The Status Artifact reflects the **last stable state**. It is accurate as of the most recent stable state and is sufficient for bootstrap *at* a stable state. During an in-flight transition — between stable states — it continues to show the last stable state; it is not updated mid-transition.

The in-flight position (what is mid-transition, and what remains to reach the next stable state) is carried by the **Repository Continuity Artifact**. A bootstrapping session therefore reads both: the Status Artifact for the last stable state, and the Repository Continuity Artifact for any in-flight work. The Status Artifact is not stale during a transition — it is the stable-state view by design, and bridging the transient interval is the continuity artifact's role.

## Failure and remediation paths

Three remediation entry points: **Bootstrap Failed** (inconsistent repository), **Phase Gate Fail**, and **Release/Status mismatch**. Each routes through a Remediation excursion whose destination is the interrupted state once its blocking preconditions are restored.

> *Example (GHES): a session bootstrapped after the repository version drifted (a release tag without a reconciled Status Artifact). Bootstrap verification detected the mismatch, remediation reconciled the Status Artifact, and work resumed at the interrupted state.*

## Traceability

Every construct here is either grounded in a decision or principle, or is explicitly evolvable design that nothing foundational depends on:

- **Continuity constructs** — session lifecycle, bootstrap, stable/transient, the two continuity mechanisms, the continuity rule, the universal postcondition, repository-provable state — implement **MADR-0001** and principles **P2, P3, P4, P7**.
- **Baseline & refinement constructs** — immutable baselines, the baseline and architecture-version counters, the Refinement transition, Baseline Publication — implement **MADR-0002** and principle **P5**.
- **Human authority & neutrality** — the agent-neutral framing, human-owned transitions, no inter-consumer channel — implement principle **P1**.
- **Decomposition topology** — the two-lifecycle shape, the work-item and phase state sets, the Milestone-Complete predicate, and the release / repository-version convention — is **evolvable design**. It is one implementation consistent with the decisions above; no ADR or principle depends on its specific shape, so it may change without reopening a decision. (MADR-0002 deliberately does *not* decide it.)

## Relationship to prompts

Prompts and skills are **implementations of transitions**, formalized only after this model is approved. Each transition names its precondition (source-state invariant), inputs, outputs, postcondition (target-state invariant, including the universal postcondition), consumer (legal next transitions), and failure route. Prompts are validated against this model, not the reverse.
