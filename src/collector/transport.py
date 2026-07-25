"""HTTP transport: GET-only (observation-only is structural), token never recorded."""
import datetime
import urllib.error
import urllib.request


class FetchResult:
    def __init__(self, url, status, headers, body_text, captured_at):
        self.url = url
        self.status = status
        self.headers = headers
        self.body_text = body_text
        self.captured_at = captured_at
        self.waits = []
        self.attempts = 1


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


MAX_ATTEMPTS = 3
MAX_WAIT_SECONDS = 60


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


def _rate_limited(result):
    if result.status == 429:
        return True
    return (result.status == 403
            and (result.headers.get("Retry-After")
                 or result.headers.get("x-ratelimit-remaining") == "0"))


def get(base_url, path, token):
    """Authenticated GET with bounded, recorded retries on rate limits and 5xx."""
    import time

    url = base_url.rstrip("/") + path
    waits, attempts = [], 0
    while True:
        attempts += 1
        result = _fetch_once(url, token)
        retryable = _rate_limited(result) or result.status >= 500
        if not retryable or attempts >= MAX_ATTEMPTS:
            result.waits, result.attempts = waits, attempts
            return result
        wait = min(int(result.headers.get("Retry-After", "1") or "1"), MAX_WAIT_SECONDS)
        waits.append(wait)
        time.sleep(wait)


def _has_next(headers):
    link = headers.get("Link", "")
    return any('rel="next"' in part for part in link.split(","))


def paginate(base_url, path, token, max_pages=100):
    """Drain a Link-paginated listing; returns (pages, complete)."""
    separator = "&" if "?" in path else "?"
    pages = []
    for number in range(1, max_pages + 1):
        page = get(base_url, f"{path}{separator}per_page=100&page={number}", token)
        pages.append(page)
        if page.status < 200 or page.status >= 300 or not _has_next(page.headers):
            return pages, True
    return pages, False
