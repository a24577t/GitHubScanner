---
status: accepted
register: methodology
---

# MADR-0001 — Repository-Authoritative Continuity

The methodology is exercised by one or more AI assistants across many sessions, in roles assigned by the human architect that may change at any time, on machines whose conversational memory is not durable and is never shared between assistants. Continuity therefore cannot rest on any assistant's chat history. This ADR fixes the foundational decision that makes a session-independent, agent-neutral lifecycle possible. It is the axiom; the lifecycle model (`lifecycle-model.md`) is one design that implements it and may evolve without reopening this decision.

## Decision

**The repository is the authoritative record of project state. Continuity between sessions is achieved through that record, independently verified before it is relied upon.**

1. **Repository artifacts are authoritative.** Nothing outside the repository is authoritative.
2. **Every session independently verifies repository state before relying on it.** A session never relies on another session's conclusions, another consumer's context, or any unverified aid.
3. **Any continuity aid outside the authoritative record is subordinate to it.** It may carry only information not yet represented in the authoritative record. When a conflict exists, the repository prevails and the discrepancy is surfaced rather than silently resolved.
4. **Context private to a single consumer is not project state.** It reaches the project only when the human architect records it through authoritative repository artifacts.

## Scope

This ADR establishes the continuity principles only. The lifecycle model (`lifecycle-model.md`) defines the concrete mechanisms that satisfy them — including the Repository Continuity Artifact, the bootstrap transition, the stable/transient distinction, and future refinements. The implementing mechanisms, the consumer-specific and platform-specific concerns, and the rationale for them belong to the lifecycle model and its supporting documentation, not to this decision.

## Considered options

**Rely on assistant conversation memory or a consumer-to-consumer context channel** — rejected. It is not durable, not shared safely across assistants, and not inspectable or auditable. A methodology that depends on it cannot survive a new session, a different assistant, or a lost environment, and it would let one consumer's private reasoning influence the project without passing through the human architect. This was encountered in practice: a session whose assistant memory was lost continued correctly *because* it re-derived context from the repository.

**Treat a continuity aid as a source of truth** — rejected. It would create two authorities that can disagree, with no rule for which wins, and would let uncommitted narrative override committed decisions. Subordinating every continuity aid to the authoritative record, which always prevails, keeps exactly one authority.

## Consequences

- The lifecycle model must distinguish states from which a session may resume using the authoritative record alone from those that require a continuity aid, and must express every precondition as a predicate verifiable against repository artifacts.
- Several methodology principles are corollaries of this decision: *the repository is authoritative memory* (P2), *preconditions are verifiable and transitions fail loud* (P3), and *a session closes clean or else emits a continuity aid* (P4).
- Every transition that returns the repository to a resumable state inherits a universal postcondition: the Status Artifact accurately reflects repository state. Otherwise the next session's verification fails.
- Inter-consumer synchronization flows only through the authoritative record. Agent-neutrality, mutable roles, and the absence of a consumer-to-consumer back-channel are consequences of this decision together with Human-Owned Design Authority (P1), requiring no separate record.
- This decision is project-independent and agent-neutral. It constrains any project the methodology governs and any assistant in any role the human architect assigns.
