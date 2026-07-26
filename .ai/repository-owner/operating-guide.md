# Repository Owner Operating Guide (authority)

**Type:** how the repository owner exercises repository authority. Pointer-first
by rule: gates are defined in the
[Skill Execution Map](../repository/methodology/skill-execution-map.md);
transition mechanics in the
[Methodology Operator Guide (transition router)](../repository/methodology/prompts/operator-guide.md);
skill governance in [`repo-owner-skills.md`](repo-owner-skills.md). This guide
never restates them — it states only what the owner does at each authority
point. The methodology's project-independent term "human architect" refers, in
this repository, to the repository owner.

## Governing invariants (from the Skill Execution Map)

1. Normal engineering execution proceeds from skill to skill; Repository Gates
   authorize progression but never become skills.
2. Repository authority changes occur only at Repository Gates. Skills prepare
   repository changes; the owner authorizes them.

## The owner at each Repository Gate

- **⟦G-Session⟧** — assign the session's role and entry bootstrap; on Bootstrap
  Failed, perform remediation and re-enter.
- **⟦G-Verdict⟧** — approve, condition, or reject an Architecture Grill
  verdict.
- **⟦G-Accept⟧** — review consolidated texts; authorize the acceptance branch
  and PR; merge; confirm STATUS reconciled atomically; complete closeout
  (tracked future-work issues).
- **⟦G-Merge⟧** — merge a ticket PR only after the verify chain (Standards +
  Spec + Conformance axes, then the independent Quality Gate) has passed.
- **⟦G-Refine⟧** — merge ratified refinements from halt-don't-decide
  excursions.
- **⟦G-Phase⟧** — execute phase gate, baseline publication, and release per the
  transition router's owner-executed steps (S5, S7, S8).

## Owner handoff review

At session end, verify the continuity rule: clean close only when the
repository is internally consistent, durable work committed, and
[`STATUS.md`](../repository/state/STATUS.md) accurate; otherwise require a
Repository Continuity Artifact
(`.ai/repository/state/repository-continuity.md`, transient)
and review it before the session ends. The collaboration avatar transfer
(manual, outside repository governance) is performed only after the
avatar generator's repository-transfer readiness gate passes.
