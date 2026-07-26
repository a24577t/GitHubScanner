# .ai — knowledge ownership map

Namespaces describe **audience and subject, not edit rights**: every `.ai`
change lands only through a repository-owner-authorized merge (Repository
Gates). Each namespace answers exactly one ownership question:

- [`collaborator/`](collaborator/) — *How should the collaborator perform its
  role?* Bootstrap, contract, avatar, avatar generator.
- [`repository-owner/`](repository-owner/) — *How does the repository owner
  exercise repository authority?* Bootstrap, operating guide, repo-owner skill
  governance.
- [`repository/methodology/`](repository/methodology/) — *How does this
  repository work, regardless of participant?* Principles, lifecycle, Skill
  Execution Map, transition prompts.
- [`repository/state/`](repository/state/) — *What is true about the repository
  today?* The Status Artifact and any Repository Continuity Artifact.
- [`repository/history/`](repository/history/) — *How did the repository
  evolve, and why?* Immutable evidence packages. Never current methodology,
  never loaded by any bootstrap, never edited after its migration PR merges;
  later corrections are appended as new, explicitly related records.

**Reference directionality.** Participant namespaces may depend on
`repository/`. `repository/` may reference participant namespaces only as
routing pointers, never as content dependencies. Any current document may link
*into* `history/` informationally, but no current document may depend on a
history package — and nothing inside a `history/**/legacy/` snapshot is ever a
link target, an instruction source, or an executable prompt. Repository-wide
searches and reviews must treat matches under `history/` as non-current
evidence.

Durable architecture (ADRs, specifications, validation evidence) lives under
`docs/`; the domain glossary `CONTEXT.md` lives at the repository root.
