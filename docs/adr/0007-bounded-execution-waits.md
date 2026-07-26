# Bounded execution waits

**Status:** accepted

Every execution wait is bounded by scanner-controlled behavior, never by trust
in server-advertised values. **Per wait:** every wait category has a concrete
maximum duration; the scanner never sleeps for an unbounded or unparseable
duration and never invents a delay. **Per logical request:** MAX_ATTEMPTS bounds
total attempts; at most one primary-rate-limit park is permitted, and it
consumes an attempt; if the retried request again affirmatively reports primary
exhaustion, the logical request terminates as a recorded failure rather than
parking again. **Per run:** logical requests are finite (eligible targets ×
active descriptors, plus the org-scoped requests); actual attempts are bounded
by logical requests × MAX_ATTEMPTS; primary parks by logical requests (one
each); the total theoretical wait by the finite number of permitted waits × their
explicit maxima. Budget-based duration arithmetic is a labeled operational
estimate with stated assumptions, never a guarantee.

**Precedence:** (1) a valid `Retry-After` on a retryable rate-limit response —
honored subject to its explicit maximum, recorded as a distinct wait category,
never treated as a primary park; a value exceeding its maximum is recorded as a
bounded transport failure, never clamped and retried early. (2) Affirmative
primary exhaustion — status 403 or 429, `x-ratelimit-remaining` parsed as
exactly zero, a parseable `x-ratelimit-reset`, and no valid higher-precedence
`Retry-After` — parks `max(0, reset_epoch − current_wall_time) + approved
slack`, subject to a concrete internal maximum park duration; a requested wait
exceeding it is not clamped and not retried before the advertised reset — it is
recorded as `rate_limit_reset_exceeds_maximum_park` and the logical request
terminates as a recorded failure. (3) Existing bounded handling for other
retryable responses. (4) Resource taxonomy classification. Remaining-zero with a
missing or unparseable reset honors a valid `Retry-After` or falls back to the
existing bounded retry, preserving a reason indicating unusable
primary-rate-limit reset evidence. A 403/429 lacking affirmative rate-limit
evidence never triggers a long park; after any bounded retry it reaches
taxonomy. Every execution-affecting wait is retained as evidence: category,
triggering request and attempt, triggering status, allowlisted rate-limit
headers, requested delay, actual elapsed delay (measured by monotonic clock),
applicable configured maximum, and post-wait outcome or termination reason.
Evidence envelopes keep individually truthful wall-clock capture timestamps.

## Consequences

- Sequential, single-threaded execution is Slice 2's secondary-limit mitigation
  and pacing strategy — risk reduction, not a guarantee that secondary limiting
  cannot occur.
- Reports derive wait visibility solely from retained evidence and never
  conflate planned logical requests with actual HTTP attempts.
- *Deferred pending estate facts (wayfinder ticket #6):* aggregate wall-clock
  budgets, aggregate parked-time budgets, maximum estate-size policy, operator
  rate-limit CLI controls, resumable/checkpointed collection; also deferred:
  concurrency, fixed inter-request delays, and adaptive pacing frameworks.
