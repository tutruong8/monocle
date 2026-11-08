import os
import time
from urllib.parse import urlsplit
import httpx

USER_AGENT = f"monocle/0.1 (student project; {os.environ.get('CONTACT_EMAIL', 'no-contact')})"
MIN_INTERVAL = 1.0
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_last_request: dict[str, float] = {}

class SourceNotFoundError(Exception):
    """404: The source doesn't exist."""

def _wait_for_turn(url: str) -> None:
    host = urlsplit(url).netloc
    wait = _last_request.get(host, 0) + MIN_INTERVAL - time.time()
    if wait > 0:
        time.sleep(wait)
    _last_request[host] = time.monotonic()

def polite_get(url: str, **kwargs) -> httpx.Response:
    for attempt in (1, 2):
        _wait_for_turn(url)
        try:
            response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=30, **kwargs)
        except httpx.TimeoutException:
            if attempt == 2:
                raise
            continue
        if response.status_code in RETRYABLE_STATUS_CODES and attempt == 1:
            continue
        if response.status_code == 404:
            raise SourceNotFoundError(f"Source not found: {url}")
        response.raise_for_status()
        return response
    raise RuntimeError(f"Failed to fetch {url} after 2 attempts")