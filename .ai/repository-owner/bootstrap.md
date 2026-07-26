# Repository Owner — Bootstrap

**Type:** load-order manifest for the repository owner. Pointer-first: this
file loads knowledge; it never restates it.

1. **This manifest** — the repository-owner entry point.
2. **Authority and operations** — [`operating-guide.md`](operating-guide.md):
   Repository Gates, acceptance and merge procedure, owner handoff review.
3. **Skill governance** — [`repo-owner-skills.md`](repo-owner-skills.md):
   `*-repo-owner` specialization rules and upstream-update review.
4. **Shared startup** — the methodology's
   [operator guide](../repository/methodology/prompts/operator-guide.md) → S1 →
   [session bootstrap](../repository/methodology/prompts/session-bootstrap.md)
   (read-only verification), then current state:
   [`STATUS.md`](../repository/state/STATUS.md).
5. **Resuming in-flight work** — a Repository Continuity Artifact
   (`.ai/repository/state/repository-continuity.md`, transient — present only
   when a session ended mid-transition) is read by session bootstrap as
   subordinate context.

`repository/history/` is never loaded at bootstrap — it is evolution evidence,
not current knowledge (see [.ai/README.md](../README.md)).
