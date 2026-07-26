# Architecture Discovery Consolidation Prompt

We have completed an architecture discovery cycle using `grill-with-docs`.

Do **not** ask another architecture question yet.

Your objective is to consolidate the current architecture before continuing discovery.

## Responsibilities

Perform the following tasks in order.

### 1. Architecture Consistency Review

Review every architecture artifact.

Identify:

* contradictions
* duplicated concepts
* inconsistent terminology
* overlapping ADRs
* obsolete statements
* hidden assumptions
* undefined relationships
* architectural drift introduced during discovery

Do not silently modify architectural decisions.

Instead:

* explain the inconsistency
* recommend a resolution
* identify which ADR(s) are impacted

---

### 2. ADR Review

Review every Candidate ADR.

For each ADR:

* summarize its purpose
* identify dependencies on other ADRs
* identify any contradictions
* identify any superseded statements
* verify terminology matches the glossary

Do **not** change ADR status.

All ADRs remain:

**Status: Proposed**

---

### 3. Domain Model

Update the Domain Model.

The Domain Model must contain:

* entities
* relationships
* ownership
* lifecycles
* invariants
* extension points
* event flow

Do not introduce new concepts.

The Domain Model is a consolidation artifact, not a design artifact.

---

### 4. Glossary Review

Review the glossary.

Ensure:

* every architectural term has exactly one definition
* retired terminology is listed only under "Avoid"
* no synonyms remain
* every ADR uses glossary terminology consistently

---

### 5. Architecture Discovery Brief

Review the Architecture Discovery Brief.

Do not rewrite history.

Instead:

* identify obsolete assumptions
* add a "Current Status" section
* reference Candidate ADRs where the architecture has evolved

The brief remains a discovery document.

It is **not** the specification.

---

### 6. Repository Review

Review the proposed repository changes.

Confirm:

* architecture artifacts only
* no implementation files
* no generated code
* no production configuration
* no secrets
* no environmental assumptions

List every file that will change.

---

### 7. Pull Request Review

Prepare—but do not create—a Pull Request.

Provide:

* Branch name
* Commit summary
* Pull Request title
* Pull Request description
* Files changed
* Review checklist

Do not commit.

Do not push.

Do not open the Pull Request.

Wait for approval.

---

### 8. Discovery Status

Determine whether architecture discovery has reached one of the following states.

* Continue Discovery
* Architecture Baseline Established
* Ready for Specification
* Ready for Implementation

Explain your reasoning.

If additional architecture discovery is recommended, identify only the remaining architectural questions.

Do **not** ask them yet.

---

### Constraints

Do not:

* write implementation code
* generate schemas
* create APIs
* produce tickets
* accept Candidate ADRs
* begin specification
* continue `grill-with-docs`

Your objective is to produce a clean, internally consistent architectural baseline.

Only after the baseline has been reviewed and approved should architecture discovery continue or the project transition to `to-spec`.
