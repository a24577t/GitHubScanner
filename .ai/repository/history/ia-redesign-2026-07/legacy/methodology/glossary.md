---
status: accepted
---

# Methodology Glossary

**Status: accepted.** The vocabulary of the AI-assisted engineering lifecycle. Terms are project-independent; where a project instantiates a term, that instantiation is marked *Example* and is not part of the definition. `_Avoid_` lines flag usages that reintroduce coupling or ambiguity the model removed. The vocabulary is also **agent-neutral**: it names no AI assistant, because roles are assigned by the human architect and may change.

---

**Repository**
The authoritative record of project state: accepted decisions, the architecture baseline, specifications, the Status Artifact, and committed work. The single source of truth ([MADR-0001](adr/0001-repository-authoritative-continuity.md)).

**Work Item**
The unit of deliverable work with its own lifecycle instance. Many instances coexist at different stages.
_Avoid_: "vertical slice" as a methodology term — that is one project's instantiation.
> *Example (GHES): a vertical slice.*

**Phase**
A project-wide stage that groups work items and ends at a milestone with a phase gate and, on pass, a new baseline.
> *Example (GHES): Phase 2 — Architecture Validation Sequence.*

**Milestone-Complete**
The predicate that holds when every work item in a phase is Work-Item Complete. It enables the phase-gate transition.
_Avoid_: treating Milestone-Complete as a durable state — it is a derived predicate, never occupied.

**Architecture Baseline**
The authoritative, versioned, **immutable** snapshot of the accepted architecture; once published it is never edited, and a later baseline consolidates accumulated refinements ([MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md)).

**Architecture Version**
The monotonic version of the architecture, advanced by Refinement between baselines. A counter recorded in repository artifacts, not a state.

**Baseline Version / Repository Version**
Monotonic counters produced by baseline publication and by release (tags), respectively. Recorded in artifacts; not states.

**Status Artifact**
The repository artifact that records the current lifecycle state, current objective, open items, and version counters — the project's "program counter." Keeping it accurate is the universal postcondition of every transition to a stable state.
> *Example (GHES): `.ai/architecture/STATUS.md`.*

**ADR (Architecture Decision Record)**
An append-only record of one consequential, hard-to-reverse decision and its rationale. Two kinds:
- **Discovery ADR** — a decision made while first establishing an architecture.
- **Refinement ADR** — a decision that clarifies or resolves a gap between accepted ADRs after a baseline. Accepted ADRs are never edited in place; a refinement is a new ADR ([P5](principles.md)).

**Methodology ADR (MADR)**
An ADR in the methodology's own decision register, kept separate from any project's architecture ADRs so the process evolves independently ([P6](principles.md)).

**Transition**
A guarded move between lifecycle states, implemented by a prompt or skill. Declares precondition (source-state invariant), inputs, outputs, postcondition (target-state invariant), consumer (legal next transitions), and failure route.

**Precondition / Postcondition**
A precondition is a *verifiable predicate* over repository artifacts that must hold for a transition to run ([P3](principles.md)). A postcondition is the invariant true after it; every transition to a stable state inherits the universal postcondition "the Status Artifact is accurate."

**Stable State**
A state in which the repository is internally consistent, all durable work is committed, and the Status Artifact is accurate. Safe to bootstrap from; a session may clean-close here.

**Transient State**
Any non-stable state. Mid-work; resuming it requires a Repository Continuity Artifact.

**Session**
One working session of a single AI assistant in a role assigned by the human architect. Has its own lifecycle: bootstrap, work, close (clean, or by emitting a Repository Continuity Artifact).

**Bootstrap**
The transition that establishes a session's context by independently reading and verifying repository state — never by trusting prior chat, another assistant's context, or an unverified continuity artifact (MADR-0001).

**Repository Continuity Artifact**
The model's one transient continuity mechanism: a *committed*, non-authoritative project artifact that carries only the uncommitted in-flight intent needed to resume a transient state — what a session was doing and what remains — for any future engineer or consumer. It points at committed work rather than restating it, carries only information not yet represented in the authoritative record (MADR-0001 D3), and disappears once that intent becomes committed authoritative state. The repository always prevails over it.
_Avoid_: treating it as authoritative; letting it restate committed architecture, specs, ADRs, or Status, or become a second summary of committed history (that belongs to authoritative artifacts — see MADR-0002); a bare, unqualified "handoff."

**Conversation Continuity Artifact** *(outside the methodology model)*
A private bootstrap artifact for a specific consumer. It exists solely to restore that consumer's conversational context. It is never authoritative, never repository state, never an inter-consumer communication mechanism, and is intentionally outside the project synchronization model. The lifecycle neither defines nor depends on it; another consumer may have none, or a different mechanism. Listed here only to keep it distinct from the Repository Continuity Artifact.
_Avoid_: treating it as project state or a synchronization mechanism; providing it to a different consumer; naming a specific assistant except inside a prompt intentionally written for that consumer.

**Refinement**
The first-class transition that records a post-baseline decision (a Refinement ADR), updates architecture artifacts, and advances the Architecture Version without publishing a new baseline. Whether accumulated refinement triggers a new baseline is a deferred publication-policy decision.

**Remediation**
An excursion that restores the preconditions a blocked transition required, then returns to the *interrupted* state — not the nearest stable state. The excursion is the repair; the destination is the state that was blocked.
