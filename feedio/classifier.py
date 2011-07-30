#!/usr/bin/python

"""
Classifier module for feedIO. Provides necessary text classification capabilities
 that are needed to prioritize the articles fetched from web feeds.
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


import sys
import os
import purify

USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
classifierDir=os.path.join(USERDIR,"classifier")

from lib.crm import *
from models import *
import feedmanager as fm


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

        #Now append the topic to every article in the db
        try:
            allItems = Item.query.all()
            allFeeds = Feed.query.all()
            for item in allItems:
                setItemTopic(item, newTopic, False)

            for feed in allFeeds:
                setFeedTopic(feed, newTopic, False)

            session.commit()
        except:
            session.rollback()
            print "Error Assignning new topic to all Items!"


def removeTopic(topic):
    """
    function to remove topic from the database.
    """
    topicTitle = topic.title
    try:
        scoreItems = ScoreItem.query.filter_by(topic = topic).all()
        scoreFeeds = ScoreFeed.query.filter_by(topic = topic).all()

        # First remove all the scoreItems from the ScoreItem table.
        for item in scoreItems:
            item.delete()
        # Now remove all the scoreFeeds from the ScoreFeed table.
        for feed in scoreFeeds:
            feed.delete()

        #Now delete the topic object
        topic.delete()
        session.commit()
    except:
        session.rollback()
        print "Error removing Items"
    else:
        print "removed Topic %s" % topicTitle


def assignItemsToTopics(itemList):
    """
    Assigns a list of items to all the topics available.
    """
    allTopics = Topic.query.all()
    print "assigning the new articles to topics.."

    for item in itemList:
        for topic in allTopics:
            setItemTopic(item, topic, False)
    try:
        session.commit()
    except:
        session.rollback()
        print "Error Assigning Topics"


def setItemTopic(item, topic, commit=True):
    """
    Assigns an Item to the given Topic.
    """
    if item.topics.count(topic) == 0:
        item.topics.append(topic)
        print "Added %s to %s" % (topic.title, item.title)

        if commit is True:
            try:
                session.commit() # disable individual commits to increse performance.
            except:
                session.rollback()
                print "Error in setItemTopic"
                return None


def assignFeedsToTopics(feedList):
    """
    Assigns a list of feeds to all the topics available.
    """
    allTopics = Topic.query.all()
    print "assigning the new feed to topics.."

    for feed in feedList:
        for topic in allTopics:
            setFeedTopic(feed, topic, False)
    try:
        session.commit()
    except:
        session.rollback()
        print "Error Assigning Topics to feed"
        return None


def setFeedTopic(feed, topic, commit=True):
    """
    Assigns a feed to the given Topic.
    """
    if feed.topics.count(topic) == 0:
        feed.topics.append(topic)
        print "Added %s to %s" % (topic.title, feed.title)

        if commit is True:
            try:
                session.commit() # disable individual commits to increse performance.
            except:
                session.rollback()
                print "Error in setItemTopic"
                return None



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


def removefromScoreTable(feed):
    """
    Function to remove the Scores of all the Items in a particular feed
    """
    itemsList = fm.listItems(feed)
    for item in itemsList:
        removeItemScores(item)

def removeItemScores(itemToRemove):
    """
    Function to remove the Scores of a particular article Item.
    """
    itemsInTopics = ScoreItem.query.filter_by(item = itemToRemove).all()
    for item in itemsInTopics:
        item.delete()
    try:
        session.commit()
        print "removed from Scores"
    except:
        print "Error removing Scores"


def removefromScoreFeeds(feed):
    """
    Function to remove the all Scores particular feed.
    """
    feedsList = fm.listFeeds()
    for feed in feedsList:
        removeFeedScores(feed)

def removeFeedScores(feedToRemove):
    """
    Function to remove the Scores of a particular article Item.
    """
    feedsInTopics = ScoreFeed.query.filter_by(feed = feedToRemove).all()
    for feed in feedsInTopics:
        feed.delete()
    try:
        session.commit()
        print "removed from Scores"
    except:
        print "Error removing Scores"


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
