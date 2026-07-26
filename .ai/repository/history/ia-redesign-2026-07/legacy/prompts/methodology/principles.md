# Methodology Principles

These principles govern how architecture is created, reviewed, documented, and evolved.

They are independent of the architecture being designed and apply to every project using this methodology.

---

## Repository as Project Memory

The repository is the authoritative memory of the project.

Architecture must never depend on previous chat sessions.

---

## Single Source of Truth

Every concept should have one authoritative artifact.

Avoid maintaining the same information in multiple places.

---

## Single Responsibility

Every document and every prompt should have one obvious responsibility.
An artifact is any maintained element of the methodology, including documents, prompts, ADRs, specifications, and other repository content.

If responsibilities overlap, simplify the methodology.

---

## Clear Ownership

Every living document must have one obvious maintainer.

Ownership should be apparent from the methodology.

---

## Evaluate or Change State

A prompt must either evaluate repository state or change repository state.

It must never do both.

---

## Minimal Documentation

Do not create documents whose information can be derived from authoritative artifacts.

Every document must justify its existence.

---

## Traceability

Architectural statements must trace to Architecture Principles, ADRs, or other approved architectural artifacts.

Do not invent undocumented architecture.

---

## Incremental Evolution

Architecture evolves through small, explicit decisions.

Prefer refinement over redesign.

---

## Immutable Milestones

Architecture Baselines are immutable architectural snapshots.

They document approved architecture at a point in time and are never rewritten.

---

## Simplicity

Prefer fewer artifacts with clear ownership over many overlapping documents.

Reduce process complexity whenever architectural integrity can be preserved.

---

## Explicit Intent

Do not infer architectural intent.

When intent is unclear, record the ambiguity rather than inventing a decision.

---

## Preserve History

Architectural history is valuable.

Correct mistakes by creating new decisions rather than rewriting historical artifacts.

Historical documents remain part of the project's evolution.