# Session Bootstrap

## Purpose

Begin a new working session by establishing accurate context **from the repository alone**. The repository is the authoritative record; prior chat context is never authoritative and is never required.

This prompt is **read-only and evaluation-only**: it discovers the repository's authoritative domains, runs verifiable checks over repository state, and produces a Session Context result. It creates, modifies, renames, moves, commits, or deletes nothing. It **consumes and verifies** repository state that prior transitions have already made authoritative and current; it does **not** prepare the repository for a refresh — closeout, gate, release, status, and reconciliation are the operator-guide's transitions, not this one.

## Outcomes

Bootstrapping has exactly **two** outcomes — no third state:

- **Bootstrap Successful** → Context Established; the session may proceed to Working.
- **Bootstrap Failed** → route to **Remediation**; the session does **not** proceed to Working.

A single failed check is a Bootstrap Failed. Bootstrap never repairs anything; it routes failures to Remediation.

## Artifact Source Selection

Establishing context requires the authoritative artifacts themselves, not a description of them. Because a consumer may lack direct repository access, the **source** of each artifact is fixed deterministically. This **applies** MADR-0001 (the repository is authoritative; every aid is subordinate and verified) — it does not reopen it.

1. **Load each required authoritative artifact from the repository at the revision governing the current work.**
2. **If repository access is unavailable, an explicitly provided copy may be used only when it is presented as a copy of a repository artifact.** Treat it as temporary transport of the authoritative artifact, never as an independent source of truth — subordinate to the repository (MADR-0001 D3).
3. **Never substitute** a conversational summary, assistant memory, an implementation report, or inferred content for the artifact.
4. **When repository access is restored, verify the provided copy against the repository version.** The repository prevails on any divergence, and the discrepancy is surfaced, never silently resolved (MADR-0001 D3).
5. **If neither the repository artifact nor an explicitly provided copy is available, report the artifact unavailable and leave guidance dependent on that artifact inactive** — never infer its contents.

## Establishing Context

Do **not** assume a fixed artifact list. Discover the repository's authoritative domains and establish the authority set from them. Required steps:

1. **Discover** the authoritative domains present in the repository.
2. **Verify** each required domain is internally consistent.
3. **Build** the authority set from the discovered domains.
4. **Apply** authority precedence across that set.
5. **Continue** only if every required domain establishes successfully; otherwise, Bootstrap Failed.

How a repository exposes its domains is repository-specific implementation — directory conventions, repository metadata, a future manifest, or another mechanism. This prompt states the requirement and remains **agnostic to the mechanism**.

> *Example (GHES): the discovered authority domains today are **architecture** (`.ai/architecture/`: the Status Artifact, the architecture baseline, domain model, principles, ADRs, `CONTEXT.md`), **methodology** (`.ai/methodology/`: MADRs, principles, the lifecycle model), and **standards** (`docs/standards/`: the Engineering Standards hub and the Python Coding Standard, with their enforcement stages — subordinate to the sources they index). Others may appear later. These paths are this repository's instantiation, not a universal assumption.*

## Verifiable Preconditions

Run these as explicit checks. Each **Passes** or **Fails**, and the results drive the output. Any Failed check is a Bootstrap Failed → Remediation. Do not repair a failing check during bootstrap.

- The Repository Version recorded in the Status Artifact equals the latest release identifier (for GHES, the latest Git tag).
- The required authority domains are discovered.
- The required artifacts exist within each domain.
- The required artifacts carry an accepted status where acceptance is required.
- Internal references resolve (ADR / MADR / specification / baseline cross-references).
- Authority precedence is established across the discovered domains.
- Working state is inspected read-only and reconciled against the Repository Continuity Artifact: current branch and HEAD, uncommitted changes, the stash list, unmerged local commits, and open pull requests are recorded; any divergence is surfaced, never silently acted on. Bootstrap inspects only — it does not switch branches, pop stashes, or merge.

## Continuity Artifact Handling

If the repository holds a **Repository Continuity Artifact** for the state being resumed, read it — it carries the uncommitted in-flight intent needed to resume a transient state. Keep it strictly **subordinate** to authoritative repository state: it may add resumption intent, never override committed state; on any conflict, the repository prevails and the discrepancy is surfaced (MADR-0001 D3). Do not require one for a clean, fully committed, stable state.

A **Conversation Continuity Artifact** is out of scope: never consume one, and never treat prior chat context as authoritative.

## Authority Precedence

Within the authority set, accepted decisions are authoritative and derived summaries are subordinate to them: a summary — such as the Status Artifact — never overrides an accepted decision, and the repository prevails over any continuity aid. Historical documents (discovery briefs, session summaries) explain how the architecture evolved but never override current authoritative artifacts. A repository may define its own detailed precedence, which bootstrap applies as discovered.

On conflict: identify it, cite the affected files and sections, apply precedence, and **surface the discrepancy** — never silently choose an interpretation, and never modify anything.

## Output — Session Context

Produce a Session Context result. Modify nothing.

### Outcome

One of: **Bootstrap Successful** (Context Established) or **Bootstrap Failed** (route to Remediation).

### Checks

- Passed checks.
- Failed checks — each with the artifact and the discrepancy. (Empty on success.)

### Current State

- Current project phase.
- The single authoritative current objective.
- Discovered authority domains.
- Repository Version and the latest release identifier.
- Latest architecture baseline and Architecture Version (when the architecture domain is present).
- Next milestone.

### Relevant Sources

The specific artifacts consulted.

### Notes

Only items that affect the current task.

## Constraints

Do not:

- modify, create, rename, move, commit, or delete repository content;
- repair inconsistencies — route them to Remediation;
- rely on prior chat context, or consume any Conversation Continuity Artifact, as authoritative;
- perform consolidation, phase-gate review, remediation, planning, or any other transition.

Bootstrap establishes context and the two-outcome readiness only.

## Success Criteria

- Authoritative domains are **discovered**, not assumed — including every accepted domain the repository exposes.
- Every precondition is an **explicit, verifiable check**.
- A failed check yields **Bootstrap Failed → Remediation**, never a partial context that proceeds to Working.
- A future contributor can tell, from the output alone, whether the session reached Context Established or Bootstrap Failed.
- No repository content is changed.
