"""HTTP transport: GET-only (observation-only is structural), token never recorded."""
import datetime
import time
import types
import urllib.error
import urllib.request

MAX_ATTEMPTS = 3
RETRY_AFTER_MAX_SECONDS = 60
PARK_SLACK_SECONDS = 5
MAX_PARK_SECONDS = 3900

SYSTEM_CLOCK = types.SimpleNamespace(
    sleep=time.sleep, epoch=time.time, monotonic=time.monotonic
)

# Rate-limit context retained inside wait records (response headers only).
RATE_LIMIT_HEADERS = frozenset({
    "retry-after", "x-ratelimit-limit", "x-ratelimit-remaining",
    "x-ratelimit-reset", "x-ratelimit-used",
})


class FetchResult:
    def __init__(self, url, status, headers, body_text, captured_at):
        self.url = url
        self.status = status
        # HTTP header names are case-insensitive; normalize once so every
        # consumer (retry logic, pagination, evidence) reads lowercase keys.
        self.headers = {name.lower(): value for name, value in headers.items()}
        self.body_text = body_text
        self.captured_at = captured_at
        self.waits = []
        self.attempts = 1
        self.wait_records = []
        self.termination_reason = None


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fetch_once(url, token):
    request = urllib.request.Request(url, method="GET")
    request.add_header("Authorization", "Bearer " + token)
    request.add_header("Accept", "application/vnd.github+json")
    try:
        with urllib.request.urlopen(request) as resp:
            return FetchResult(
                url, resp.status, dict(resp.headers), resp.read().decode("utf-8"), _now()
            )
    except urllib.error.HTTPError as err:
        return FetchResult(
            url, err.code, dict(err.headers), err.read().decode("utf-8"), _now()
        )
    except (urllib.error.URLError, OSError) as err:
        # Transport-level failure: status 0, reason preserved (never the token).
        return FetchResult(url, 0, {}, f"transport error: {err.reason if hasattr(err, 'reason') else err}", _now())


def rate_limited(status, headers):
    """The affirmative rate-limit marker predicate, shared with derivation:
    429, or 403 carrying a Retry-After or zero-remaining marker."""
    if status == 429:
        return True
    return (status == 403
            and (headers.get("retry-after")
                 or headers.get("x-ratelimit-remaining") == "0"))


def parse_nonnegative_int(value):
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return parsed if parsed >= 0 else None


def _record_wait(result, attempt, category, requested, maximum, outcome,
                 reason=None):
    return {
        "category": category,
        "attempt": attempt,
        "status": result.status,
        "url": result.url,
        "rate_limit_headers": {
            name: value for name, value in result.headers.items()
            if name in RATE_LIMIT_HEADERS
        },
        "requested_seconds": requested,
        "elapsed_seconds": None,
        "maximum_seconds": maximum,
        "outcome": outcome,
        "reason": reason,
    }


def _refused(result, attempt, category, requested, maximum, outcome,
             reason=None):
    """A refused wait: recorded with zero elapsed time, never slept."""
    record = _record_wait(result, attempt, category, requested, maximum,
                          outcome, reason)
    record["elapsed_seconds"] = 0
    return record


def _wait_and_record(clock, result, attempt, category, requested, maximum,
                     reason, waits, records):
    record = _record_wait(result, attempt, category, requested, maximum,
                          "retried", reason)
    before = clock.monotonic()
    clock.sleep(requested)
    record["elapsed_seconds"] = round(clock.monotonic() - before, 3)
    records.append(record)
    waits.append(requested)


def _finish(result, attempts, waits, records, termination_reason):
    result.attempts = attempts
    result.waits = waits
    result.wait_records = records
    result.termination_reason = termination_reason
    return result


def get(base_url, path, token, clock=SYSTEM_CLOCK):
    """Authenticated GET with bounded, recorded waits per ADR-0007."""
    url = base_url.rstrip("/") + path
    waits, records = [], []
    attempts = 0
    # Fetches plus parks, each charged against MAX_ATTEMPTS (ADR-0007: a park
    # consumes an attempt). Distinct from ADR-0007's unenforced duration
    # "budgets" and from `attempts`, which reports actual fetches.
    attempts_charged = 0
    parked = False
    while True:
        attempts += 1
        attempts_charged += 1
        result = _fetch_once(url, token)
        marked = rate_limited(result.status, result.headers)
        if not marked and result.status < 500:
            return _finish(result, attempts, waits, records, None)
        # ADR-0007: remaining is parsed, and exhaustion means exactly zero.
        remaining_zero = (
            parse_nonnegative_int(result.headers.get("x-ratelimit-remaining"))
            == 0
        )
        reset = parse_nonnegative_int(result.headers.get("x-ratelimit-reset"))
        retry_after = parse_nonnegative_int(result.headers.get("retry-after"))
        # Remaining-zero with a missing/unparseable reset: the fallback wait
        # preserves the unusable-reset evidence reason (ADR-0007).
        reason = ("unusable-rate-limit-reset"
                  if marked and remaining_zero and reset is None else None)
        if marked and retry_after is not None:
            # Precedence 1: a valid Retry-After — bounded, never a park.
            if retry_after > RETRY_AFTER_MAX_SECONDS:
                # Never clamped, never retried early.
                records.append(_refused(result, attempts, "retry-after",
                                        retry_after, RETRY_AFTER_MAX_SECONDS,
                                        "retry-after-exceeds-maximum", reason))
                return _finish(result, attempts, waits, records,
                               "retry-after-exceeds-maximum")
            if attempts_charged >= MAX_ATTEMPTS:
                return _finish(result, attempts, waits, records, None)
            _wait_and_record(clock, result, attempts, "retry-after",
                             retry_after, RETRY_AFTER_MAX_SECONDS, reason,
                             waits, records)
            continue
        if marked and remaining_zero and reset is not None:
            # Precedence 2: affirmative primary exhaustion parks at most once.
            if parked:
                # Renewed affirmative exhaustion: terminate as a recorded
                # failure, never re-park (ADR-0007). The park is necessarily
                # records[-1]: parking charges the attempt budget, so no other
                # wait can occur between the park and this response.
                records[-1]["outcome"] = "renewed-exhaustion"
                return _finish(result, attempts, waits, records,
                               "rate_limit_renewed_exhaustion")
            if attempts_charged >= MAX_ATTEMPTS:
                return _finish(result, attempts, waits, records, None)
            requested = int(max(0, reset - clock.epoch())) + PARK_SLACK_SECONDS
            if requested > MAX_PARK_SECONDS:
                # Never clamped, never retried before the advertised reset.
                records.append(_refused(result, attempts, "primary-park",
                                        requested, MAX_PARK_SECONDS,
                                        "rate_limit_reset_exceeds_maximum_park"))
                return _finish(result, attempts, waits, records,
                               "rate_limit_reset_exceeds_maximum_park")
            _wait_and_record(clock, result, attempts, "primary-park",
                             requested, MAX_PARK_SECONDS, None, waits, records)
            parked = True
            attempts_charged += 1  # a park consumes an attempt (ADR-0007)
            continue
        # Precedence 3: existing bounded retry for other retryable responses.
        if attempts_charged >= MAX_ATTEMPTS:
            return _finish(result, attempts, waits, records, None)
        requested = min(retry_after if retry_after is not None else 1,
                        RETRY_AFTER_MAX_SECONDS)
        _wait_and_record(clock, result, attempts, "retry", requested,
                         RETRY_AFTER_MAX_SECONDS, reason, waits, records)


def _has_next(headers):
    link = headers.get("link", "")
    return any('rel="next"' in part for part in link.split(","))


def paginate(base_url, path, token, max_pages=100, clock=SYSTEM_CLOCK):
    """Drain a Link-paginated listing; returns (pages, complete)."""
    separator = "&" if "?" in path else "?"
    pages = []
    for number in range(1, max_pages + 1):
        page = get(base_url, f"{path}{separator}per_page=100&page={number}",
                   token, clock=clock)
        pages.append(page)
        if page.status < 200 or page.status >= 300:
            return pages, False
        if not _has_next(page.headers):
            return pages, True
    return pages, False
