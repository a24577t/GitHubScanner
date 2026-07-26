# Decisions governing this migration

## Approvals

- Two independent architectural reviews of the proposed IA (inventory-driven;
  candidate structures challenged, not adopted by default), followed by a final
  validation returning **APPROVE WITH MINOR REVISIONS** (2026-07-26).
- Repository-owner approval of the revised architecture including
  `repository/history/`, subject to five corrections (below), 2026-07-26.
- Sequencing executed as approved: PR #24 (methodology/collaboration refresh,
  separate logical change, merged `e943ed1`) → Slice 2 ⟦G-Accept⟧ (PR #25,
  merged `b346159`; closeout issues #26–#28) → this atomic migration PR.

## Structural decisions

- Top level organized by audience/ownership: `collaborator/`,
  `repository-owner/`, `repository/` — five ownership questions, three owners.
- `repository/` name retained over `shared/`, `common/`, `project/`,
  `process/`: the controlled vocabulary establishes the repository itself as
  the participant-neutral knowledge owner.
- No `implementor/` namespace: the implementation participant has no
  role-specific durable artifacts; the distinction is vocabulary
  ("implementation participant" as qualified use of *participant*), not
  directories.
- `prompts/` folded into `repository/methodology/prompts/`: prompts are
  transition implementations and travel with the extractable methodology unit
  (P6).
- Repository owner gets an **Operating Guide, not a contract**: the owner
  exercises authority; a contract binds the collaborator to the owner.
- `CONTEXT.md` stays at the repository root: durable domain glossary in its
  established location, not repository state.
- Instructor / architect / reviewer / quality gate ruled **responsibilities of
  the collaborator**, not roles; controlled vocabulary: collaborator,
  repository owner, repository, participant.

## Owner corrections incorporated (2026-07-26)

1. **Immutability boundary:** provisional while the migration PR is open;
   immutable at merge; later corrections append new related records.
2. **Exact snapshot provenance:** pre-migration SHA, branch, PR, merge-commit
   convention, and the post-PR-#24 statement recorded in the package README.
3. **Mechanical exclusion of historical instructions:** documented in
   `.ai/README.md` and the package README; automated verification added at the
   repository's existing validation seam
   (`tests/test_information_architecture.py`).
4. **Atomic migration scope:** hygiene deletions folded into this PR so the
   package records the complete executed redesign.
5. **Future history-package threshold:** create a package when a change
   introduces or retires a namespace, moves or renames multiple operational or
   authoritative artifacts, changes knowledge ownership, replaces a
   bootstrap/lifecycle/execution model, or consolidates artifacts such that
   lineage would otherwise be difficult to answer. Routine edits and isolated
   file changes rely on Git history.

## Retained prior minor revisions

`.ai/README.md` ownership map with change-authority statement; namespace names
describe audience/subject, not edit rights; all `.ai` changes via
owner-authorized merge; pointer-first repository-owner documents;
methodology→participant references limited to bounded routing pointers; guide
titles disambiguated ("Methodology Operator Guide (transition router)" vs
"Repository Owner Operating Guide (authority)"); history is evidence, never
authority; durable architecture outside repository state.

## Open items deliberately not decided by this migration

- DGIL ratification (status remains `proposed`).
- Disposition of the `research/ghas-sku-pricing` branch.
- Location of future Architecture Baseline artifacts (legacy prompt text
  referenced prospective `.ai/architecture/` files that were never created;
  STATUS references were updated, the prospective baseline paths await a
  decision before the first baseline publication).
- Collaboration Avatar regeneration (next transfer point, via the readiness
  gate).
