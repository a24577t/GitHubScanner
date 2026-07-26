# Repository-owner specialization skills

Repository-owner skills adapt upstream Matt Pocock skills to this repository's
authority model without touching them.

> Repository-owner skills do not replace upstream skills. They specialize or
> constrain upstream behavior for repository execution. Upstream changes must be
> reviewed against the repository-owner specialization before being adopted.

## Rules

- **Upstream skills remain unchanged.** Never edit, relocate, or rename a skill
  under `.claude/skills/` that was installed from the upstream set. Updates or
  reinstalls of the upstream set must not be able to overwrite repository-owned
  behavior.
- **Delta only.** A repository-owner skill references its base skill and
  contains only repository-owner preconditions, constraints, overrides, outputs,
  and stop boundaries. It never copies the upstream text.
- **Naming and location.** `<upstream-name>-repo-owner`, at
  `.claude/skills/<upstream-name>-repo-owner/SKILL.md`.
- **Upstream update review.** When an upstream skill changes, review the diff
  against every specialization that wraps it before adopting the update; adopt,
  adjust the specialization, or reject — as an owner-reviewed change.
- **Gate discipline.** Every repository-owner skill states where it stops.
  Skills prepare repository changes; repository authority changes only at
  Repository Gates (see the
  [Skill Execution Map](../../.ai/methodology/skill-execution-map.md)).

## Current specializations

| Skill | Base | Position | Stops at |
|---|---|---|---|
| [`to-spec-repo-owner`](../../.claude/skills/to-spec-repo-owner/SKILL.md) | `to-spec` | S5 (consolidation after an owner-approved Architecture Grill verdict) | ⟦G-Accept⟧ |
