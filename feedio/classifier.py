#!/usr/bin/python

"""
Author  : Chanaka Jayamal
Date    : 20/05/2011

Classifier module for feedIO.
Provides necessary text classification capabilities needed to prioritize the articles.
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

USERDIR=os.path.join(os.path.expanduser("~"),".feedIO")
classifierDir=os.path.join(USERDIR,"classifier")

sys.path.append("./lib")
sys.path.append("./UI")

from crm import *
from models import Topic

def addTopic(topic):
    """
    function to add a new topic, creates required classifier files and database entries.
    """
    c = Classifier(classifierDir, [topic, "not"+topic])
    
    newTopic = Topic(title = topic)
    
       
def removeTopic(topic):
    """
    function to remove topic from the database.
    """
    pass
    #add code to remove the topic passed to the function
    
def voteFeed(feed):
    feed.numVotes += 1
    
    
def voteArticle(upOrDown, text, topic="Good"):
    """
    voteArticle function, takes arguments upOrDown vote, topic to vote, 
    and text to vote for
    """
        
    c = Classifier(classifierDir, [topic,"not"+topic])
    
    if upOrDown is "up":
        c.learn(topic, text)
                
    elif upOrDown is "down":
        c.learn("not"+topic, text)
    
    if topic is not "Good":
        d = Classifier(classifierDir, ["Good","notGood"])
        if upOrDown is "up":
            d.learn("Good", text)
                    
        elif upOrDown is "down":
            d.learn("notGood"+topic, text)
            
            
def classifyArticle(topic,text):
    """
    function to calculate the matching probability of a given text to a 
    specified topic. Add code to remove any tags in the code and generate a 
    plain text string. Use the "markdown" module if needed.
    """
    c = Classifier(classifierDir, [topic,"not"+topic])
    
    (classification, probability) = c.classify(text)
    
    return (classification, probability)


def calculateScore(item, topic="Good"):
    """
    when an item is passed this function calculates its overall score, by 
    adding content score + feed score + feed update frequency(should be 
    caluculated by taking the deviation from the mean update friquency.)
        
    """
    pass
    text = textifyFunction(item.description) # get only the plain text.
    
    classificationScore = classifyArticle(topic,text)
    feedScore = item.feed.numVotes
    #updateFrequencyScore - score based on the feeds update frequncy. 
    #less frequently updated content would get fairly better scores.
    
