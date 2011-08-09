#!/usr/bin/python
"""
prioritizer module for feedIO. Provides functionality to calculate the score of
 an article under a user interest topic and prioritizes the articles list
 according to their scores.

"""

__version__ = "0.0.3"

__license__ = """
    Copyright (C) 2011 Sri Lanka Institute of Information Technology.

    feedIO is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    feedIO is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with feedIO.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Chanaka Jayamal <seejay@seejay.net>"

__developers__ = ["Chanaka Jayamal",
                  "Lanka Amarasekara",
                  "Kolitha Gajanayake",
                  "Chamika Viraj"]


import classifier
import feedmanager
import purify
from models import *
from operator import itemgetter, attrgetter


TEXT_SCORE_WEIGHT = 0.45
TITLE_SCORE_WEIGHT = 0.45
FEED_SCORE_WEIGHT = 0.1
UPDATE_FREQUENCY_WEIGHT = 0.1



class Prioritizer:
    def __init__(self, topic="General"):
            self.topic = topic


    def prioritize(self, scoreItemsList):
        """
        Sorts the ScoreItemList according to the article scores under the self.topic of the Prioritizer instance.
        """
        priorityList = []

        if scoreItemsList is not None:
            priorityList = sorted(scoreItemsList, key=attrgetter('score'), reverse=True)
#           priorityList = sorted(priorityList, key=attrgetter('age'))

        return priorityList


    def listScoreItems(self, feed=-1):
        """
        Lists all the ScoreItem objects under the self.topic of the Prioritizer instance.
        """
        scoreItemList = []

        if feed is (-1):
            scoreItemList = ScoreItem.query.filter_by(topic = self.topic).all()
            # Generator to return only the unread Items.
            scoreItemList = [scoreItem for scoreItem in scoreItemList if scoreItem.item.isUnread is True]

        else:
            scoreItemList = ScoreItem.query.filter_by(topic = self.topic).all()
            # Implement a generator here to get only the feeds of the "feed"
            scoreItemList = [scoreItem for scoreItem in scoreItemList if (scoreItem.item.feed is feed and scoreItem.item.isUnread is True)]

        return scoreItemList


    def setScores(self, scoreItemsList):
        """
        Sets the priority score under the self.topic for a given set of ScoreItems.
        """

        for scoreObject in scoreItemsList:
            scoreObject.score = self.calcScore(scoreObject.item)

        try:
            session.commit()
            print "Saved article scores"
        except:
            session.rollback()
            print "Error Commiting scores to the db"


    def calcScore(self, article):
        """
        when an article is passed this function calculates its overall score, by
        adding content score + feed score + feed update frequency(should be
        caluculated by taking the deviation from the mean update friquency.)

        """
        # Get the Article title and content in plain text.
        text = purify.cleanText(article.description)

        titleText = purify.cleanText(article.title)

        #Calculate the Score for the texual content of the article
        (textTopic, textScore) = classifier.classifyArticleText(self.topic.title, text)
        textTopic = textTopic.replace("_", " ")
#        print "text : %s, %s" % (textTopic, textScore)

        #Calculate the Score for the title of the article.
        (titleTopic,titleScore) = classifier.classifyArticleTitle(self.topic.title, titleText)
        titleTopic = titleTopic.replace("_", " ")

#        print "Title : %s, %s" % (titleTopic,titleScore)

        #Now set the textual scores to minus values if the article "notTopic"
        if textTopic ==self.topic.title:
            textScore = textScore * 10000
        else:
            textScore = textScore * (-100)

        if titleTopic ==self.topic.title+"Title":
            titleScore = titleScore * 10000
        else:
            titleScore = titleScore * (-100)

        #Get the Score for the feed from the db
        scoreFeed = ScoreFeed.query.filter_by(feed = article.feed, topic = self.topic).first()
        feedScore = scoreFeed.score * 100

        #updateFrequencyScore - score based on the feeds update frequncy.
        #less frequently updated content would get fairly better scores.

        # Set weights to be given for the calculated individual scores.
        #TODO: Give an option for the user to set the weights of these scores from GUI.

        textScoreWeight = TEXT_SCORE_WEIGHT
        titleScoreWeight = TITLE_SCORE_WEIGHT
        feedScoreWeight = FEED_SCORE_WEIGHT
#        updateFrequencyWeight = UPDATE_FREQUENCY_WEIGHT

        finalScore = ( ( textScoreWeight * textScore ) +
                        ( titleScoreWeight * titleScore ) +
                        ( feedScoreWeight * feedScore ) )

#                        ( updateFrequencyWeight * updateFrequencyScore ) )


        return finalScore

def main():
    pass

if __name__ == "__main__":
    print __doc__
    main()
