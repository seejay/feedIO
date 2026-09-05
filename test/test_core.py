import threading
from types import SimpleNamespace

import pytest
from feedparser import FeedParserDict
from feedio import classifier, feedmanager as fm, models as m, purify


def test_purify():
    assert purify.cleanText('<p>Hello &amp; goodbye</p>') == 'Hello & goodbye'
    assert purify.cleanText(None) == ''
    assert purify.shorten('hello', 3) == 'hel..'


def test_feed_and_score_cascade():
    topic = m.Topic(title='General')
    feed = m.Feed(url='https://example.test/feed', title='Example')
    m.session.add_all([topic, feed])
    feed.topics.append(topic)
    m.session.commit()
    fm.fetchFeeds(feed, FeedParserDict(entries=[FeedParserDict(
        title='One', link='https://example.test/one', summary='<p>Text</p>')]))
    assert len(fm.listItems()) == 1
    assert m.session.query(m.ScoreItem).count() == 1
    fm.removeFeed(feed)
    assert not fm.listItems()
    assert m.session.query(m.ScoreItem).count() == 0


def test_fresh_topics_offline():
    classifier.initTopics()
    assert classifier.getTopic('General') is not None


def test_batch_flags():
    item = SimpleNamespace()
    fm.setItemFlag(item, 1, False)
    assert item.age == 1 and item.isUnread


def test_worker_session_is_separate():
    identities = []
    def identity():
        identities.append(id(m.session()))
        m.session.remove()
    identity()
    worker = threading.Thread(target=identity)
    worker.start()
    worker.join()
    assert identities[0] != identities[1]
