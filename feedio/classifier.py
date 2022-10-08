#!/usr/bin/python

"""
Classifier module for feedIO. Provides necessary text classification capabilities
 that are needed to prioritize the articles fetched from web feeds.
"""


__version__ = "0.0.5"

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


from lib.crm import *
from models import *
import feedmanager as fm


USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
classifierDir=os.path.join(USERDIR,"classifier")


def listTopics():
    """
    Function to query the database for the available Topics. Returns a list
    with all the topics as Topic objects.
    """
    topicsList = Topic.query.all()
    return topicsList


def addTopic(topic):
    """
    Function to add a new topic, creates required classifier files and database entries.
    Also assigns the newly created topic with all the Item objects and Feed objects 
    in the table.
    """
    if topic is unicode(""):
        return None

    try:
        newTopic = Topic(title = unicode(topic))
        session.commit()
    except:
        session.rollback()
        logging.debug("Error adding topic")
    else:
        topic = topic.replace(" ", "_")
        c = Classifier(classifierDir, [topic, "not"+topic])
        c2 = Classifier(classifierDir, [topic+"Title", "not"+topic+"Title"])
        logging.debug("Added new topic %s" % unicode(topic))

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
            logging.debug("Error Assigning new topic to all Items!")


def removeTopic(topic):
    """
    Function to remove a Topic. First removes all the ScoreItem objects from
    the ScoreItem table and then removes all the ScoreFeed objects from the
    ScoreFeed table.
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
        logging.debug("Error removing Items")
    else:
        logging.debug("removed Topic %s" % topicTitle)


def assignItemsToTopics(itemList):
    """
    Assigns a list of Item objects to all the Topic objects available.
    This will create an ScoreItem object for each Item and Topic pair to hold 
    the priority score of an Item under a particular topic.
    """
    allTopics = Topic.query.all()
    logging.debug("assigning the new articles to topics..")

    for item in itemList:
        for topic in allTopics:
            setItemTopic(item, topic, False)
    try:
        session.commit()
    except:
        session.rollback()
        logging.debug("Error Assigning Topics")


def setItemTopic(item, topic, commit=True):
    """
    Assigns an Item to a given Topic. This will create a ScoreItem object.
    commit is set to True by default but should be disabled by passing False 
    when setting a Topic to a couple of Items at once to increase the performance.
    """
    if item.topics.count(topic) == 0:
        item.topics.append(topic)
        logging.debug("Added %s to %s" % (topic.title, item.title))

        if commit is True:
            try:
                session.commit() # disable individual commits to increse performance.
            except:
                session.rollback()
                logging.debug("Error in setItemTopic")
                return None


def assignFeedsToTopics(feedList):
    """
    Assigns a list of Feed objects to all the Topic objects available.
    This will create an ScoreFeed object for each Feed and Topic pair to hold 
    the reputation score (number of votes) of an Feed under a particular topic.
    """
    allTopics = Topic.query.all()
    logging.debug("assigning the new feed to topics..")

    for feed in feedList:
        for topic in allTopics:
            setFeedTopic(feed, topic, False)
    try:
        session.commit()
    except:
        session.rollback()
        logging.debug("Error Assigning Topics to feed")
        return None


def setFeedTopic(feed, topic, commit=True):
    """
    Assigns a feed to the given Topic. This will create a ScoreFeed object.
    commit is set to True by default but should be disabled by passing False 
    when setting a Topic to a couple of Feeds at once to increase the performance.
    """
    if feed.topics.count(topic) == 0:
        feed.topics.append(topic)
        logging.debug("Added %s to %s" % (topic.title, feed.title))

        if commit is True:
            try:
                session.commit() # disable individual commits to increse performance.
            except:
                session.rollback()
                logging.debug("Error in setItemTopic")
                return None



def getTopic(topicTitle):
    """
    This returns the Topic object when the Topic title is given. This is used
    to easily retrieve the Topic object from the title string which is being
    used mostly when dealing with the text classification process.
    """
    try:
        topic = Topic.query.filter_by(title = unicode(topicTitle))[0]
        return topic
    except:
        return None


def _voteFeed(upOrDown, feed, topic):
    """
    Function to add or subtract the number of votes of a Feed under a given
    Topic when getting an Up Vote or a Down Vote.
    """
    scoreFeed = ScoreFeed.query.filter_by(feed = feed, topic = topic).first()
    try:
        if upOrDown is "up":
            scoreFeed.score += 1
            logging.debug("Up voted %s under %s new score is  %d" % (feed.title, topic.title, scoreFeed.score))

        elif upOrDown is "down":
            scoreFeed.score -= 1
            logging.debug("Down voted %s under %s new score is  %d" % (feed.title, topic.title, scoreFeed.score))

        session.commit()
    except:
        session.rollback()


def removefromScoreTable(feed):
    """
    Function to remove the Scores of all the Items in a particular feed. This will
    remove all the ScoreItem objects of the Items that belong to a particular feed.
    """
    itemsList = fm.listItems(feed)
    for item in itemsList:
        removeItemScores(item)


def removeItemScores(itemToRemove):
    """
    Function to remove the Scores of a particular article Item. This will remove 
    all the ScoreItem objects for that Item under all the Topics.
    """
    itemsInTopics = ScoreItem.query.filter_by(item = itemToRemove).all()
    for item in itemsInTopics:
        item.delete()
    try:
        session.commit()
        logging.debug("removed from Scores")
    except:
        logging.debug("Error removing Scores")


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
        logging.debug("removed from Scores")
    except:
        logging.debug("Error removing Scores")


def voteArticle(upOrDown, item, topic):
    """
    voteArticle function, takes arguments upOrDown vote, topic to vote,
    and the text to vote for
    """
    # vote for the feed that the article belongs.
    _voteFeed(upOrDown, item.feed, topic)

    # we'll be working with strings from now on, so get the topic title.
    topic = topic.title
    # calls to CRM breaks when a topic title contains spaces, replace them with underscores.
    topic = topic.replace(" ", "_")

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

            # We sould only get the Upvote for general. So disabled the DownVote.
#            elif upOrDown is "down":
#                d.learn("notGeneral", text)
#                d2.learn("notGeneralTitle", title)
    except UnicodeEncodeError:
        logging.debug("Article content contains invalid characters!")


def classifyArticleText(topic,text):
    """
    function to calculate the matching probability of a given Article text to a
    specified topic.
    """

    # calls to CRM breaks when a topic title contains spaces, replace them with underscores.
    topic = topic.replace(" ", "_")

    c = Classifier(classifierDir, [topic,"not"+topic])

    try:
        (classification, probability) = c.classify(text)

    except UnicodeEncodeError:
        # return a default value for articles with character Errors
        #TODO: filter out the invalid characters
            (classification, probability) = ("not"+topic, 0)

    else:
        return (classification, probability)


def classifyArticleTitle(topic,title):
    """
    function to calculate the matching probability of a given Article Title to a
    specified Topic.
    """

    # calls to CRM breaks when a topic title contains spaces, replace them with underscores.
    topic = topic.replace(" ", "_")

    c = Classifier(classifierDir, [topic+"Title", "not"+topic+"Title"])

    try:
        (classification, probability) = c.classify(title)

    except UnicodeEncodeError:
        # return a default value for articles with character Errors
        #TODO: filter out the invalid characters
            (classification, probability) = ("not"+topic+"Title", 0)
    else:
        return (classification, probability)


def initTopics():
    """
    Function to initialize the user interest profile. Adds the Topic "General"
    by default.
    """

    #Add the "General" interest topic by default
    if not getTopic("General"):
        addTopic(unicode("General"))


def main():
    initTopics()

if __name__ == "__main__":
    logging.debug(__doc__)
    main()
