#!/usr/bin/python
"""
prioritizer module for feedIO. Provides functionality to calculate the score of
 an article under a user interest topic and prioritizes the articles list
 according to their scores.

"""

__version__ = "0.0.1"

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


class Prioritizer:
    def __init__( self, topic = "General" ):
        self.topic = topic


    def prioritize(self, articleList):
        priorityList = []
        
        if articleList is not None:
            priorityList = sorted(articleList, key=attrgetter('generalScore'), reverse=True)
#           priorityList = sorted(priorityList, key=attrgetter('age'))

        return priorityList


    def setScores(self, articleList):
        """
        prioritizes the feedList
        """

        for article in articleList:
            self.calcScore(article)

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
        (textTopic, textScore) = classifier.classifyArticleText(self.topic, text)

#        print "text : %s, %s" % (textTopic, textScore)

        #Calculate the Score for the title of the article.
        (titleTopic,titleScore) = classifier.classifyArticleTitle(self.topic, titleText)
#        print "Title : %s, %s" % (titleTopic,titleScore)

        #Now set the textual scores to minus values if the article "notTopic"
        if textTopic ==self.topic:
            textScore = textScore * 10000
        else:
            textScore = textScore * (-100)

        if titleTopic ==self.topic:
            titleScore = titleScore * 10000
        else:
            titleScore = titleScore * (-100)

        #Get the Score for the feed from the db
        feedScore = article.feed.numVotes * 200

        #updateFrequencyScore - score based on the feeds update frequncy.
        #less frequently updated content would get fairly better scores.

        # Set weights to be given for the calculated individual scores.
        #TODO: Give an option for the user to set the weights of these scores from GUI.

        textScoreWeight = 0.55
        titleScoreWeight = 0.35
        feedScoreWeight = 0.1
#        updateFrequencyWeight = 0.1

        finalScore = ( ( textScoreWeight * textScore ) +
                        ( titleScoreWeight * titleScore ) +
                        ( feedScoreWeight * feedScore ) )
                        
#                        ( updateFrequencyWeight * updateFrequencyScore ) )

        article.generalScore = finalScore

        return article.generalScore

def main():
    pass

if __name__ == "__main__":
    print __doc__
    main()
