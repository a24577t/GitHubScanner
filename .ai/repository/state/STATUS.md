# Status Artifact

**Type:** derived summary. Subordinate to accepted decisions; never overrides them.

## Repository Version

v0.2.0

## Current Phase

Phase 1 — Observation. Vertical Slice 1 (Observation Collector) implemented, independently gated (PASS at `d5d4572`), and merged (PR #19, merge commit `193fad1`). Validation on merged main: 39/39 tests OK, Python 3.12.10, stdlib-only.

## Current Objective

Implement Vertical Slice 2 — Repository Configuration Collector — per the approved specification (tasks T1–T10, dependency order). T1 and T2 complete and merged (T1: PR #38, `50aa3e7`; T2: PR #40, `96c694a`); the next ticket, T3 (`transport.py` waits per ADR-0007), begins only with explicit repository-owner authorization. The GHAS governance rollout decision pack (wayfinder map, [issue #1](https://github.com/a24577t/GitHubScanner/issues/1)) remains the standing planning objective — discovery frontier tickets #2–#6 open.

## Completed Work Items

- **Vertical Slice 1 — Observation Collector** (PR #19, merged `193fad1`): `collect`/`derive` CLI per the approved specification; evidence: red-first TDD record, two independent quality-gate rounds (FAIL → corrections QG-01..06 → PASS), /code-review Standards PASS + Spec PASS, token-secrecy and offline byte-identity proven in-suite.
- **Validation Environment** (PR #21, merged `bdb752d`, independent Quality Gate PASS at `7ea9944`): `GHScannerLab` organization with three Slice-1 fixtures; first live github.com validation run `20260725T184527Z` committed under `docs/validation/runs/`; environment documented in `docs/validation/validation-environment.md` (honest scope: Free-plan github.com API surface only). Slice 2's real-environment-validation precondition is now satisfied.
- **Methodology ratification and collaboration refresh** (2026-07-26): methodology audit against the Matt Pocock skill set; Skill Execution Map adopted as the operational execution model with its two governing invariants (`.ai/methodology/skill-execution-map.md`); repo-owner specialization skill pattern established (`docs/agents/repo-owner-skills.md`; first instance `to-spec-repo-owner`, PR #23 merged `f0ad563`); collaboration contract, load order, and Collaboration Avatar updated (PR #24, merged `e943ed1`). Slice 2 Architecture Grill completed 2026-07-26 with verdict PASS WITH CONDITIONS, owner-approved.
- **Slice 2 architecture accepted** (⟦G-Accept⟧, PR #25 merged `b346159`): ADRs 0004–0007 accepted; Vertical Slice 2 specification and normative validation matrix approved (architecture grill, 2026-07-26; consolidation by `to-spec-repo-owner`); acceptance closeout created future-work issues #26–#28 (Observation Target Model; `security_and_analysis` projection; per-ruleset detail).
- **`.ai` information-architecture migration** (PR #29, merged `872544e`; approved design 2026-07-26): audience/ownership namespaces `collaborator/`, `repository-owner/`, `repository/{methodology, state, history}`; history package `ia-redesign-2026-07` with exact legacy snapshot — **immutable as of the merge**, per its recorded boundary (the merge SHA is deliberately not embedded in the package; its README documents the self-reference convention); two dead files and one superseded draft removed (evidence in the package); all references updated atomically; post-merge validation 42/42 tests OK.
- **Methodology Release v0.2.0 closeout** (PRs #31, #32, #33, #35): MADR-0003 accepted; transfer architecture accepted — Observer and Review Evidence Package (REP) recorded as Architecture Accepted / Implementation Deferred under [issue #34](https://github.com/a24577t/GitHubScanner/issues/34); Decision-Gated Implementation Lifecycle ratified; Observer added to the controlled vocabulary; Collaboration Avatar regenerated through the readiness gate; GHAS SKU research evidence preserved under `docs/research/`.

- **Slice 2 T1 — descriptor table + `default-branch-protection` projection** (PR #38, merged `50aa3e7`; Quality Gate PASS, owner-recorded 2026-07-26; merge approved without code changes): `resources.py` declarative descriptor table with import-time integrity validation and pure projection interpreter, per the approved specification's module table; evidence: red-first TDD record (four cycles, preserved in the ticket commit message), 21 new behavioral tests at the ratified seams, validation on merged main 63/63 tests OK (zero regressions), diff scoped to the task (two new files, both ≤300 lines).

- **Slice 2 T2 — classification extracted into `taxonomy.py`** (PR #40, merged `96c694a`; Quality Gate PASS, owner-recorded 2026-07-26; merge approved without code changes): descriptor-anchored absence matching and the closed deterministic-reason set now owned by the pure `taxonomy.py`; `derive.py` retains evidence loading and invocation only; evidence: red-first TDD record (four cycles, in the ticket commit message), matrix rows V13–V20 covered at the classify seam, S10 three-axis review (Standards: two judgement calls dispositioned to T6; Spec: complete; Conformance: clean), validation on merged main 78/78 tests OK (zero regressions; the 42 Slice-1 CLI tests pass unchanged).

## Architecture

- **Architecture Baseline:** none published (Pre-Baseline; Slice 1 is implementation of accepted ADRs, not a baseline).
- **Architecture Version:** none.
- **Domain Model / CONTEXT.md:** not yet created (created lazily by `/domain-modeling`).
- **ADRs:** 0001–0007 accepted (`docs/adr/`): three evidence layers + derivability; seven-state taxonomy + affirmative absence; explicit environment targeting; repository resource observation model; canonical target discovery + evidence addressing; taxonomy evidence rules; bounded execution waits.

## Authority Domains

- **Collaborator** — `.ai/collaborator/` (bootstrap, contract, avatar, avatar generator).
- **Repository owner** — `.ai/repository-owner/` (bootstrap, operating guide, repo-owner skill governance).
- **Repository methodology** — `.ai/repository/methodology/` (principles, lifecycle model, glossary, MADRs, Skill Execution Map, transition prompts — skills execute, Repository Gates authorize).
- **Repository state** — `.ai/repository/state/` (this Status Artifact; Repository Continuity Artifact when emitted).
- **Repository history** — `.ai/repository/history/` (immutable evolution evidence; never loaded at bootstrap, never authority).
- **Agent configuration** — `CLAUDE.md`, `docs/agents/` (issue tracker, triage labels, domain-doc rules).

## Next Milestone

Roadmap, in accepted order:

1. Vertical Slice 2 implementation (T1–T10 per the approved specification); T1 begins only with explicit repository-owner authorization.
2. The binding post-slice architecture gate: Architecture Consolidation → `/domain-modeling` and `CONTEXT.md` creation → only then Slice 3 activity.
3. Observer and Review Evidence Package (REP) implementation under [issue #34](https://github.com/a24577t/GitHubScanner/issues/34) — only when its recorded trigger and explicit repository-owner authorization are satisfied; Architecture Accepted / Implementation Deferred until then.
4. Wayfinder discovery tickets (platform, licensing, native controls, CI/runners, estate shape) may proceed in parallel where already authorized by repository artifacts.
