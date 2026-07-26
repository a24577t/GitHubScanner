# Migration FAQ — canonical questions and authoritative answers

One entry per original artifact, then cross-cutting questions. Answers are true
as of this migration and are never updated (immutability rule; see README.md).

## .ai/collaboration/load-order.md
- What happened: moved and renamed → `.ai/collaborator/bootstrap.md`.
- Why: it already was the collaborator's role bootstrap manifest by its own
  audience statement; the rename states the fact.
- Principle: one ownership question per artifact; audience-based namespaces.
- Omitted content: none.

## .ai/collaboration/instructor-architect-contract.md
- What happened: moved and renamed → `.ai/collaborator/contract.md`; H1
  retitled "Collaborator Contract".
- Why: instructor/architect/reviewer/quality-gate are responsibilities of one
  persistent collaborator role, not four roles (controlled vocabulary).
- Omitted content: none — all sections preserved.

## .ai/collaboration/avatar-bootstrap.md
- What happened: moved → `.ai/collaborator/avatar-bootstrap.md`, unchanged.
- Why: collaborator-role continuity artifact; content model untouched.

## .ai/collaboration/collaboration-avatar-generator.md
- What happened: moved and renamed → `.ai/collaborator/avatar-generator.md`.
- Why: namespace already says "collaborator"; the shorter name removes the
  redundant prefix. Content unchanged.

## .ai/collaboration/calaboration-human-notes.md
- What happened: deleted.
- Why: byte-empty file with a misspelled name and zero incoming references
  (grep-proven). Nothing replaced it; there was nothing to replace.
- Omitted content: none existed.

## .ai/architecture/STATUS.md
- What happened: moved → `.ai/repository/state/STATUS.md`.
- Why: the directory claimed "architecture" but held only current state;
  durable architecture lives under `docs/`. Principle: state is transient and
  answers "what is true today".

## .ai/methodology/** (whole unit)
- What happened: moved intact → `.ai/repository/methodology/**`.
- Why: participant-neutral repository knowledge under the repository owner
  namespace; the unit stays extractable (P6).

## .ai/prompts/methodology/*.md (seven live prompts)
- What happened: moved → `.ai/repository/methodology/prompts/`.
- Why: prompts are transition implementations of the methodology and travel
  with it. The continuity prompt's output was retargeted from the never-created
  `.ai/working/` to `.ai/repository/state/repository-continuity.md`.

## .ai/prompts/methodology/principles.md
- What happened: deleted (superseded early draft; zero incoming references).
- Replaced by: `.ai/repository/methodology/principles.md` (accepted P1–P7).
- Intentionally omitted content: its "Single Source of Truth" and "Single
  Responsibility" statements were not copied into the accepted principles.
  Their substance survives elsewhere with authority: CLAUDE.md's engineering
  rules (one responsibility per file; do not duplicate logic; update existing
  documentation instead of creating duplicates) and the methodology's own
  practice (P2 subsumes "repository as project memory"). Folding them into the
  accepted principles was declined to avoid editing an accepted artifact for
  content already enforced elsewhere.

## .ai/prompts/methodology/readme.md
- What happened: deleted (four-line stub; zero incoming references).
- Replaced by: the Methodology Operator Guide (transition router), which is
  the authoritative prompt index.

## docs/agents/repo-owner-skills.md
- What happened: relocated → `.ai/repository-owner/repo-owner-skills.md`.
- Why: `docs/agents/` holds configuration consumed by upstream skills at fixed
  paths; this document is owner governance. It was created by PR #24 and moved
  here unchanged apart from one link.

## Cross-cutting

- **Why does `.ai/repository/` exist?** The top level is organized by
  knowledge owner/audience: collaborator, repository owner, and the repository
  itself (participant-neutral). Methodology, state, and history are the
  repository's own knowledge.
- **Why did `.ai/prompts/` disappear?** Its only content was methodology
  prompts, which belong inside the extractable methodology unit.
- **Why is STATUS no longer under `architecture/`?** It never contained
  architecture; see the STATUS entry above.
- **Where are the repository-owner documents from?** `bootstrap.md` and
  `operating-guide.md` were created by this migration (pointer-first; the
  owner exercises authority under an operating guide, not a contract).
- **What replaced nothing / was newly created?** `.ai/README.md` (ownership
  map), the two repository-owner documents, this history package, and the
  automated exclusion test `tests/test_information_architecture.py`.
