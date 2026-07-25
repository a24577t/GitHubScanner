# Execution-agnostic collector with three evidence layers

**Status:** accepted

The GitHub environment collector is a deterministic, non-interactive CLI whose contract is independent of any hosting model (Actions, schedulers, containers are future thin wrappers). It writes an operator-directed output directory containing three layers with explicit authority: **raw evidence** (append-only verbatim API responses with request envelopes — authoritative), **observed state** (a regenerable, latest-only normalized mirror), and **collection reports** (append-only operational history). The architectural invariant is the **derivability rule**: every element of observed state must be reproducible byte-identically from raw evidence alone, offline. If regeneration differs, either normalization logic changed or raw evidence is incomplete — there is no third possibility.

## Consequences

- Determinism is required of *derivation*, not collection; the environment may change between runs.
- Git operations, evidence ownership, and retention are operational concerns outside the collector's contract.
- Alternatives rejected: a GitHub Actions-native collector (assumes Actions availability in unknown environments) and a service/product (Phase 1 is observation only, and the project must not become a custom governance product).
