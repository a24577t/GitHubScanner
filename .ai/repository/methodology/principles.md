---
status: accepted
---

# Methodology Principles

**Status: accepted.** Enduring constraints on the AI-assisted engineering lifecycle. Principles state *what must always hold*; the `adr/` register records the *specific consequential decisions*. **Principles constrain; ADRs decide.** Each principle is therefore one of two kinds — a **foundational governance principle** that stands on its own (P1, P6), or a principle **supported by one or more methodology ADRs** (P2–P5, P7), noted inline. A foundational principle is not a candidate for promotion to an ADR; promoting governance values to ADRs would collapse the distinction between values and decisions.

The principles are project-independent. A project applying the methodology is an implementation example, never a dependency.

---

**P1 — Human-Owned Design Authority.**
AI assistants collaborate with the project through the human architect. Repository artifacts record decisions and their rationale, not which assistant proposed them. Roles are assigned by the human architect and may change at any time — an assistant may be replaced, added, or reassigned without any change to the methodology. No assistant relies on another assistant's conversation history, and there is no consumer-to-consumer channel: project continuity is achieved only through authoritative repository artifacts and the Repository Continuity Artifact. A consumer may privately restore its own conversational context by whatever means it chooses, but that is never a project continuity mechanism and never a channel to another consumer. One assistant's reasoning reaches the project solely when the human architect converts it into authoritative repository state.
*Why:* decisions and their accountability belong to people; assistants are interchangeable contributors in mutable roles, and the record must not depend on any one of them or on a private channel between them.
*Constrains the model:* the methodology is agent-neutral — it names no assistant except inside a prompt intentionally written for one consumer; repository artifacts and continuity artifacts carry no agent attribution; the design authority for every transition is the human, not the prompt.
*(Foundational governance principle — deliberately not an ADR. Consequential decisions *derived from* P1 may be recorded as ADRs; P1 itself is a value that constrains, not a decision.)*

**P2 — The repository is authoritative memory.**
Project state lives in the repository. Chat history is never required to continue, and is never authoritative.
*Why:* the only durable, inspectable, shareable record is the repository.
*Corollary of [MADR-0001](adr/0001-repository-authoritative-continuity.md).*

**P3 — Preconditions are verifiable; transitions fail loud.**
A transition establishes that its source state actually holds — as a checkable predicate over repository artifacts — or it refuses with a clear explanation. It never proceeds on assumption.
*Why:* an unverifiable precondition fails silently, which is how state drift enters undetected.
*Corollary of MADR-0001; mirrors the product's "fail loud on ambiguity" stance.*

**P4 — Clean close or explicit continuity artifact.**
A session closes without emitting a Repository Continuity Artifact only when the repository is internally consistent, all durable work is committed, and the Status Artifact accurately represents the current state and next objective. Otherwise it emits one.
*Why:* the next session must be able to resume from the repository alone, or from the repository plus a bounded Repository Continuity Artifact — never from lost context.
*Corollary of MADR-0001 (the ratified continuity rule).*

**P5 — Refinement over rewrite.**
A decision discovered after a baseline is recorded as a *new* refinement ADR. Accepted ADRs are never edited in place; forward navigation to a refinement is carried by the next baseline, since an accepted ADR cannot point forward to one.
*Why:* the decision record must be append-only to remain trustworthy — editing an accepted decision in place is the governance equivalent of rewriting published evidence.
*Constrains the model:* Refinement is a first-class transition with defined pre/postconditions.
*Grounded in [MADR-0002](adr/0002-immutable-baselines-append-only-refinement.md) (immutable baselines, append-only refinement).*

**P6 — The methodology is project-independent.**
The methodology evolves separately from any architecture it produces. A project appears as an implementation example, never as a dependency. The methodology should be extractable to its own repository without architectural change.
*Why:* the process is reusable across projects; coupling it to one project's artifacts would prevent reuse and entangle two independently-evolving things.
*Constrains the model:* these documents reference a concrete project only as a marked *Example*, never in a definition.

**P7 — Repository-provable state.**
A lifecycle state exists in the model only if a repository artifact proves it; a condition that cannot be established from repository evidence is not a state and is never treated as established.
*Why:* a state the repository cannot prove cannot be verified at bootstrap, so admitting it would reintroduce reliance on unverifiable context — the very thing [MADR-0001](adr/0001-repository-authoritative-continuity.md) forbids.
*Corollary of MADR-0001 (repository authoritative) and P3, but distinct: P3 governs when a transition may fire; P7 governs which states the model may admit at all.*
