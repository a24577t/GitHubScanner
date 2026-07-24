# Create Repository Continuity Artifact

## Purpose

A session is ending while uncommitted, in-flight project work remains. Produce a **Repository Continuity Artifact** — the temporary bridge that lets the next session resume that work.

The Repository Continuity Artifact preserves **only uncommitted, in-flight project intent** that is not yet represented by authoritative repository artifacts. It **points at** authoritative artifacts for context; it never restates them, and it is **never** an alternate representation of project history.

It bridges repository state across an **interrupted transient session** — not architectural history. It is a temporary working artifact: not an architecture document, not a specification, not a design document, not a permanent project record.

## Precondition

Produce a Repository Continuity Artifact **only when a session ends while uncommitted project work remains**. A clean session close — the repository internally consistent, all durable work committed, the Status Artifact accurate — emits **no** Repository Continuity Artifact.

## What it may and may not contain

**May contain:**

- unpublished work in progress;
- outstanding architectural or implementation decisions;
- unresolved questions;
- the intended next activity;
- references to authoritative repository artifacts that provide necessary context.

**Must not contain** — each of these is committed, authoritative content that belongs elsewhere; point to it, never restate it:

- a summary of completed work;
- a summary of repository state, or a second representation of STATUS;
- a reconciliation of changes since the previous baseline;
- a release summary;
- an alternate project history.

## Inputs

- STATUS.md (reference only)
- The latest Architecture Baseline (reference only)
- Previous Repository Continuity Artifact (if one exists)
- The uncommitted, in-flight work of the ending session

Do not reread architecture already captured by authoritative artifacts unless required to describe the uncommitted work.

## Responsibilities

### 1. Identify Uncommitted Work

List work that has been done or discussed but has **not** yet become repository state — pending document updates, prompt revisions, ADR reviews, specifications, or implementation work. Actionable, uncommitted items only.

### 2. Identify Outstanding Decisions

List architectural or methodological decisions and unresolved questions that remain open. For each: the decision required and the recommended next step. If none remain, state `None`.

### 3. Recommend the Next Activity

Identify the single best starting point for the next session to resume the in-flight work.

## Output

Produce, for **human review and commit** — the human authorizes what becomes repository state; this prompt does not commit automatically:

`.ai/working/repository-continuity.md`

Containing:

- **Created** — date
- **Resume Context** — references (pointers, not summaries) to the authoritative artifacts the next session needs: STATUS, the latest baseline, relevant ADRs
- **Work Not Yet Committed** — the uncommitted in-flight work
- **Outstanding Decisions** — `None`, or the open decisions and questions
- **Recommended Next Activity** — one starting point
- **Notes** — optional; only what helps the next session resume

## Lifecycle

The Repository Continuity Artifact is a temporary, single-use bridge:

1. **Created** when a session ends with uncommitted in-flight work.
2. **Consumed once** by the next Session Bootstrap, which resumes that work.
3. **Retired** as soon as its content becomes authoritative repository state (committed) or is intentionally discarded — at which point it is removed and no longer participates in any future bootstrap.

It bridges a single interrupted session; it does not accumulate, persist across resumptions, or become an enduring project artifact. A resuming session that is itself interrupted retires the consumed artifact and emits a fresh one.

It is never authoritative over Architecture Baselines, ADRs, the Domain Model, Architecture Principles, or STATUS.

## Constraints

Do not:

- restate or summarize committed work, accepted decisions, released architecture, or repository state — point at the authoritative artifacts instead;
- duplicate STATUS, the Architecture Baseline, or ADRs;
- reconcile changes since the previous baseline, or produce a release summary;
- rewrite or redesign architecture;
- create implementation tasks or invent future work;
- commit the artifact automatically — produce it for human review and commit.

The Repository Continuity Artifact exists only to bridge uncommitted, in-flight work between sessions.

## Success Criteria

- The artifact contains only uncommitted, in-flight intent and pointers to authoritative artifacts — never a summary of committed history or state.
- A future Session Bootstrap can read it quickly and know what remains uncommitted, which decisions are open, and where to resume.
- Its lifecycle is explicit: created on interruption, consumed once, retired when its content becomes authoritative or is discarded.
- It never becomes a permanent or authoritative project artifact.
