"""Bounded, deterministic ranking. A model is built once for each scoring batch."""
from . import classifier
from .models import session, ScoreItem, Item
from .network import check_cancel


class Prioritizer:
    def __init__(self, topic='General'):
        self.topic = classifier.getTopic(topic) if isinstance(topic, str) else topic
        if self.topic is None:
            raise ValueError('Unknown topic')

    def listScoreItems(self, feed=None):
        query = session.query(ScoreItem).join(ScoreItem.item).filter(
            ScoreItem.topic_id == self.topic.id, Item.isUnread.is_(True))
        if feed is not None:
            query = query.filter(Item.feed_id == (feed if isinstance(feed, int) else feed.id))
        return query.all()

    def prioritize(self, rows):
        return sorted(rows, key=lambda row: (-row.score, -(row.item.updated or 0), -row.item.id))

    def calcScore(self, article):
        return classifier.model_for(self.topic.id).score(article)

    def setScores(self, rows, cancel=None):
        model = classifier.model_for(self.topic.id)
        try:
            for row in rows:
                check_cancel(cancel)
                row.score = model.score(row.item)
            session.commit()
        except Exception:
            session.rollback()
            raise
