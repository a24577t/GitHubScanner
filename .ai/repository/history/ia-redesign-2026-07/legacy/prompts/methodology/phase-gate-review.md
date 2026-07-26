# Phase Gate Review

## Purpose

Evaluate whether the repository has reached a stable architectural milestone suitable for advancing to the next stage.

Your responsibility is to determine whether the project is ready to advance to the next phase.

This prompt is an architectural review gate.

It evaluates the current state of the repository.

It does **not** modify repository artifacts.

It does **not** redesign the architecture.

It does **not** publish the Architecture Baseline.

It determines whether the current phase has achieved its objectives and whether the repository is ready for the next architectural milestone.

---

# Inputs

Review the repository before beginning.

At minimum review:

- `.ai/architecture/STATUS.md`
- `.ai/architecture/domain-model.md`
- `.ai/architecture/architecture-principles.md`
- `CONTEXT.md`
- `docs/adr/`

When appropriate also review:

- Architecture Discovery Brief
- Current specifications
- Session summaries
- `OPEN_ITEMS.md` (if present)

Review only the artifacts necessary to evaluate the completed phase.

---

# Precondition

This transition (Phase Active → Phase Gate) runs only when its precondition holds: the phase's **Milestone-Complete** predicate is true — every work item in the phase has reached its completed state.

Verify this from repository state **before** any qualitative evaluation. If a work item is not complete, the precondition is unmet: report which work items are incomplete and **stop — issue no readiness decision**. An incomplete milestone is a fail-loud precondition failure, not a FAIL readiness outcome. The gate evaluates a *completed* milestone's architectural readiness; it does not substitute for milestone completion.

---

# Responsibilities

## 1. Verify Phase Objectives

The Precondition above has already established that the phase's **work items** are complete; this step documents the **objective** outcomes for the Phase Gate Review Record. An objective that is genuinely *Not Completed* because a work item is unfinished is a precondition failure — return to the Precondition and stop.

Classify each objective as:

- Complete
- Partially Complete
- Deferred
- Not Completed

Explain any incomplete objectives.

---

## 2. Verify Architectural Integrity

Confirm that the repository accurately reflects the approved architecture.

Review:

- ADR consistency
- Domain Model consistency
- Architecture Principles
- Terminology
- Architectural traceability

Identify:

- contradictions
- undocumented architectural changes
- missing architectural decisions
- ambiguity requiring future clarification

Do not redesign the architecture.

---

## 3. Identify Blocking Issues

Identify issues that affect progression to the next phase.

Classify each issue as:

### Blocking

The project should not advance until resolved.

### Non-Blocking

The project may advance.

The issue should be documented or deferred.

Examples include:

- architectural debt
- specification debt
- documentation gaps
- implementation assumptions
- environmental unknowns

---

## 4. Assess Readiness

Determine overall readiness.

Possible outcomes:

- PASS
- PASS WITH CONDITIONS
- FAIL

Definitions:

### PASS

Phase objectives have been achieved.

Architecture remains internally consistent.

No blocking issues remain.

Architecture is ready to advance.

Publication is appropriate if a new architectural milestone has been reached.

### PASS WITH CONDITIONS

A **qualified Pass**. The lifecycle transition remains binary: PASS and PASS WITH CONDITIONS are both a Pass and make the phase eligible to proceed to Baseline Publication; only FAIL routes to Remediation. PASS WITH CONDITIONS is a human-facing classification, not a third lifecycle branch.

The conditions are structured metadata attached to the Pass result. They travel forward as **required inputs to Baseline Publication**. Because this is a Pass, every condition is **non-blocking**: publication always proceeds. A condition that would block publication is a blocking issue, and therefore a **FAIL** — not a Pass with Conditions.

Every condition must identify:

- the condition
- affected repository artifact(s)
- recommended resolution timing (during publication, after publication, or next phase)

### FAIL

Blocking issues remain.

The current phase must continue.

Explain the reasoning.

---

## 5. Recommend the Next Phase

Identify the appropriate next phase.

Examples:

- Architecture Discovery
- Architecture Consolidation
- Vertical Slice Specification
- Implementation
- Testing
- Enterprise Pilot

Explain why this is the correct next step.

## 6. Recommended Next Action

The Phase Gate has exactly two lifecycle outcomes, so recommend exactly one:

- **Pass** (including Pass with Conditions) → proceed to **Baseline Publication** (`publish-architecture-baseline.md`), carrying any conditions forward.
- **Fail** → **Remediation**: the current phase continues until the blocking issues are resolved.

Do not recommend work-item or session transitions here (specification, implementation, and the like). Those follow later, from the next Phase Active state, and are outside this gate's scope.

## 7. Methodology Observations

Capture improvements to the project's engineering process.

These observations are not architectural issues and must not affect the readiness decision.

That keeps methodology evolution separate from architecture evaluation.
---

# Output

**Produce the Phase Gate Review Record** — the proving artifact for the Phase Gate state. This prompt *produces* the record as its output; it does **not** commit or publish it. The human architect reviews the record and commits it (commit / PR / merge), at which point the repository proves the Phase Gate state. **Produce the proving artifact; do not publish it** — evaluation stays separate from repository mutation.

The Phase Gate Review Record contains:

## Current Phase

## Phase Objectives Assessment

## Architecture Integrity Assessment

## Blocking Issues

## Non-Blocking Issues

## Readiness Decision

PASS

PASS WITH CONDITIONS

or

FAIL

## Recommendation

If the decision is:

### PASS

Recommend running:

`publish-architecture-baseline.md`

### PASS WITH CONDITIONS

Recommend documenting the listed conditions during Architecture Baseline publication before advancing.

### FAIL

Recommend continuing the current phase until blocking issues are resolved.

---

# Constraints

Do not:

- modify repository files
- publish an Architecture Baseline
- update STATUS.md
- create ADRs
- redesign the architecture
- generate implementation tasks
- recommend Git tags or releases

This prompt evaluates the repository.

Do not recommend changes solely because a better design is possible. Evaluate only whether the repository satisfies the current architecture.

It never changes repository state.

---

# Success Criteria

The review should answer one question:

**Is the project ready to advance to the next phase?**

The output should provide a clear, well-supported recommendation while preserving the separation between:

- evaluation (this prompt)
- publication (Architecture Baseline)
- implementation (future phases)

The result should leave no ambiguity about whether the next prompt should be executed.