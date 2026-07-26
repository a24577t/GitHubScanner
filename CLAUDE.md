# GitHubScanner

New project — scope and domain model not yet defined.

## Git workflow

`main` is protected — never commit to, push to, or locally merge into `main`. Every change goes on a feature branch and lands in `main` only through a pull request.

# Engineering Rules

## Authority
- Repository artifacts are authoritative.
- Conversation is not repository truth.
- Do not guess. STOP when required information is missing and cannot be determined from the repository.

## Architecture
- Architecture before implementation.
- Implement only approved scope.
- Follow existing repository patterns.
- Do not change architecture, methodology, governance, or conventions without approval.

## Structure
- One responsibility per file.
- Files MUST remain ≤300 physical lines (see File-size rule below).
- Default: split at a natural responsibility boundary before exceeding.
- Exceeding 300 lines requires the File-size rule's exception process: STOP, argue the case in full, and wait for the human decision.
- Do not perform unrelated refactoring.
- Choose the simplest correct solution.
- Avoid speculative abstraction.

## Configuration
- Environment-specific values belong in `.env`.
- Domain constants belong in code.
- Never hardcode secrets.
- Missing required configuration is an error — no hidden defaults.

## Validation
- Frontend validates UX.
- Backend validates authority.
- Validate every external boundary with schemas.
- Run all required validation before completion.
- Never bypass failing validation.

## Errors
- Never hide errors.
- Fail loudly and explicitly.

## Frontend
- Avoid `useEffect()` unless required.
- Prefer props and derived state.
- UI must respond immediately — never block on network; show optimistic or pending state.

## Backend
- Prefer functions over classes.
- Routes, workers, and CLI are orchestration only.
- Keep orchestration layers thin.
- Business logic belongs in services/interfaces.
- Libraries are pure and side-effect free.
- Repositories perform database I/O only.
- Keep query shaping in SQL.
- Use schema-shaped inputs and outputs.
- Alembic revision IDs ≤32 characters.

## Data
- Set operations belong in SQL.
- Do not recreate SQL with Python loops.
- Business rules belong on the backend.
- Presentation belongs on the frontend.

## Compatibility
- Do not preserve backward compatibility unless requested.

## Code Quality
- Do not duplicate logic.
- Remove dead code.
- Comment why, never what.

## Dependencies
- Do not introduce new dependencies without justification.

## Documentation
- Do not create documentation unless requested.
- Update existing documentation instead of creating duplicates.

## Decision Gates
STOP and wait for approval when changing:
- Architecture
- Public interfaces
- Repository conventions
- File size exception (>300 physical lines)
- Methodology or governance

## Completion
Do not claim completion until:
- Required validation passes.
- Approved scope is complete.
- No known rule violations remain.

## File-size rule

Source files MUST NOT exceed 300 physical lines.

When planned work would cause a file to exceed 300 lines:

1. Refactor the file at a natural responsibility boundary before continuing.
2. Do not ask for approval merely because the threshold was reached.
3. Do not continue beyond 300 lines by default.

Exception process:

Only stop and request human review when there is a specific, defensible reason
that splitting the file would reduce correctness, cohesion, readability, or
maintainability.

The review request MUST include:

- current line count;
- estimated final line count;
- why the new behavior belongs in the existing file;
- the most reasonable split alternative;
- why that split would be materially worse;
- the conceptual structure of both approaches;
- a recommendation.

Do not implement beyond 300 lines until explicit approval is received.

The human review decides one of three outcomes:

1. **Approval with limits** — the exception is granted under stated constraints
   (e.g. a new ceiling, a scope boundary, or a follow-up refactor commitment);
   those constraints become binding.
2. **Outright approval** — the exception is granted as argued.
3. **Split** — the exception is denied; refactor at the recommended (or a
   directed) boundary before continuing.

Proceed only per the decision received.

Convenience, speed, avoiding a refactor, or keeping related code nearby are not
sufficient reasons for an exception.

## Agent skills

### Issue tracker

Issues are tracked as GitHub Issues on `a24577t/GitHubScanner`, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary — the five canonical roles used verbatim (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — one `CONTEXT.md` and `docs/adr/` at the repo root, created lazily by `/domain-modeling`. See `docs/agents/domain.md`.

### Repo-owner skills

Repository-owned `*-repo-owner` skills wrap upstream Matt Pocock skills with repository-specific deltas; upstream skills are never modified. See `.ai/repository-owner/repo-owner-skills.md`.

## Methodology

The project follows the methodology in `.ai/repository/methodology/` (project-independent lifecycle model, principles, and glossary). Engineering work executes per the Skill Execution Map (`.ai/repository/methodology/skill-execution-map.md`): skills execute, Repository Gates authorize. Session startup routing: `.ai/repository/methodology/prompts/operator-guide.md` → `.ai/repository/methodology/prompts/session-bootstrap.md`. Role entry: collaborator sessions start at `.ai/collaborator/bootstrap.md`; repository-owner sessions at `.ai/repository-owner/bootstrap.md`. The `.ai` ownership map: `.ai/README.md`.
