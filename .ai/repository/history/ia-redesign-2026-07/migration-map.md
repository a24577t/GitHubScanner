# Executed migration map

Pre-migration paths as of `b346159`; all moves via `git mv` in the migration PR.

| Old path | New path | Kind |
|---|---|---|
| `.ai/architecture/STATUS.md` | `.ai/repository/state/STATUS.md` | move |
| `.ai/collaboration/load-order.md` | `.ai/collaborator/bootstrap.md` | move+rename |
| `.ai/collaboration/instructor-architect-contract.md` | `.ai/collaborator/contract.md` | move+rename |
| `.ai/collaboration/avatar-bootstrap.md` | `.ai/collaborator/avatar-bootstrap.md` | move |
| `.ai/collaboration/collaboration-avatar-generator.md` | `.ai/collaborator/avatar-generator.md` | move+rename |
| `.ai/collaboration/calaboration-human-notes.md` | — | **deleted** (empty file, misspelled name, zero incoming references — grep-proven) |
| `.ai/methodology/**` (unit: README, principles, glossary, lifecycle-model, DGIL, skill-execution-map, adr/, validation/) | `.ai/repository/methodology/**` | move (unit intact) |
| `.ai/prompts/methodology/session-bootstrap.md` | `.ai/repository/methodology/prompts/session-bootstrap.md` | move |
| `.ai/prompts/methodology/operator-guide.md` | `.ai/repository/methodology/prompts/operator-guide.md` | move (+ title: "(transition router)") |
| `.ai/prompts/methodology/review-discipline.md` | `.ai/repository/methodology/prompts/review-discipline.md` | move |
| `.ai/prompts/methodology/phase-gate-review.md` | `.ai/repository/methodology/prompts/phase-gate-review.md` | move |
| `.ai/prompts/methodology/architecture-consolidation.md` | `.ai/repository/methodology/prompts/architecture-consolidation.md` | move |
| `.ai/prompts/methodology/publish-architecture-baseline.md` | `.ai/repository/methodology/prompts/publish-architecture-baseline.md` | move |
| `.ai/prompts/methodology/project-release.md` | `.ai/repository/methodology/prompts/project-release.md` | move |
| `.ai/prompts/methodology/create-repository-continuity.md` | `.ai/repository/methodology/prompts/create-repository-continuity.md` | move (+ output retargeted to `.ai/repository/state/repository-continuity.md`) |
| `.ai/prompts/methodology/principles.md` | — | **deleted** (superseded early draft; zero incoming references — see `questions.md` for intentionally omitted content) |
| `.ai/prompts/methodology/readme.md` | — | **deleted** (4-line stub superseded by the operator guide; zero incoming references) |
| `docs/agents/repo-owner-skills.md` | `.ai/repository-owner/repo-owner-skills.md` | relocate (owner governance, not skill-consumed config) |
| *(planned, never created)* `.ai/working/repository-continuity.md` | `.ai/repository/state/repository-continuity.md` | retarget in prompt, map, and operating guide |
| — | `.ai/README.md` | new (ownership map, directionality rules) |
| — | `.ai/repository-owner/bootstrap.md` | new (pointer-first owner manifest) |
| — | `.ai/repository-owner/operating-guide.md` | new (pointer-first authority guide) |
| — | `.ai/repository/history/ia-redesign-2026-07/**` | new (this package) |
| — | `tests/test_information_architecture.py` | new (automated exclusion verification) |
