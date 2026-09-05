from pathlib import Path
from threading import Event
from sqlalchemy import select
import pytest
from feedio import feedmanager as fm, models as m, classifier
from feedio.network import Response, Cancelled
from feedio.lib.autorss import discover

FIXTURES = Path(__file__).parent / 'fixtures'


def response(name='rss.xml', **kwargs):
    return Response(kwargs.pop('url', 'https://example.test/rss'), 200,
                    {'Last-Modified': 'Tue, 14 Nov 2023 22:13:20 GMT', 'ETag': 'one'},
                    (FIXTURES / name).read_bytes(), **kwargs)


def test_subscribe_refresh_restart_and_read_state(monkeypatch):
    classifier.initTopics()
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: response())
    result = fm.addFeed('https://example.test/rss')
    assert result.added == 2
    feed = fm.listFeeds()[0]
    item = fm.listItems()[0]
    assert item.updated == 1700000000
    fm.setItemFlag(item, 2)
    refreshed = fm.updateFeed(feed.id)
    assert refreshed.added == 0
    assert not item.isUnread
    m.session.remove()
    with m.engine.connect() as db:
        assert len(db.execute(select(m.Item)).all()) == 2


def test_atom_body_redirect_and_304(monkeypatch):
    classifier.initTopics()
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: response('atom.xml'))
    fm.addFeed('https://example.test/rss')
    feed = fm.listFeeds()[0]
    assert 'Full article' in fm.listItems()[0].description
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: response('atom.xml', url='https://example.test/new', permanent=True))
    assert not fm.updateFeed(feed.id).error
    m.session.expire_all()
    assert fm.listItems()[0].feed.url.endswith('/new')
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: Response(feed.url, 304, {}, b''))
    assert fm.updateFeed(feed.id).unchanged


def test_bad_refresh_preserves_content_and_validators(monkeypatch):
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: response())
    fm.addFeed('https://example.test/rss')
    feed = fm.listFeeds()[0]
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: Response(feed.url, 200, {'ETag':'bad'}, b'<html>oops</html>'))
    assert fm.updateFeed(feed.id).error
    assert feed.etag == 'one'
    assert len(fm.listItems()) == 2


def test_discovery_relative_to_redirected_document():
    page = Response('https://example.test/blog/index.html', 200, {},
                    b'<link rel="alternate" type="application/rss+xml" href="feed.xml">')
    assert discover(page) == 'https://example.test/blog/feed.xml'


def test_cancellation_does_not_insert(monkeypatch):
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: response())
    cancel = Event()
    cancel.set()
    with pytest.raises(Cancelled):
        fm.addFeed('https://example.test/rss', cancel)
    assert not fm.listFeeds()
