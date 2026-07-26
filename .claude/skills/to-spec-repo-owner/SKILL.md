---
name: to-spec-repo-owner
description: Repository-owned specialization of /to-spec — consolidate grill-approved decisions into a review-ready specification under docs/specifications/. Runs only after the Architecture Grill verdict is owner-approved (G-Verdict); stops at G-Accept.
disable-model-invocation: true
---

# to-spec — repository-owner specialization

**Base skill:** the installed Matt Pocock [`to-spec`](../to-spec/SKILL.md). Use its
synthesis behavior — consolidate what has already been discussed and decided, with no
interview — wherever this file does not override it. Do not duplicate its text here;
do not modify it there.

> Repository-owner skills do not replace upstream skills. They specialize or constrain
> upstream behavior for repository execution. Upstream changes must be reviewed against
> the repository-owner specialization before being adopted.

> Skills prepare repository changes; repository authority changes only at Repository
> Gates. Execution of `to-spec-repo-owner` does not itself make the resulting artifacts
> authoritative.

`to-spec-repo-owner` is a repository-owned specialization of the upstream Matt Pocock
`to-spec` skill. The upstream skill remains unchanged. Future upstream updates must be
reviewed against this specialization before repository behavior is changed.

## Preconditions — verify each; on any failure STOP and report the missing prerequisite

1. The Architecture Grill for this work is complete.
2. The grill verdict has been approved by the repository owner (G-Verdict).
3. Architectural questions relevant to the specification are settled.
4. Available inputs: the approved grill record, the accepted ADRs (`docs/adr/`),
   repository conventions (`CLAUDE.md`, `docs/agents/`), and existing specification
   precedent (`docs/specifications/`).

Do not continue into specification production with any precondition unmet.

## Repository-owner overrides

- **Consolidation mode.** Consolidate settled decisions into a precise engineering
  specification. Do not reopen architectural decisions.
- **No redesign.** Do not redesign seams, modules, boundaries, contracts, identifiers,
  or layouts already settled by the Architecture Grill or accepted ADRs. The upstream
  seam-sketching step ("sketch the seams", "check with the user") does not run.
- **Format and location.** Follow this repository's specification precedent
  (`docs/specifications/`), not the upstream PRD template. Produce the specification
  file under `docs/specifications/`.
- **Exactness permitted.** Exact paths, module names, artifact names, identifiers,
  fixture names, and layouts are allowed when they are part of the approved contract.
  The upstream "no specific file paths" rule does not apply to approved contract
  content.
- **Authority by reference.** Reference governing ADRs; never restate architectural
  decisions as competing paraphrased authority. Coordinate any required ADR text
  through the repository's `domain-modeling` conventions.
- **No publication, no authorization.** Do not publish a tracker issue. Do not apply
  `ready-for-agent` or any other implementation authorization. Do not create
  implementation tickets. Do not invoke `to-tickets`. Do not begin implementation.

## Stop boundary

Stop after producing review-ready artifacts for **G-Accept** (owner review →
acceptance PR → owner merge). Until that gate authorizes them, the produced artifacts
are proposals, not repository truth.
