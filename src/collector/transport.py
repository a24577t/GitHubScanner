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


def get(base_url, path, token):
    """Perform a single authenticated GET; HTTP errors are results, not exceptions."""
    url = base_url.rstrip("/") + path
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
