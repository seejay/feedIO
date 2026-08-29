#!/usr/bin/python3
"""
prioritizer module for feedIO.
"""

__version__ = "2.0.0"

import logging
from operator import attrgetter
from . import classifier
from . import purify
from .models import session, ScoreItem, ScoreFeed

TEXT_SCORE_WEIGHT = 0.45
TITLE_SCORE_WEIGHT = 0.45
FEED_SCORE_WEIGHT = 0.1

class Prioritizer(object):
    def __init__(self, topic="General"):
        if isinstance(topic, str):
            self.topic = classifier.getTopic(topic)
        else:
            self.topic = topic

    def prioritize(self, scoreItemsList):
        """
        Sorts the ScoreItemList according to the article scores.
        """
        if scoreItemsList:
            return sorted(scoreItemsList, key=attrgetter('score'), reverse=True)
        return []

    def listScoreItems(self, feed=None):
        """
        Lists all the ScoreItem objects under the self.topic.
        """
        query = session.query(ScoreItem).filter_by(topic=self.topic)
        scoreItemList = query.all()
        
        if feed:
            return [si for si in scoreItemList if si.item.feed == feed and si.item.isUnread]
        else:
            return [si for si in scoreItemList if si.item.isUnread]

    def setScores(self, scoreItemsList):
        """
        Sets the priority score for a given set of ScoreItems.
        """
        for scoreObject in scoreItemsList:
            scoreObject.score = int(self.calcScore(scoreObject.item))

        try:
            session.commit()
            logging.debug("Saved article scores")
        except Exception as e:
            session.rollback()
            logging.error(f"Error committing scores: {e}")

    def calcScore(self, article):
        """
        Calculates overall score for an article.
        """
        text = purify.cleanText(article.description)
        titleText = purify.cleanText(article.title)

        # Calculate the Score for the textual content
        (textTopic, textScore) = classifier.classifyArticleText(self.topic.title, text)
        
        # Calculate the Score for the title
        (titleTopic, titleScore) = classifier.classifyArticleTitle(self.topic.title, titleText)

        # Now set the textual scores to minus values if the article "notTopic"
        safe_topic = self.topic.title.replace(" ", "_")
        if textTopic == safe_topic:
            textScore = textScore * 10000
        else:
            textScore = textScore * (-100)

        if titleTopic == safe_topic + "Title":
            titleScore = titleScore * 10000
        else:
            titleScore = titleScore * (-100)

        # Get the Score for the feed from the db
        scoreFeed = session.query(ScoreFeed).filter_by(feed=article.feed, topic=self.topic).first()
        feedScore = (scoreFeed.score if scoreFeed else 1) * 100

        finalScore = ((TEXT_SCORE_WEIGHT * textScore) +
                      (TITLE_SCORE_WEIGHT * titleScore) +
                      (FEED_SCORE_WEIGHT * feedScore))
        
        return finalScore
