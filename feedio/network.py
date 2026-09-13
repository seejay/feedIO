"""Bounded HTTP retrieval, independent of parsing and database state."""
from dataclasses import dataclass
from urllib.parse import urljoin
import time
import requests
from .portability import http_url

MAX_BYTES = 5_000_000
TIMEOUT = (5, 10)


class FetchError(RuntimeError):
    pass


class Cancelled(FetchError):
    pass


class RetryableFetchError(FetchError):
    pass


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    headers: dict
    content: bytes
    permanent: bool = False


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled('Operation cancelled')


def retrieve(url, etag='', modified='', cancel=None):
    deadline = time.monotonic() + 30
    for attempt in range(2):
        try:
            return _retrieve(url, etag, modified, cancel, deadline)
        except RetryableFetchError:
            if attempt or time.monotonic() + 0.5 >= deadline:
                raise
            if cancel is not None:
                if cancel.wait(0.5):
                    raise Cancelled('Operation cancelled') from None
            else:
                time.sleep(0.5)


def _retrieve(url, etag, modified, cancel, deadline):
    url = http_url(url)
    headers = {'User-Agent': 'feedIO/2', 'Accept': 'application/atom+xml,application/rss+xml,application/xml,text/html;q=0.8'}
    if etag:
        headers['If-None-Match'] = etag
    if modified:
        headers['If-Modified-Since'] = modified
    redirected, permanent = False, True
    try:
        with requests.Session() as client:
            for hop in range(6):
                check_cancel(cancel)
                if time.monotonic() > deadline:
                    raise FetchError('Feed request exceeded its time budget')
                with client.get(url, headers=headers, stream=True, timeout=TIMEOUT,
                                allow_redirects=False) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        if not response.headers.get('Location'):
                            raise FetchError('Redirect did not include a destination')
                        url = http_url(urljoin(response.url, response.headers['Location']))
                        redirected = True
                        permanent = permanent and response.status_code in (301, 308)
                        headers.pop('If-None-Match', None)
                        headers.pop('If-Modified-Since', None)
                        continue
                    if response.status_code == 304:
                        return Response(response.url, 304, dict(response.headers), b'')
                    if response.status_code != 200:
                        error_class = RetryableFetchError if response.status_code in (500, 502, 503, 504) else FetchError
                        raise error_class(f'Feed server returned HTTP {response.status_code}')
                    chunks, size = [], 0
                    for chunk in response.iter_content(65536):
                        check_cancel(cancel)
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise FetchError('Feed exceeds the 5 MB limit')
                        if time.monotonic() > deadline:
                            raise FetchError('Feed request exceeded its time budget')
                        chunks.append(chunk)
                    return Response(response.url, 200, dict(response.headers), b''.join(chunks),
                                    redirected and permanent)
            raise FetchError('Too many feed redirects')
    except requests.RequestException as error:
        # Request exception strings may include private URL query parameters.
        raise RetryableFetchError('Unable to fetch feed. Check the network and server address.') from error
