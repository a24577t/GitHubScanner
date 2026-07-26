# Methodology Operator Guide

**Type:** operational routing aid. **Subordinate to** the lifecycle model and the prompts.

This guide answers one question: *given my current situation, which methodology prompt — if any — do I run next?* It does **not** define the lifecycle (see [`../../methodology/lifecycle-model.md`](../../methodology/lifecycle-model.md)), restate principles (see [`../../methodology/principles.md`](../../methodology/principles.md)), or describe what each prompt does internally (see the prompt files). Where this guide disagrees with those sources, **they prevail** — this is a derived summary and is fixed to match, never the reverse.

State names (*Phase Active*, *Phase Gate*, *Context Established*, *Work-Item Complete*, …) are used exactly as the lifecycle model defines them. Preconditions and outcomes below are summarized from the prompt files; the prompt itself is authoritative for its own contract.

Not every transition runs a prompt. Some are performed by human action or by re-running an existing prompt; those are marked **no prompt** and collected at the end.

**Repository preparation vs. bootstrap.** The gate, release, status-reconciliation, and session-close transitions here (S3–S10) *prepare* repository state — they **produce** a repository that is authoritative and current, including before a context refresh for the next collaborator. [`session-bootstrap.md`](session-bootstrap.md) (S1) does the opposite: it **consumes and verifies** that already-prepared state, read-only, and never prepares it. The collaboration-avatar refresh is a **separate, non-repository step** owned by the outgoing collaboration ([`../../collaboration/collaboration-avatar-generator.md`](../../collaboration/collaboration-avatar-generator.md)), not by any transition here.

## Start here every session

Begin at **S1**. After any prompt completes, or whenever you reach a decision point, return here, match your situation, and act. Bootstrap's output already reports the current objective and next milestone; this guide turns *"objective + situation"* into *"next prompt."*

## Index

| # | Situation | Run | Next state |
|---|-----------|-----|------------|
| S1 | Starting or resuming a session | [`session-bootstrap.md`](session-bootstrap.md) | Context Established / Bootstrap Failed |
| S2 | Bootstrap (or a transition) reported failed checks | **no prompt** — resolve, then re-run the failed transition | interrupted state resumes |
| S3 | Architecture discovery cycle completed; consolidate | [`architecture-consolidation.md`](architecture-consolidation.md) | Pre-Baseline (per Discovery Status) |
| S4 | A phase milestone is believed complete | [`phase-gate-review.md`](phase-gate-review.md) | Phase Gate |
| S5 | Gate returned PASS or PASS WITH CONDITIONS | [`publish-architecture-baseline.md`](publish-architecture-baseline.md) | Phase Active (new baseline) |
| S6 | Gate returned FAIL | **no prompt** — resume work, re-run S4 later | Phase Active (phase continues) |
| S7 | An intentional repository release is being prepared | [`project-release.md`](project-release.md) | Release Plan produced (transient) |
| S8 | A Release Plan is in hand | **no prompt** — human executes the plan | Release complete, bootstrap-safe |
| S9 | Session ending with uncommitted, in-flight work | [`create-repository-continuity.md`](create-repository-continuity.md) | Ended (continuity artifact emitted) |
| S10 | Session ending clean | **no prompt** — clean close | Ended (no artifact) |

## Situations

### S1 — Starting or resuming a session

- **Preconditions:** none beyond intent to begin or resume. Bootstrap runs its own verifiable checks over repository state; if a Repository Continuity Artifact is present for the state being resumed, bootstrap reads it as subordinate context.
- **Prompt(s):** [`session-bootstrap.md`](session-bootstrap.md).
- **Expected outcome:** a Session Context result — **Bootstrap Successful** (Context Established) or **Bootstrap Failed**, with any failed checks listed by artifact and discrepancy. Nothing is modified.
- **Next state:** *Context Established* → proceed to Working (perform work-item execution or move to whichever situation below matches your objective). *Bootstrap Failed* → **S2**.

### S2 — Bootstrap or a transition reported failed checks

- **Preconditions:** a *Bootstrap Failed* outcome, or any transition that stopped on an unmet precondition, with its failed checks / blocking issues listed (each naming the artifact and the discrepancy).
- **Prompt(s):** **none.** This is Remediation: the human resolves each listed discrepancy in the repository, then **re-runs the transition that failed** (for a bootstrap failure, re-run **S1**). Remediation returns to the interrupted state — it does not advance past it.
- **Expected outcome:** the previously failed checks now pass on re-run.
- **Next state:** the interrupted state resumes (typically *Context Established* after a bootstrap re-run).

### S3 — Architecture discovery cycle completed; consolidate before continuing

- **Preconditions:** the project is in architecture discovery (Pre-Baseline) and a discovery cycle has just completed. Do not continue discovery, accept ADRs, or begin specification until consolidation is reviewed.
- **Prompt(s):** [`architecture-consolidation.md`](architecture-consolidation.md).
- **Expected outcome:** a consistency review; updated Domain Model, glossary, and discovery brief; a **prepared (not created)** pull request; and a Discovery Status of *Continue Discovery*, *Architecture Baseline Established*, *Ready for Specification*, or *Ready for Implementation*. ADRs remain Proposed; nothing is committed.
- **Next state:** *Pre-Baseline* — continue discovery, or advance toward a baseline milestone, per the Discovery Status. The human reviews and commits the prepared PR.

### S4 — A phase milestone is believed complete

- **Preconditions:** the phase's **Milestone-Complete** predicate is true — every work item in the phase has reached its completed state. If a work item is not complete, the prompt stops and issues **no** readiness decision; that is a precondition failure (**S2**), not a FAIL.
- **Prompt(s):** [`phase-gate-review.md`](phase-gate-review.md).
- **Expected outcome:** a **Phase Gate Review Record** with a readiness decision of PASS, PASS WITH CONDITIONS, or FAIL. The record is produced, not committed; the human commits it.
- **Next state:** *Phase Gate*. PASS or PASS WITH CONDITIONS → **S5**. FAIL → **S6**.

### S5 — Gate returned PASS or PASS WITH CONDITIONS

- **Preconditions:** Architecture Consolidation is complete; a Phase Gate Review Record exists returning PASS or PASS WITH CONDITIONS; architectural decisions are accepted. Any conditions from a qualified pass travel forward as required inputs.
- **Prompt(s):** [`publish-architecture-baseline.md`](publish-architecture-baseline.md).
- **Expected outcome:** the next sequential **immutable Architecture Baseline**, consolidating accepted refinements since the previous baseline; the architecture side of the Status Artifact updated (Completed/Current Phase, Baseline Version, Architecture Version, Next Milestone). No Repository Version, tag, or release is produced.
- **Next state:** *Phase Active* on the new baseline; the published state is ready for Project Release to consume (**S7**, when a release is intended).

### S6 — Gate returned FAIL

- **Preconditions:** a Phase Gate Review Record with a FAIL decision and its blocking issues.
- **Prompt(s):** **none.** The current phase continues. Resolve the blocking issues through ongoing work-item execution, then re-run **S4** once the milestone is complete again.
- **Expected outcome:** blocking issues resolved; the milestone becomes re-eligible for the gate.
- **Next state:** *Phase Active* (the phase continues) → eventually **S4** again.

### S7 — An intentional repository release is being prepared

- **Preconditions:** internally consistent repository state and a human-authorized release scope. Type-conditional prerequisites, verified only when applicable: a phase-completion release requires a PASS / PASS WITH CONDITIONS Phase Gate Review Record; a baseline-milestone release requires the baseline already published. Verify only the prerequisites the determined release type requires.
- **Prompt(s):** [`project-release.md`](project-release.md).
- **Expected outcome:** a **Release Plan** (evaluation only) — release type and authorization, selected Repository Version, tag and GitHub Release recommendation, and the human execution order. No tags or releases are created; the Status Artifact is not reconciled by this prompt.
- **Next state:** the release is **transient and incomplete** until the plan is executed → **S8**.

### S8 — A Release Plan is in hand

- **Preconditions:** an approved Release Plan.
- **Prompt(s):** **none.** The human executes the plan in order: update the Status Artifact to the intended Repository Version and next objective; commit and merge that update; create the annotated tag from the intended commit; publish the GitHub Release; verify the tag, release metadata, and Status Artifact all agree.
- **Expected outcome:** the Repository Version is tagged, the Status Artifact is reconciled, and all three agree.
- **Next state:** *Phase Active*, release complete and **bootstrap-safe** — the next bootstrap's Repository-Version check passes.

### S9 — Session ending with uncommitted, in-flight work

- **Preconditions:** the session is ending while uncommitted, in-flight project work remains (a transient state, mid-transition). A clean, fully committed close does **not** produce this artifact — see **S10**.
- **Prompt(s):** [`create-repository-continuity.md`](create-repository-continuity.md).
- **Expected outcome:** `.ai/working/repository-continuity.md`, produced for human review and commit — carrying only uncommitted intent and pointers to authoritative artifacts, never a summary of committed work.
- **Next state:** session *Ended*; the artifact is consumed once by the next bootstrap (**S1**).

### S10 — Session ending clean

- **Preconditions:** the clean-close condition holds — the repository is internally consistent, all durable work is committed, and the Status Artifact accurately represents the current state and next objective.
- **Prompt(s):** **none.** Clean close; emit no continuity artifact.
- **Expected outcome:** the session ends leaving the repository fully resumable from its authoritative artifacts alone.
- **Next state:** *Ended*; the next session starts at **S1** from the repository alone.

## Transitions performed without a methodology prompt

These are intentional: they are handled by human action or by re-running an existing prompt, and add no operational concept.

- **Remediation (S2)** — the human resolves the failed checks and re-runs the transition that failed. Its destination is the interrupted state.
- **Phase-gate FAIL (S6)** — the phase continues through ongoing work; the gate is re-run when the milestone is complete again.
- **Release execution (S8)** — the human executes the Release Plan produced by `project-release.md`.
- **Clean session close (S10)** — a human action gated by the clean-close condition; no artifact is produced.
- **Work-item execution** — authoring a specification, generating implementation tickets, implementing, and verifying-and-merging are performed by project work-item tooling and human action, not by a methodology prompt. How that work crosses from decision to code — the decision gates, the halt-don't-decide rule, and the Architecture Conformance Review before merge — is described by the [Decision-Gated Implementation Lifecycle](../../methodology/decision-gated-implementation-lifecycle.md). The governance prompts above pick up at the phase and release boundaries.
