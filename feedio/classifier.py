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
        print "Error adding topic"
    else:
        c = Classifier(classifierDir, [topic, "not"+topic])
        c2 = Classifier(classifierDir, [topic+"Title", "not"+topic+"Title"])
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
        elif upOrDown is "down" and feed.numVotes > 1:
            feed.numVotes -= 1
            session.commit()
    except:
        session.rollback()


def voteArticle(upOrDown, item, topic="General"):
    """
    voteArticle function, takes arguments upOrDown vote, topic to vote,
    and the text to vote for
    """
    text = purify.cleanText(item.description)
    title = purify.cleanText(item.title)

    c = Classifier(classifierDir, [topic,"not"+topic])
    c2 = Classifier(classifierDir, [topic+"Title", "not"+topic+"Title"])
    try:
        if upOrDown is "up":
            c.learn(topic, text)
            c2.learn(topic+"Title", title)

        elif upOrDown is "down":
            c.learn("not"+topic, text)
            c2.learn("not"+topic+"Title", title)

        if topic is not "General":
            #always add the upvote to the General interest category as well.
            d = Classifier(classifierDir, ["General","notGeneral"])
            d2 = Classifier(classifierDir, ["GeneralTitle","notGeneralTitle"])
            if upOrDown is "up":
                d.learn("General", text)
                d2.learn("GeneralTitle", title)

            elif upOrDown is "down":
                d.learn("notGeneral", text)
                d2.learn("notGeneralTitle", title)
    except UnicodeEncodeError:
        print "Article content contains invalid characters!"


def classifyArticleText(topic,text):
    """
    function to calculate the matching probability of a given text to a
    specified topic. Add code to remove any tags in the code and generate a
    plain text string. Use the "markdown" module if needed.
    """
    c = Classifier(classifierDir, [topic,"not"+topic])

    try:
        (classification, probability) = c.classify(text)

    except UnicodeEncodeError:
        # return a dummy value for articles with character Errors
        #TODO: filter out the invalic characters
            (classification, probability) = ("not"+topic, 0)

    else:
        return (classification, probability)


def classifyArticleTitle(topic,title):
    """
    function to calculate the matching probability of a given text to a
    specified topic. Add code to remove any tags in the code and generate a
    plain text string. Use the "markdown" module if needed.
    """
    c = Classifier(classifierDir, [topic+"Title", "not"+topic+"Title"])

    try:
        (classification, probability) = c.classify(title)

    except UnicodeEncodeError:
        # return a dummy value for articles with character Errors
        #TODO: filter out the invalic characters
            (classification, probability) = ("not"+topic+"Title", 0)
    else:
        return (classification, probability)



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
