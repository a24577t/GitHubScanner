# Executed reference updates

Every cross-reference changed by the migration, by file (at its new path).

- **`CLAUDE.md`** — methodology unit path; Skill Execution Map path; session
  startup routing (operator-guide, session-bootstrap under
  `repository/methodology/prompts/`); role-entry lines (collaborator and
  repository-owner bootstraps); repo-owner-skills pointer; `.ai/README.md`
  ownership-map pointer.
- **`.ai/collaborator/bootstrap.md`** — contract links (×4,
  `instructor-architect-contract.md` → `contract.md`); all
  `../prompts/methodology/` links → `../repository/methodology/prompts/`
  (operator-guide, session-bootstrap, review-discipline, phase-gate-review,
  create-repository-continuity); avatar generator links
  (`collaboration-avatar-generator.md` → `avatar-generator.md`); Skill
  Execution Map and DGIL links → `../repository/methodology/`; methodology
  unit link; H1 retitle ("Collaborator Bootstrap — Load Order"); checklist
  self-reference (`load-order.md` → `bootstrap.md`).
- **`.ai/collaborator/contract.md`** — `bootstrap.md` links (ex `load-order.md`);
  review-discipline path; Skill Execution Map path; repo-owner-skills path;
  H1 retitle ("Collaborator Contract", four responsibilities named beneath).
- **`.ai/repository/methodology/prompts/operator-guide.md`** — lifecycle and
  principles links (`../../methodology/` → `../`); avatar-generator links
  (`../../collaboration/…` → `../../../collaborator/avatar-generator.md`);
  continuity output path; title suffix "(transition router)".
- **`.ai/repository/methodology/prompts/session-bootstrap.md`** — GHES example
  authority-domain paths updated to the new instantiation, including the
  history-domain exclusion statement.
- **`.ai/repository/methodology/prompts/create-repository-continuity.md`** —
  output path `.ai/working/…` → `.ai/repository/state/repository-continuity.md`.
- **`.ai/repository/methodology/prompts/{phase-gate-review, publish-architecture-baseline, project-release}.md`**
  — Status Artifact path `.ai/architecture/STATUS.md` →
  `.ai/repository/state/STATUS.md` (prospective baseline-artifact paths left
  untouched pending the open baseline-location decision; see `decisions.md`).
- **`.ai/repository/methodology/skill-execution-map.md`** — repo-owner-skills
  links (×2) → `../../repository-owner/repo-owner-skills.md`; continuity path.
- **`.ai/repository/methodology/glossary.md`** — Status Artifact example path.
- **`.ai/repository/methodology/validation/README.md`** — self-descriptive
  unit paths; MADR register path.
- **`.ai/repository-owner/repo-owner-skills.md`** — Skill Execution Map link →
  `../repository/methodology/skill-execution-map.md` (skill links unchanged:
  same depth to repo root).
- **`.ai/repository/state/STATUS.md`** — Authority Domains rewritten to the
  five new domains (history marked evidence, not loaded); IA-migration
  completed-work item added. Historical completed-work entries retain the
  paths that were true when written.
- **Unchanged by design** — `.ai/collaborator/avatar-bootstrap.md` (repository
  references are deliberately generic) and `.ai/collaborator/avatar-generator.md`
  (same-directory references only); methodology unit internal links
  (same-directory, unit moved intact); `docs/` artifacts (no `.ai` references).
