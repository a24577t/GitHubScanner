---
status: accepted
---

# Skill Execution Map

**Type:** operational execution model. The [Decision-Gated Implementation
Lifecycle](decision-gated-implementation-lifecycle.md) and the
[Lifecycle Model](lifecycle-model.md) explain **why** this flow exists; this map
defines **what to execute next**. Where they appear to disagree, the lifecycle
documents prevail and this map is corrected.

> **Governing invariants.**
>
> 1. Normal engineering execution always proceeds from one skill to the next.
>    Repository Gates authorize progression between skills but never replace,
>    duplicate, or become engineering skills themselves.
> 2. Repository authority changes occur only at Repository Gates. Skills prepare
>    repository changes; Repository Gates authorize them.

Skill Steps (S1–S11) are executable engineering work — installed Matt Pocock
skills or repository-owned specializations of them (see
[repo-owner-skills.md](../../repository-owner/repo-owner-skills.md)).
Repository Gates ⟦G-…⟧ are unnumbered authorization points; each names its
successor skill. Determinism is per step: a skill appearing at two steps has one
normal successor at each, and the step is always known from the completion
condition just met.

## Session frame

- **⟦G-Session⟧** — every session enters through session bootstrap (read-only,
  two outcomes). *Context Established* → the Skill Step named by the Status
  Artifact's objective; *Failed* → human remediation → re-enter.
- **Session end** — clean close (continuity rule holds), or `/handoff`: plain
  mode for private context; continuity mode prepares
  `.ai/repository/state/repository-continuity.md` for owner review when ending
  mid-transition (including between a grill freeze and ratification).

## Main path

| Step | Invoke | Specialization | Complete when | Normal next | Conditional — gate |
|---|---|---|---|---|---|
| S1 | `wayfinder` (chart) | Architecture-bearing efforts exit via S4 | Map + tickets created | S2 | — |
| S2 | `grilling`/`research`/`prototype` per ticket (`domain-modeling` inline) | Research branches disposed on ticket close | Ticket resolved, closed, indexed | S2 (next ticket) | Frontier empty → S3 |
| S3 | `wayfinder` (close map) | — | Way clear | S4 | No architecture in effort → S5 |
| S4 | `grilling` as **Architecture Grill** | Frozen proposal; fixed invariants out of scope; per-question classifications; verdict | Verdict delivered | ⟦G-Verdict⟧ | — |
| — | **⟦G-Verdict⟧** owner approves the verdict | | Approved | S5 | FAIL / withheld → S2 |
| S5 | `to-spec-repo-owner` + `domain-modeling` (ADR texts) | Consolidation mode; house format; no publication or authorization | Review-ready texts presented | ⟦G-Accept⟧ | — |
| — | **⟦G-Accept⟧** owner review → acceptance PR → owner merge; STATUS reconciled in the PR | | Merged; STATUS accurate | S6 | Decision gap → S4 |
| S6 | `to-tickets` | Consumes the approved spec's breakdown 1:1; labels only per owner authorization | Tickets published with edges | S7 (first frontier ticket, fresh context) | — |
| S7 | `implement` (one ticket) | Feature branch only; drives S8–S11; never self-merges | Verify chain complete | S8 | — |
| S8 | `codebase-design` | *Validate* mode when the spec pre-settled structure | Seams confirmed | S9 | Unratified seam → HALT → E1 |
| S9 | `tdd` | Red-first record kept; ratified seams only | Suite green | S10 | Unratified question → HALT → E1 |
| S10 | `code-review` (Standards + Spec + **Conformance axis**) | Third axis: conformance to ADRs/spec | Three axes clean | S11 | Findings → S9; crossing → HALT → E1 |
| S11 | `code-review` as **Quality Gate** | Independent reviewer, review-discipline, verdict | Verdict recorded | ⟦G-Merge⟧ | fail → S9; pass-with-conditions: conditions travel forward |
| — | **⟦G-Merge⟧** owner merges the ticket PR | | On `main` | S7 (next ticket) | Milestone-Complete → ⟦G-Phase⟧ |
| — | **⟦G-Phase⟧** phase gate → baseline → release; STATUS reconciled | | Gate PASS; tag/release/STATUS agree | S1 or S2 per new objective | Gate FAIL → S7 |

## Excursion E1 — halt-don't-decide (Refinement)

HALT (from S8/S9/S10) → `grilling` (the one surfaced question) +
`domain-modeling` → `to-spec-repo-owner`/`domain-modeling` (ratify the
refinement, append-only) → ⟦G-Refine⟧ owner PR merges; architecture version
advances → resume the interrupted step, re-running S10.

## On-ramps

| Situation | Invoke | Complete when | Normal next | Conditional |
|---|---|---|---|---|
| External issue/PR | `triage` | One category + one state role | S7 (`ready-for-agent`) | Needs shaping → S2; `wontfix` → done |
| Something broken | `diagnosing-bugs` | Tight red loop established | S9 (regression-test fix) | No seam → `improve-codebase-architecture` |
| Spare capacity | `improve-codebase-architecture` | Candidate chosen | S2 (candidate enters as new effort) | — |

Out-of-lifecycle utilities (`teach`, `writing-great-skills`, `setup-pre-commit`,
`resolving-merge-conflicts`, …) hold no position; they return to the
interrupted skill.

## Dependency diagram

```
⟦G-Session⟧ → wayfinder → (grilling/research/prototype per ticket)
  → grilling [Architecture Grill] → ⟦G-Verdict⟧
  → to-spec-repo-owner + domain-modeling → ⟦G-Accept⟧
  → to-tickets → implement → codebase-design → tdd
  → code-review [3 axes] → code-review [Quality Gate] → ⟦G-Merge⟧
  → next ticket … → (Milestone-Complete) → ⟦G-Phase⟧ → next effort
halts: S8/S9/S10 → grilling → ratify → ⟦G-Refine⟧ → resume
on-ramps: triage → implement · diagnosing-bugs → tdd
          improve-codebase-architecture → grilling
```

## Relationship note

`to-spec-repo-owner` is a repository-owned specialization of the upstream Matt
Pocock `to-spec` skill. The upstream skill remains unchanged. Future upstream
updates must be reviewed against this specialization before repository behavior
is changed. The same rule governs every `*-repo-owner` skill
([repo-owner-skills.md](../../repository-owner/repo-owner-skills.md)).
