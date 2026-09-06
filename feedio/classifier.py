"""Rebuildable, corpus-free preference models backed by transactional vote records.

Votes apply only to the selected topic. Repeating a vote is idempotent; changing
it replaces the evidence. No pickle or externally downloaded models are loaded.
"""
from collections import Counter
import hashlib
import math
from pathlib import Path
import re
from sqlalchemy import delete
from . import config, purify
from .models import session, Topic, Item, Feed, ScoreItem, ScoreFeed, Vote

MAX_TRAINING_VOTES = 2000
MAX_VOCABULARY = 20000
MAX_DOCUMENT_TOKENS = 256


def tokens(text):
    return set(re.findall(r"[^\W\d_]{2,}", (text or '')[:50000].casefold()))


def get_classifier_path(name, kind='body'):
    """Compatibility locator only. Legacy binary models are preserved, never read."""
    key = hashlib.sha256((kind + '\0' + name).encode()).hexdigest()
    return str(Path(config.CLASSIFIER_DIR) / (key + '.retired'))


class PreferenceModel:
    def __init__(self, votes):
        self.counts = {'title': {1: Counter(), -1: Counter()},
                       'body': {1: Counter(), -1: Counter()}}
        self.feeds = {}
        for vote in votes:
            for kind in self.counts:
                words = sorted(tokens(getattr(vote, kind)))[:MAX_DOCUMENT_TOKENS]
                self.counts[kind][vote.value].update(words)
            key = vote.item_key.split(':', 1)[0]
            totals = self.feeds.setdefault(key, [0, 0])
            totals[0] += vote.value
            totals[1] += 1
        self.vocabulary = {}
        for kind, labels in self.counts.items():
            combined = labels[1] + labels[-1]
            self.vocabulary[kind] = set(w for w, count in combined.most_common(MAX_VOCABULARY))
            for label in (1, -1):
                self.counts[kind][label] = Counter({w: n for w, n in labels[label].items()
                                                   if w in self.vocabulary[kind]})

    def probability(self, text, kind):
        words = sorted(tokens(text) & self.vocabulary[kind])[:MAX_DOCUMENT_TOKENS]
        if not words:
            return 0.5
        positive, negative = self.counts[kind][1], self.counts[kind][-1]
        # Smoothed token evidence, normalized by document length so long articles
        # do not dominate. Neutral prior stays neutral for unseen vocabulary.
        evidence = sum(math.log((positive[w] + 1) / (negative[w] + 1)) for w in words)
        evidence /= math.sqrt(len(words))
        return 1 / (1 + math.exp(-max(-20, min(20, evidence))))

    def score(self, article):
        body = self.probability(purify.cleanText(article.description), 'body')
        title = self.probability(purify.cleanText(article.title), 'title')
        total, count = self.feeds.get(str(article.feed_id), [0, 0])
        feed = 0.5 + 0.5 * total / (count + 2)
        return round(10000 * (0.45 * body + 0.45 * title + 0.10 * feed))


def model_for(topic_id):
    votes = session.query(Vote).filter_by(topic_id=topic_id).order_by(Vote.id.desc()).limit(MAX_TRAINING_VOTES).all()
    return PreferenceModel(votes)


def listTopics():
    return session.query(Topic).order_by(Topic.id).all()


def getTopic(title):
    return session.query(Topic).filter_by(title=title).first()


def addTopic(title):
    title = title.strip()
    if not title or len(title) > 100:
        raise ValueError('Topic names must contain between 1 and 100 characters')
    if getTopic(title):
        return getTopic(title)
    try:
        topic = Topic(title=title)
        session.add(topic)
        topic.items.extend(session.query(Item).all())
        topic.feeds.extend(session.query(Feed).all())
        session.commit()
        return topic
    except Exception:
        session.rollback()
        raise


def initTopics():
    return getTopic('General') or addTopic('General')


def removeTopic(topic):
    if isinstance(topic, int):
        topic = session.get(Topic, topic)
    if topic is None:
        return
    if topic.title == 'General':
        raise ValueError('The General topic cannot be removed')
    try:
        session.delete(topic)
        session.commit()
    except Exception:
        session.rollback()
        raise


def voteArticle(direction, item, topic):
    if direction not in ('up', 'down'):
        raise ValueError('Vote must be up or down')
    value = 1 if direction == 'up' else -1
    key = str(item.feed_id) + ':' + item.entry_id
    try:
        vote = session.query(Vote).filter_by(topic_id=topic.id, item_key=key).first()
        if vote:
            # One durable vote per article per topic. Repeated clicks don't train twice.
            vote.value = value
            vote.title = purify.cleanText(item.title)
            vote.body = purify.cleanText(item.description)
        else:
            session.add(Vote(topic_id=topic.id, item_key=key, title=purify.cleanText(item.title),
                             body=purify.cleanText(item.description), value=value, feed_url=item.feed.url))
        session.commit()
    except Exception:
        session.rollback()
        raise


def reset(topic_id):
    try:
        session.execute(delete(Vote).where(Vote.topic_id == topic_id))
        for row in session.query(ScoreItem).filter_by(topic_id=topic_id):
            row.score = 5000
        session.commit()
    except Exception:
        session.rollback()
        raise


def classifyArticleText(topic_title, text):
    topic = getTopic(topic_title)
    probability = model_for(topic.id).probability(text, 'body')
    return (topic.title, probability) if probability >= 0.5 else ('not' + topic.title, 1 - probability)


def classifyArticleTitle(topic_title, text):
    topic = getTopic(topic_title)
    probability = model_for(topic.id).probability(text, 'title')
    return (topic.title + 'Title', probability) if probability >= 0.5 else ('not' + topic.title + 'Title', 1 - probability)


def assignItemsToTopics(items):
    for item in items:
        for topic in listTopics():
            if topic not in item.topics:
                item.topics.append(topic)
    session.commit()


def assignFeedsToTopics(feeds):
    for feed in feeds:
        for topic in listTopics():
            if topic not in feed.topics:
                feed.topics.append(topic)
    session.commit()
