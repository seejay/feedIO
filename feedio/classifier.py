#!/usr/bin/python

"""
Classifier module for feedIO. Provides necessary text classification capabilities
 that are needed to prioritize the articles fetched from web feeds.
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


import sys
import os
import purify

USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
classifierDir=os.path.join(USERDIR,"classifier")

from lib.crm import *
from models import *


def listTopics():
    topicsList = Topic.query.all()
    return topicsList


def addTopic(topic):
    """
    function to add a new topic, creates required classifier files and database entries.
    """
    if topic is unicode(""):
        return None

    try:
        newTopic = Topic(title = unicode(topic))
        session.commit()
    except:
        session.rollback()
    else:
        c = Classifier(classifierDir, [topic, "not"+topic])
        print "Added new topic %s" % unicode(topic)


def removeTopic(topic):
    """
    function to remove topic from the database.
    """
    try:
        topic.delete()
        session.commit()
    except:
        session.rollback()
        print "Error removing topic!"
    else:
        print "Removed topic %s" % unicode(topic)


def getTopic(topicTitle):
    """
    returns the Topic object when the Topics title is passed.
    """
    try:
        topic = Topic.query.filter_by(title = unicode(topicTitle))[0]
        return topic
    except:
        return None


def voteFeed(upOrDown, feed):
    try:
        if upOrDown is "up":
            feed.numVotes += 1
            session.commit()
        elif upOrDown is "down" and feed.numVotes >= 0:
            feed.numVotes -= 1
            session.commit()
    except:
        session.rollback()

def voteArticle(upOrDown, text, topic="General"):
    """
    voteArticle function, takes arguments upOrDown vote, topic to vote,
    and the text to vote for
    """
    text = purify.cleanText(text)

    c = Classifier(classifierDir, [topic,"not"+topic])
    try:
        if upOrDown is "up":
            c.learn(topic, text)

        elif upOrDown is "down":
            c.learn("not"+topic, text)

        if topic is not "General":
            #always add the upvote to the General interest category as well.
            d = Classifier(classifierDir, ["General","notGeneral"])
            if upOrDown is "up":
                d.learn("General", text)

            elif upOrDown is "down":
                d.learn("notGeneral", text)
    except UnicodeEncodeError:
        print "Article content contains invalid characters!"

def classifyArticle(topic,text):
    """
    function to calculate the matching probability of a given text to a
    specified topic. Add code to remove any tags in the code and generate a
    plain text string. Use the "markdown" module if needed.
    """
    c = Classifier(classifierDir, [topic,"not"+topic])
    try:
        (classification, probability) = c.classify(text)

        return (classification, probability)
    except UnicodeEncodeError:
        # return a dummy value for articles with character Errors
        #TODO: filter out the invalic characters
            return ("not"+topic, 0)


def calculateScore(item, topic="General"):
    """
    when an item is passed this function calculates its overall score, by
    adding content score + feed score + feed update frequency(should be
    caluculated by taking the deviation from the mean update friquency.)

    """
    pass

    # get only the plain text.

    text = purify.cleanText(item.description)

    titleText = purify.cleanText(item.title)

    #Calculate the Score for the texual content of the article

    textScore = classifyArticle(topic,text)

    titleScore = classifyArticle(titleText,text)

    #Get the Score for the feed from the db
    feedScore = item.feed.numVotes

    #updateFrequencyScore - score based on the feeds update frequncy.
    #less frequently updated content would get fairly better scores.

    # Set weights to be given for the calculated individual scores.
    #TODO: Give an option for the user to set the weights of these scores from GUI.

    textScoreWeight = 0.55
    titleScoreWeight = 0.25
    feedScoreWeight = 0.1
    updateFrequencyWeight = 0.1



    finalScore = ( ( textScoreWeight * textScore ) +
                    ( titleScoreWeight * titleScore ) +
                    ( feedScoreWeight * updateFrequencyScore ) +
                    ( updateFrequencyWeight * updateFrequencyScore ) )

    try:
        item.generalScore = finalScore
        session.commit()
    except:
        session.rollback()
        print "Error setting Article Score!"

def initTopics():
    """
    function to create the initial user interest profile.
    """

    #Add the "General" interest topic by default
    if not getTopic("General"):
        addTopic(unicode("General"))


def main():
    initTopics()

if __name__ == "__main__":
    print __doc__
    main()
