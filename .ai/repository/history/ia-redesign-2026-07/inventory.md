# Pre-migration inventory and classification

The complete `.ai` inventory (plus directly related artifacts) as reviewed at
`b346159`, classified by the four-question ownership test then in force
(collaborator / repository owner / repository methodology / repository state;
the history question was added by the approved revision that created this
package). Authority: A accepted/authoritative, D evolvable design, S
subordinate/derived, X defunct.

| Artifact | Purpose | Audience | Auth | Ownership question | Disposition |
|---|---|---|---|---|---|
| `.ai/architecture/STATUS.md` | Status Artifact (program counter) | All | S | State | move |
| `.ai/collaboration/load-order.md` | Collaborator startup manifest | Collaborator | A | Collaborator | move+rename |
| `.ai/collaboration/instructor-architect-contract.md` | Collaborator role contract | Collaborator | A | Collaborator | move+rename |
| `.ai/collaboration/avatar-bootstrap.md` | Transferable collaboration knowledge | Incoming collaborator | S | Collaborator | move |
| `.ai/collaboration/collaboration-avatar-generator.md` | Avatar generation + readiness gate | Outgoing collaborator | D | Collaborator | move+rename |
| `.ai/collaboration/calaboration-human-notes.md` | Empty; misspelled | — | X | — | delete |
| `.ai/methodology/README.md` | Methodology unit charter | All | A | Methodology | move with unit |
| `.ai/methodology/adr/0001,0002` | Methodology axioms (MADRs) | All | A | Methodology | move with unit |
| `.ai/methodology/principles.md` | P1–P7 | All | A | Methodology | move with unit |
| `.ai/methodology/glossary.md` | Vocabulary | All | A | Methodology | move with unit |
| `.ai/methodology/lifecycle-model.md` | State model | All | A/D | Methodology | move with unit |
| `.ai/methodology/decision-gated-implementation-lifecycle.md` | Decision→code crossing (status: proposed) | All | D | Methodology | move with unit |
| `.ai/methodology/skill-execution-map.md` | Operational execution model | All | A | Methodology | move with unit |
| `.ai/methodology/validation/**` | Methodology-validation charter | All | D/E | Methodology | move with unit |
| `.ai/prompts/methodology/*.md` (7 live prompts) | Transition implementations | Mixed executors | D | Methodology | move into unit `prompts/` |
| `.ai/prompts/methodology/principles.md` | Superseded 3-principle draft | — | X | Methodology | delete (see questions.md) |
| `.ai/prompts/methodology/readme.md` | Superseded stub | — | X | — | delete |
| `docs/agents/repo-owner-skills.md` | `*-repo-owner` governance | Owner | A | Repository owner | relocate |
| Unmoved, reviewed: `CLAUDE.md`, `docs/agents/{issue-tracker,triage-labels,domain}.md`, `docs/adr/`, `docs/specifications/`, `docs/validation/`, `.claude/skills/**`, `CONTEXT.md` (future, root) | Established authoritative locations | — | — | — | retain in place |

Reference evidence: incoming/outgoing references were established by repository
grep before disposition; both deleted files and the superseded draft had zero
incoming references. The full reference graph as executed is in
`reference-updates.md`.
