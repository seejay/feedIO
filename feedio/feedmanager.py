"""Transactional RSS/Atom ingestion and reading-state operations."""
from dataclasses import dataclass
import calendar
import hashlib
import time
import feedparser
from .models import session, Feed, Item, Topic
from .network import retrieve, check_cancel, FetchError, Cancelled
from .portability import http_url
from .lib import autorss


class FeedError(FetchError):
    pass


@dataclass(frozen=True)
class RefreshResult:
    feed_id: int
    added: int = 0
    updated: int = 0
    skipped: int = 0
    unchanged: bool = False
    error: str = ''


def _parse(response):
    data = feedparser.parse(response.content)
    if not data.get('version') or data.get('bozo'):
        raise FeedError('The server did not return a valid RSS or Atom feed')
    return data


def _header(response, name):
    return next((str(v) for k, v in response.headers.items() if k.lower() == name), '')


def addFeed(url, cancel=None):
    response = retrieve(http_url(url), cancel=cancel)
    try:
        data = _parse(response)
    except FeedError:
        discovered = autorss.discover(response)
        if discovered == response.url:
            raise
        response = retrieve(discovered, cancel=cancel)
        data = _parse(response)
    check_cancel(cancel)
    try:
        if session.query(Feed).filter_by(url=response.url).first():
            raise FeedError('This feed is already subscribed')
        feed = Feed(url=response.url, title=data.feed.get('title') or response.url,
                    description=data.feed.get('subtitle', ''))
        session.add(feed)
        feed.topics.extend(session.query(Topic).all())
        session.flush()
        result = _ingest(feed, data, cancel)
        feed.etag = _header(response, 'etag')
        feed.modified = _header(response, 'last-modified')
        feed.last_success = time.time()
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise


def _normalize(entry):
    title = str(entry.get('title') or 'Untitled article')
    content = entry.get('content') or []
    body = entry.get('summary') or (content[0].get('value', '') if content else '')
    body = str(body)
    link = str(entry.get('link') or '')
    try:
        link = http_url(link)
    except ValueError:
        link = ''
    identity = str(entry.get('id') or entry.get('guid') or link)
    if not identity:
        if title == 'Untitled article' and not body:
            raise ValueError('Empty entry')
        identity = 'sha256:' + hashlib.sha256((title + '\0' + body).encode()).hexdigest()
    stamp = entry.get('updated_parsed') or entry.get('published_parsed')
    try:
        updated = float(calendar.timegm(stamp)) if stamp else 0
    except (ValueError, TypeError, OverflowError):
        updated = 0
    return dict(entry_id=identity, title=title, description=body, url=link,
                updated=updated, author=str(entry.get('author') or ''))


def _addItem(feed, entry):
    values = _normalize(entry)
    item = session.query(Item).filter_by(feed_id=feed.id, entry_id=values['entry_id']).first()
    if item is None:
        item = Item(feed=feed, **values)
        session.add(item)
        item.topics.extend(session.query(Topic).all())
        return 'added'
    changed = any(getattr(item, key) != value for key, value in values.items())
    for key, value in values.items():
        setattr(item, key, value)
    return 'updated' if changed else 'skipped'


def _ingest(feed, data, cancel=None):
    counts = dict(added=0, updated=0, skipped=0)
    for entry in data.entries:
        check_cancel(cancel)
        try:
            counts[_addItem(feed, entry)] += 1
        except (ValueError, TypeError, AttributeError):
            counts['skipped'] += 1
    check_cancel(cancel)
    return RefreshResult(feed.id, **counts)


def fetchFeeds(feed, data):
    try:
        result = _ingest(feed, data)
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise


def updateFeed(feed, cancel=None):
    identity = feed if isinstance(feed, int) else feed.id
    feed = session.get(Feed, identity)
    if feed is None:
        return RefreshResult(identity, error='Feed no longer exists')
    try:
        response = retrieve(feed.url, feed.etag, feed.modified, cancel)
        check_cancel(cancel)
        if response.status == 304:
            feed.last_success = time.time()
            feed.last_error = ''
            session.commit()
            return RefreshResult(feed.id, unchanged=True)
        data = _parse(response)
        result = _ingest(feed, data, cancel)
        if response.permanent and response.url != feed.url:
            duplicate = session.query(Feed).filter_by(url=response.url).first()
            if duplicate and duplicate.id != feed.id:
                raise FeedError('Redirect points to another subscription; remove the duplicate first')
            feed.url = response.url
        feed.title = data.feed.get('title') or feed.title
        feed.etag = _header(response, 'etag')
        feed.modified = _header(response, 'last-modified')
        feed.last_success = time.time()
        feed.last_error = ''
        session.commit()
        return result
    except Cancelled:
        session.rollback()
        raise
    except Exception as error:
        session.rollback()
        message = str(error) if isinstance(error, (FetchError, ValueError)) else 'Unable to save feed update'
        feed = session.get(Feed, identity)
        if feed:
            feed.last_error = message
            try:
                session.commit()
            except Exception:
                session.rollback()
        return RefreshResult(identity, error=message)


def updateAll(cancel=None):
    identities = [f.id for f in listFeeds()]
    results = []
    for identity in identities:
        check_cancel(cancel)
        results.append(updateFeed(identity, cancel))
    return results


def removeFeed(feed):
    obj = session.get(Feed, feed if isinstance(feed, int) else feed.id)
    if obj is None:
        return
    try:
        session.delete(obj)
        session.commit()
    except Exception:
        session.rollback()
        raise


def listFeeds():
    return session.query(Feed).order_by(Feed.title, Feed.id).all()


def listItems(feed=None):
    query = session.query(Item)
    if feed is not None:
        query = query.filter_by(feed_id=feed if isinstance(feed, int) else feed.id)
    return query.order_by(Item.updated.desc(), Item.id.desc()).all()


def listNew(feed=None):
    return [item for item in listItems(feed) if item.age == 0]


def listUnread(feed=None):
    return [item for item in listItems(feed) if item.age == 1]


def listRead(feed=None):
    return [item for item in listItems(feed) if item.age == 2]


def setItemFlag(item, age=2, commit=True):
    if age not in (0, 1, 2):
        raise ValueError('Invalid read state')
    if isinstance(item, int):
        item = session.get(Item, item)
    if item is None:
        return
    item.age = age
    item.isUnread = age != 2
    if commit:
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
