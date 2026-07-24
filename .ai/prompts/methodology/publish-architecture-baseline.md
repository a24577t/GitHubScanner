# Architecture Baseline Publishing Prompt

## Purpose

A major project phase has successfully completed.

The Phase Gate Review has determined that the project is ready to advance.

Your responsibility is to publish the approved architectural milestone.

The primary artifact produced is a new **Architecture Baseline** that becomes the authoritative architectural snapshot for the completed phase.

Publish the authoritative architectural state of the repository and prepare the repository to become the sole source of truth for subsequent engineering work.

This prompt assumes the architecture has already been approved.

Publication reflects approved architecture.

It never:

- changes architecture
- creates architecture
- interprets unresolved decisions
- modifies ADRs
- creates specifications
- creates implementation artifacts

---

# Preconditions

Execute this prompt only after:

- Architecture Consolidation is complete.
- A **Phase Gate Review Record** exists and returned **PASS** or **PASS WITH CONDITIONS**.
- Architectural decisions have been accepted.

If these conditions are not satisfied, stop and report that the repository is not ready for publication.

---

# Inputs

Review the repository before beginning publication. Previous conversations may provide historical context but must not override repository content.

At minimum review:

- `.ai/architecture/STATUS.md`
- `.ai/architecture/domain-model.md`
- `.ai/architecture/architecture-principles.md`
- `CONTEXT.md`
- Relevant ADRs
- Phase Gate Review Record

Also review when available:

- Previous Architecture Baseline
- Architecture Discovery Brief (historical only)
- Repository Continuity Artifact (only when unpublished work exists)

Review only the artifacts necessary to publish the completed architectural milestone.

---

# Publication Authority

Publication does not create architecture.

Publication reflects architecture that has already been approved.

If architectural uncertainty exists:

stop publication.

---

# Determine the Baseline Version

Locate the most recent Architecture Baseline.

Examples:

- architecture-baseline-v1.md
- architecture-baseline-v2.md
- architecture-baseline-v3.md

Publish the next sequential version.

Never overwrite an existing baseline.

Architecture Baselines are immutable publications.

Never edit an existing baseline.

Corrections are published in the next baseline.

---

# Responsibilities

## 0. Consume the Phase Gate Review Record

Publication **consumes** the Phase Gate Review Record as its proving artifact; it does not re-perform the gate. Verify:

- the Phase Gate Review Record exists and returned PASS or PASS WITH CONDITIONS;
- required architecture artifacts and references still exist and resolve;
- **no new inconsistency has been introduced since** the Phase Gate Review Record was produced.

Do not re-audit architectural integrity — the gate already established it. If the record is missing, or a new inconsistency is found, report it and stop publication. Do not repair repository state during publication.

## 1. Publish the Architecture

Produce a concise but complete description of the approved architecture.

The Architecture Baseline should summarize the architecture without replacing the ADRs.

Reference ADRs.

Do not reproduce ADR content.

**Consolidate refinements (MADR-0002).** The new baseline consolidates **every accepted refinement since the previous published baseline** into a single immutable snapshot. State this explicitly in the baseline — list the refinements consolidated and the Architecture Version they cumulatively produced — so that MADR-0002's append-only-then-consolidate evolution is directly observable. The previous baseline is never edited; this baseline supersedes it.

Capture:

- Executive Summary
- Project Mission
- Current Phase
- Architecture Overview
- Governance Model
- Domain Overview
- Architecture Principles
- Current Scope
- Deferred Scope
- ADR Index
- Consolidated Refinements Since Previous Baseline
- Recommended Reading
- Next Baseline Trigger

---

## 2. Preserve Architectural Integrity

Do not introduce:

- new architecture
- new ADRs
- new terminology
- new principles
- new requirements

The Phase Gate Review Record already established architectural integrity; do not re-audit it. If a **new** contradiction — one introduced since the record was produced — is discovered:

- report it
- identify impacted ADRs
- stop publication

Do not resolve architectural contradictions during publication.

---

## 3. Publish Repository State

Update `STATUS.md` to reflect the newly published architectural milestone. Update only the **architecture-side** state:

- Completed Phase
- Current Phase
- Current Architecture Baseline
- Baseline Version
- Architecture Version
- Next Milestone

Do **not** update Repository Version, and do not touch Git tags or releases — those belong exclusively to Project Release, which reconciles them afterward.

STATUS.md should remain concise and represent the current repository state. Do not add architectural narrative to STATUS.md; it is a concise project status document, not an architecture document.

---

## 4. Prepare Future Sessions

Verify that the repository is ready for a future Session Bootstrap.

Confirm:

- STATUS correctly references the latest Architecture Baseline.
- Repository navigation is correct.
- Architecture artifacts remain internally consistent.
- Verify that a new engineering session can begin using only the repository.

The repository should contain sufficient authoritative information that previous chat history is unnecessary.

The repository should become the authoritative project memory.

---

## 5. Architecture Version

Determine the new **Architecture Version** for this baseline and record it in `STATUS.md` (Responsibility #3) and the baseline metadata. Explain the version choice.

Architecture Version is owned by Baseline Publication. **Repository Version, Git tags, and GitHub Releases are not** — they belong exclusively to Project Release, which runs afterward and consumes this published state. Do not recommend or produce them here.

---

# Required Sections

Every Architecture Baseline should contain:

1. Metadata
2. Executive Summary
3. Project Mission
4. Current Phase
5. Architecture Overview
6. Architecture Diagram
7. Architecture Principles
8. Domain Overview
9. ADR Index
10. Current Scope
11. Deferred Scope
12. Repository Navigation
13. Open Architectural Items
14. Recommended Reading
15. What This Baseline Is
16. What This Baseline Is Not
17. Next Baseline Trigger
18. Consolidated Refinements and Changes Since Previous Baseline (when applicable)

---

# Metadata

Every Architecture Baseline should begin with metadata similar to:

- Baseline Version
- Status
- Published Date
- Phase Completed
- Current Phase
- Supersedes
- Superseded By
- Architecture Version
- Related ADRs

---

# Repository Navigation

The published Architecture Baseline becomes the primary onboarding document.

Recommended reading order:

1. STATUS
2. Latest Architecture Baseline
3. Domain Model
4. Architecture Principles
5. CONTEXT
6. Relevant ADRs
7. Specifications

---

# Constraints

Do not:

- redesign the architecture
- re-evaluate the architecture
- rewrite ADRs
- create specifications
- generate implementation details
- create implementation tasks
- modify architectural history or edit any published baseline
- recommend or produce a Repository Version, a Git tag, or a GitHub Release (those are owned by Project Release)

This prompt publishes architecture.

It does not evolve architecture, and it does not perform repository releases.

---

# Output

Publish:

`.ai/architecture/architecture-baseline-v<next>.md` — the immutable baseline, consolidating all accepted refinements since the previous baseline.

Update the architecture-side of:

`.ai/architecture/STATUS.md` — Completed/Current Phase, Current Architecture Baseline, Baseline Version, Architecture Version, Next Milestone.

Leave the repository in a state Project Release can consume. Do not produce a Repository Version, Git tag, or GitHub Release — those are owned by Project Release.

---

# Success Criteria

Successful publication means:

- the Architecture Baseline becomes the authoritative onboarding document;
- STATUS accurately reflects the newly published milestone;
- repository navigation is correct;
- the repository is ready for future Session Bootstrap;
- the published state is ready for Project Release to consume (Baseline Publication produces no Repository Version, tag, or release);
- the repository fully represents the approved architectural state without relying on previous chat history.

The repository should become the authoritative memory of the project.

Successful publication establishes a new architectural starting point.

Future engineering work should begin from the published repository state rather than unpublished conversation context.