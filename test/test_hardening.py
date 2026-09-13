"""Adversarial boundaries: no network, personal profiles or native audio required."""
import json
import sqlite3
import threading
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

import pytest
import requests
from feedio import network, migration, models as m, config, classifier, portability
from feedio import feedmanager as fm, reader, speechengine, settings


class HTTP:
    def __init__(self, status=200, headers=None, chunks=(b'feed',), url='https://example.test/rss'):
        self.status_code, self.headers, self.chunks, self.url = status, headers or {}, chunks, url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def iter_content(self, size):
        yield from self.chunks


def responses(monkeypatch, *values):
    iterator, calls = iter(values), []
    def get(client, url, **kwargs):
        calls.append((url, dict(kwargs['headers'])))
        return next(iterator)
    monkeypatch.setattr(requests.Session, 'get', get)
    return calls


@pytest.mark.parametrize('status', [401, 403, 404, 429, 500, 503])
def test_http_errors_are_actionable_without_body(monkeypatch, status):
    responses(monkeypatch, *[HTTP(status, chunks=(b'private detail',)) for _ in range(2)])
    monkeypatch.setattr(network.time, 'sleep', lambda seconds: None)
    with pytest.raises(network.FetchError, match=f'HTTP {status}') as error:
        network.retrieve('https://example.test/rss?secret=private')
    assert 'private' not in str(error.value)


def test_validators_and_redirect_boundaries(monkeypatch):
    calls = responses(monkeypatch, HTTP(301, {'Location': '/new'}), HTTP(url='https://example.test/new'))
    result = network.retrieve('https://example.test/rss', etag='v1', modified='yesterday')
    assert result.permanent
    assert calls[0][1]['If-None-Match'] == 'v1'
    assert 'If-None-Match' not in calls[1][1]
    responses(monkeypatch, *[HTTP(302, {'Location': '/loop'}) for _ in range(6)])
    with pytest.raises(network.FetchError, match='Too many'):
        network.retrieve('https://example.test/rss')
    responses(monkeypatch, HTTP(301, {'Location': 'file:///etc/passwd'}))
    with pytest.raises(ValueError):
        network.retrieve('https://example.test/rss')


def test_http_size_deadline_and_cancellation(monkeypatch):
    monkeypatch.setattr(network, 'MAX_BYTES', 4)
    responses(monkeypatch, HTTP(chunks=(b'123', b'45')))
    with pytest.raises(network.FetchError, match='limit'):
        network.retrieve('https://example.test/rss')
    event = threading.Event()
    event.set()
    with pytest.raises(network.Cancelled):
        network.retrieve('https://example.test/rss', cancel=event)
    ticks = iter([0, 31])
    monkeypatch.setattr(network.time, 'monotonic', lambda: next(ticks))
    with pytest.raises(network.FetchError, match='time budget'):
        network.retrieve('https://example.test/rss')


def test_request_exception_hides_credentials(monkeypatch):
    monkeypatch.setattr(network.time, 'sleep', lambda seconds: None)
    def failure(*args, **kwargs):
        raise requests.ConnectionError('private-token-and-body')
    monkeypatch.setattr(requests.Session, 'get', failure)
    with pytest.raises(network.FetchError) as error:
        network.retrieve('https://example.test/rss')
    assert 'private-token' not in str(error.value)


def test_transient_http_retries_once(monkeypatch):
    waits = []
    monkeypatch.setattr(network.time, 'sleep', waits.append)
    calls = responses(monkeypatch, HTTP(503), HTTP())
    assert network.retrieve('https://example.test/rss').status == 200
    assert len(calls) == 2 and waits == [0.5]


@pytest.mark.parametrize('url', ['file:///tmp/a', 'javascript:alert(1)', 'https://u:p@host/',
    'http://@host/', 'http://host:0/', 'http://host:70000/', 'http://host:no/', 'http://host/\nsecret'])
def test_reject_unsafe_urls(url):
    with pytest.raises(ValueError):
        portability.http_url(url)


def test_invalid_opml_is_atomic(profile):
    classifier.initTopics()
    source = profile / 'bad.opml'
    source.write_text('<opml><body><outline xmlUrl="https://example.test/ok"/>'
                      '<outline xmlUrl="file:///bad"/></body></opml>')
    with pytest.raises(ValueError):
        portability.import_opml(source)
    assert not m.session.query(m.Feed).count()
    source.write_text('<!DOCTYPE opml [<!ENTITY x "bad">]><opml/>')
    with pytest.raises(ValueError):
        portability.import_opml(source)


def test_schema_damage_and_future_version_leave_bytes_unchanged(profile):
    for name, sql in [('partial', f'PRAGMA user_version={m.SCHEMA_VERSION}; CREATE TABLE feed(id INTEGER);'),
                      ('future', 'PRAGMA user_version=999;')]:
        source = profile / (name + '.sqlite')
        with sqlite3.connect(source) as db:
            db.executescript(sql)
        before = source.read_bytes()
        with pytest.raises(ValueError):
            migration.prepare_database(source)
        assert source.read_bytes() == before


def test_interrupted_legacy_conversion_retains_original(profile, monkeypatch):
    source = profile / 'legacy.sqlite'
    with sqlite3.connect(source) as db:
        db.executescript("CREATE TABLE feed(url TEXT, title TEXT); INSERT INTO feed VALUES ('https://example.test/rss', 'News');")
    original = source.read_bytes()
    def interrupt(*args):
        raise OSError('simulated interrupted replacement')
    monkeypatch.setattr(migration.os, 'replace', interrupt)
    with pytest.raises(OSError):
        migration.prepare_database(source)
    assert source.read_bytes() == original
    assert list(profile.glob('legacy.sqlite.pre-v1-*.bak'))
    assert not list(profile.glob('migration-*.sqlite'))


def test_import_does_not_erase_preferences_without_feeds(profile):
    source = profile / 'copy.sqlite'
    migration.snapshot(config.DB_FILE, source)
    settings.save(settings.Preferences(refresh_minutes=7))
    with pytest.raises(ValueError, match='empty profile'):
        migration.import_profile(source)
    assert settings.load().refresh_minutes == 7


def test_reader_escapes_titles_and_removes_active_content():
    result = reader.article_html('<script>title</script>', '<script>bad()</script>'
        '<iframe src="https://tracker.test"></iframe><a href="javascript:bad()" onclick="bad()">link</a>'
        '<img src="file:///private" onerror="bad()"><p style="background:url(https://tracker.test)">ok</p>')
    assert '&lt;script&gt;title' in result
    for forbidden in ('<script>', '<iframe', 'onclick', 'onerror', 'file://', 'javascript:', 'tracker.test'):
        assert forbidden not in result


def test_offline_interceptor_blocks_remote_and_files():
    from PyQt6.QtCore import QUrl
    for url in ['https://tracker.test/a', 'file:///private', 'ftp://server/a',
                'feedio://reader/private', 'feedio://other/article']:
        blocked = []
        info = SimpleNamespace(requestUrl=lambda: QUrl(url), block=blocked.append)
        reader.OfflineRequests().interceptRequest(info)
        assert blocked == [True]


def test_article_scheme_accepts_only_its_document():
    from PyQt6.QtCore import QUrl
    for url, allowed in [('feedio://reader/article?revision=2', True),
                         ('feedio://reader/other', False),
                         ('file:///article', False),
                         ('https://reader/article', False)]:
        assert reader.is_article_url(QUrl(url)) is allowed
    from PyQt6.QtWebEngineCore import QWebEngineUrlRequestJob
    failed = []
    request = SimpleNamespace(requestUrl=lambda: QUrl('feedio://reader/article'),
                              requestMethod=lambda: b'POST', fail=failed.append)
    reader.ArticleContent(None).requestStarted(request)
    assert failed == [QWebEngineUrlRequestJob.Error.RequestDenied]


def test_speech_subprocess_cleanup_and_stop(monkeypatch):
    done = threading.Event()
    commands = []
    class Process:
        returncode = None
        def __init__(self, command, **kwargs):
            commands.append(command)
        def wait(self, timeout=None):
            assert done.wait(2)
            self.returncode = 0
            return 0
        def poll(self):
            return self.returncode
        def terminate(self):
            done.set()
    monkeypatch.setattr(speechengine.subprocess, 'Popen', Process)
    engine = speechengine.SpeechEngine()
    engine.say('private article')
    path = Path(commands[0][-1])
    assert json.loads(path.read_text())['text'] == 'private article'
    assert 'private article' not in str(commands)
    engine.stop()
    engine._worker.join(2)
    assert not engine.playing and not path.exists()


def test_malformed_dates_and_empty_entries():
    assert fm._normalize({'title': 'Undated', 'updated_parsed': 'invalid'})['updated'] == 0
    assert fm._normalize({'title': 'No URL'})['entry_id'].startswith('sha256:')
    with pytest.raises(ValueError, match='Empty'):
        fm._normalize({})


def test_corrupt_preferences_fall_back():
    m.session.add(m.Setting(key='preferences', value='{invalid'))
    m.session.commit()
    assert settings.load() == settings.Preferences()


def test_deleted_feed_identity_is_never_reused():
    topic = classifier.initTopics()
    feed = m.Feed(title='Old', url='https://example.test/old')
    item = m.Item(feed=feed, entry_id='one', title='Old article')
    m.session.add(item)
    m.session.commit()
    old_id = feed.id
    classifier.voteArticle('up', item, topic)
    fm.removeFeed(feed.id)
    fresh = m.Feed(title='New', url='https://example.test/new')
    m.session.add(fresh)
    m.session.commit()
    assert fresh.id > old_id
    assert str(fresh.id) not in classifier.model_for(topic.id).feeds


def test_v1_upgrade_retains_data_and_backup(profile):
    classifier.initTopics()
    m.session.add(m.Feed(title='Development v1', url='https://example.test/v1'))
    m.session.commit()
    m.close()
    with closing(sqlite3.connect(config.DB_FILE)) as db:
        db.execute('PRAGMA user_version=1')
    m.initDB()
    assert m.session.query(m.Feed).one().title == 'Development v1'
    assert list(profile.glob('*.pre-v2-*.bak'))


@pytest.mark.parametrize('operation', ['upgrade', 'import'])
def test_database_replacement_closes_sqlite_handles(profile, monkeypatch, operation):
    classifier.initTopics()
    source = profile / 'source.sqlite'
    migration.snapshot(config.DB_FILE, source)
    if operation == 'upgrade':
        m.close()
        with sqlite3.connect(config.DB_FILE) as db:
            db.execute('PRAGMA user_version=1')
        db.close()

    connections = []
    connect = sqlite3.connect
    replace = migration.os.replace

    def tracked_connect(*args, **kwargs):
        connection = connect(*args, **kwargs)
        connections.append(connection)
        return connection

    def checked_replace(*args):
        # Retain references so garbage collection cannot hide an open handle.
        # Windows cannot replace databases while SQLite still has them open.
        for connection in connections:
            with pytest.raises(sqlite3.ProgrammingError, match='closed database'):
                connection.execute('SELECT 1')
        return replace(*args)

    monkeypatch.setattr(migration.sqlite3, 'connect', tracked_connect)
    monkeypatch.setattr(migration.os, 'replace', checked_replace)
    try:
        if operation == 'upgrade':
            m.initDB()
        else:
            migration.import_profile(source)
        assert m.session.query(m.Topic).one().title == 'General'
    finally:
        for connection in connections:
            connection.close()


def test_mixed_refresh_votes_offline_and_restarts(monkeypatch):
    content = (Path(__file__).parent / 'fixtures/rss.xml').read_bytes()
    monkeypatch.setattr(fm, 'retrieve', lambda url, *args, **kw: network.Response(url, 200, {}, content))
    classifier.initTopics()
    identifiers = [fm.addFeed(f'https://example.test/feed/{i}').feed_id for i in range(12)]
    for cycle in range(6):
        assert all(not result.error for result in fm.updateAll())
        topic = classifier.getTopic('General')
        item = m.session.query(m.Item).order_by(m.Item.id).first()
        fm.setItemFlag(item, 2)
        classifier.voteArticle('up' if cycle % 2 else 'down', item, topic)
        m.close()
        m.initDB()
        assert m.session.query(m.Feed).count() == len(identifiers)
        assert m.session.query(m.Item).count() == 24
        assert m.session.query(m.Vote).count() == 1
    def offline(*args, **kwargs):
        raise network.FetchError('Offline fixture')
    monkeypatch.setattr(fm, 'retrieve', offline)
    assert all(result.error for result in fm.updateAll())
    assert m.session.query(m.Item).count() == 24
    assert m.session.query(m.Item).filter_by(isUnread=False).count() == 1


def test_second_process_cannot_open_locked_profile(profile):
    import subprocess
    import sys
    from PyQt6.QtCore import QLockFile
    lock = QLockFile(str(profile / 'feedio.lock'))
    assert lock.tryLock(0)
    try:
        result = subprocess.run([sys.executable, '-m', 'feedio', '--profile', str(profile), '--check'],
                                capture_output=True, text=True, timeout=15)
        assert result.returncode == 1
        assert 'Close other instances' in result.stderr
    finally:
        lock.unlock()


def test_failed_refresh_commit_retains_articles_and_validators(monkeypatch):
    from sqlalchemy.exc import OperationalError
    content = (Path(__file__).parent / 'fixtures/rss.xml').read_bytes()
    monkeypatch.setattr(fm, 'retrieve', lambda url, *args, **kw: network.Response(url, 200, {'ETag': 'old'}, content))
    classifier.initTopics()
    identity = fm.addFeed('https://example.test/rss').feed_id
    monkeypatch.setattr(fm, 'retrieve', lambda url, *args, **kw: network.Response(url, 200, {'ETag': 'new'}, content))
    real_commit = m.session.commit
    attempts = []
    def fail_once():
        attempts.append(1)
        if len(attempts) == 1:
            raise OperationalError('private SQL', {}, Exception('disk full'))
        real_commit()
    monkeypatch.setattr(m.session, 'commit', fail_once)
    result = fm.updateFeed(identity)
    assert result.error and 'private' not in result.error
    m.session.expire_all()
    assert m.session.get(m.Feed, identity).etag == 'old'
    assert m.session.query(m.Item).count() == 2
