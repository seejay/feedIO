"""Real loopback sockets exercise requests, streaming, parsing and persistence."""
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time
from urllib.parse import urlsplit

import pytest
import requests

from feedio import classifier, feedmanager as fm, models as m, network

_request = requests.sessions.Session.request
FIXTURES = Path(__file__).parent / 'fixtures'


@pytest.fixture
def local_http(monkeypatch):
    counts = Counter()
    started, release = threading.Event(), threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            return

        def handle(self):
            try:
                super().handle()
            except (BrokenPipeError, ConnectionResetError):
                # TLS and cancellation probes intentionally close the socket,
                # sometimes before the HTTP request line has been parsed.
                return

        def do_GET(self):
            counts[self.path] += 1
            self.respond()

        def send(self, body, status=200, **headers):
            self.send_response(status)
            self.send_header('Content-Length', str(len(body)))
            for key, value in headers.items():
                self.send_header(key.replace('_', '-'), value)
            self.end_headers()
            self.wfile.write(body)

        def respond(self):
            if self.path == '/redirect':
                self.send(b'', 301, Location='/blog/index.html')
            elif self.path == '/blog/index.html':
                self.send(b'<link rel="alternate" type="application/rss+xml" href="feed.xml">')
            elif self.path in ('/blog/feed.xml', '/rss'):
                if self.headers.get('If-None-Match') == 'one':
                    self.send(b'', 304)
                else:
                    self.send((FIXTURES / 'rss.xml').read_bytes(), ETag='one')
            elif self.path == '/atom':
                self.send((FIXTURES / 'atom.xml').read_bytes())
            elif self.path == '/relative':
                self.send(b'<rss version="2.0"><channel><title>Relative</title>'
                          b'<link>/</link><description>News</description><item>'
                          b'<title>Article</title><link>/article</link><guid>one</guid>'
                          b'<description>&lt;a href="/more"&gt;More&lt;/a&gt;</description>'
                          b'</item></channel></rss>')
            elif self.path == '/retry':
                self.send(b'busy' if counts[self.path] == 1 else b'ok',
                          503 if counts[self.path] == 1 else 200)
            elif self.path == '/large':
                self.send(b'x' * 65537)
            elif self.path == '/slow':
                started.set()
                release.wait(2)
                self.send(b'ok')
            elif self.path == '/stream':
                self.send_response(200)
                self.send_header('Content-Length', '131072')
                self.end_headers()
                self.wfile.write(b'x' * 65536)
                self.wfile.flush()
                started.set()
                release.wait(2)
                self.wfile.write(b'x' * 65536)
            elif self.path == '/truncated':
                self.send_response(200)
                self.send_header('Content-Length', '1000')
                self.end_headers()
                self.wfile.write(b'incomplete')
            else:
                self.send(b'not found', 404)

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01})
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'

    def loopback_only(client, method, url, **kwargs):
        assert urlsplit(url).hostname == '127.0.0.1', 'External HTTP is forbidden'
        client.trust_env = False
        return _request(client, method, url, **kwargs)

    monkeypatch.setattr(requests.sessions.Session, 'request', loopback_only)
    monkeypatch.setattr(network, 'TIMEOUT', (0.3, 0.3))
    try:
        yield base, counts, started, release
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        thread.join(3)
        assert not thread.is_alive()


def test_real_discovery_conditional_refresh_and_restart(local_http):
    base, counts, _, _ = local_http
    classifier.initTopics()
    result = fm.addFeed(base + '/redirect')
    assert result.added == 2
    item = m.session.query(m.Item).first()
    identity = item.id
    fm.setItemFlag(item, 2)
    assert fm.updateFeed(result.feed_id).unchanged
    m.close()
    m.initDB()
    assert m.session.get(m.Item, identity).isUnread is False
    assert m.session.query(m.Item).count() == 2
    assert counts['/blog/feed.xml'] == 2
    assert m.session.get(m.Feed, result.feed_id).url == base + '/blog/feed.xml'


def test_real_atom_and_relative_article_links(local_http):
    base, _, _, _ = local_http
    assert fm.addFeed(base + '/atom').added == 1
    relative = fm.addFeed(base + '/relative')
    item = m.session.query(m.Item).filter_by(feed_id=relative.feed_id).one()
    assert item.url == base + '/article'
    assert base + '/more' in item.description


def test_real_transient_retry(local_http):
    base, counts, _, _ = local_http
    assert network.retrieve(base + '/retry').content == b'ok'
    assert counts['/retry'] == 2


@pytest.mark.parametrize('path', ['/slow', '/truncated'])
def test_real_transport_failures_are_bounded(local_http, path):
    base, counts, _, _ = local_http
    start = time.monotonic()
    with pytest.raises(network.FetchError):
        network.retrieve(base + path)
    assert counts[path] == 2
    assert time.monotonic() - start < 4


def test_real_tls_failure(local_http):
    base, _, _, _ = local_http
    with pytest.raises(network.FetchError, match='network and server'):
        network.retrieve(base.replace('http:', 'https:') + '/rss')


def test_real_body_size_limit(local_http, monkeypatch):
    base, _, _, _ = local_http
    monkeypatch.setattr(network, 'MAX_BYTES', 65536)
    with pytest.raises(network.FetchError, match='limit'):
        network.retrieve(base + '/large')


def test_real_stream_cancellation(local_http):
    base, counts, started, release = local_http
    cancel = threading.Event()
    results = []
    def fetch():
        try:
            results.append(network.retrieve(base + '/stream', cancel=cancel))
        except Exception as error:
            results.append(error)
    worker = threading.Thread(target=fetch)
    worker.start()
    try:
        assert started.wait(2)
        cancel.set()
        release.set()
        worker.join(3)
        assert not worker.is_alive()
        assert len(results) == 1 and isinstance(results[0], network.Cancelled)
        assert counts['/stream'] == 1
    finally:
        cancel.set()
        release.set()
        worker.join(3)
