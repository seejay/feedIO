#!/usr/bin/python3
"""
Classifier module for feedIO using TextBlob for cross-platform support.
"""

__version__ = "2.0.0"

import os
import pickle
import logging
import re
import hashlib
import tempfile
from textblob.classifiers import NaiveBayesClassifier

from . import config
from . import purify
from .models import session, Topic, Item, Feed, ScoreItem, ScoreFeed
from . import feedmanager as fm

def get_classifier_path(name, kind='body'):
    key = hashlib.sha256((kind + '\0' + name).encode('utf-8')).hexdigest()
    return os.path.join(config.CLASSIFIER_DIR, key + '.pickle')

def load_classifier(name, labels, kind='body'):
    path = get_classifier_path(name, kind)
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logging.error(f"Error loading classifier {name}: {e}")
    
    # Initial training data to avoid empty classifier errors
    initial_data = [([], labels[0]), ([], labels[1])]
    return NaiveBayesClassifier(initial_data)

def save_classifier(classifier, name, kind='body'):
    path = get_classifier_path(name, kind)
    descriptor, temporary = tempfile.mkstemp(dir=config.CLASSIFIER_DIR)
    try:
        with os.fdopen(descriptor, 'wb') as f:
            pickle.dump(classifier, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def listTopics():
    return session.query(Topic).all()

def addTopic(topic_title):
    if not topic_title:
        return None

    existing = session.query(Topic).filter_by(title=topic_title).first()
    if existing:
        return existing

    try:
        new_topic = Topic(title=topic_title)
        session.add(new_topic)
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Error adding topic: {e}")
        return None
    
    # Initialize classifiers
    safe_title = topic_title
    c = load_classifier(safe_title, [safe_title, "not" + safe_title])
    save_classifier(c, safe_title)
    
    c_title = load_classifier(safe_title, [safe_title + "Title", "not" + safe_title + "Title"], kind="title")
    save_classifier(c_title, safe_title, kind="title")

    # Assign new topic to all existing items and feeds
    all_items = session.query(Item).all()
    all_feeds = session.query(Feed).all()
    
    for item in all_items:
        if new_topic not in item.topics:
            item.topics.append(new_topic)
    
    for feed in all_feeds:
        if new_topic not in feed.topics:
            feed.topics.append(new_topic)
            
    session.commit()
    return new_topic

def removeTopic(topic):
    topic_title = topic.title
    try:
        # Cascade delete should handle score_items and score_feeds if set up in models
        session.delete(topic)
        session.commit()
        
        # Remove classifier files
        safe_title = topic_title
        for suffix in ["body", "title"]:
            path = get_classifier_path(safe_title, suffix)
            if os.path.exists(path):
                os.remove(path)
    except Exception as e:
        session.rollback()
        logging.error(f"Error removing topic: {e}")

def voteArticle(upOrDown, item, topic):
    # Vote for the feed
    score_feed = session.query(ScoreFeed).filter_by(feed=item.feed, topic=topic).first()
    if score_feed:
        if upOrDown == "up":
            score_feed.score += 1
        else:
            score_feed.score -= 1
    
    safe_topic = topic.title
    text = purify.cleanText(item.description)
    title = purify.cleanText(item.title)

    # Update body classifier
    c = load_classifier(safe_topic, [safe_topic, "not" + safe_topic])
    label = safe_topic if upOrDown == "up" else "not" + safe_topic
    c.update([(re.findall(r"\w+", text.lower()), label)])
    save_classifier(c, safe_topic)

    # Update title classifier
    c_title = load_classifier(safe_topic, [safe_topic + "Title", "not" + safe_topic + "Title"], kind="title")
    label_title = safe_topic + "Title" if upOrDown == "up" else "not" + safe_topic + "Title"
    c_title.update([(re.findall(r"\w+", title.lower()), label_title)])
    save_classifier(c_title, safe_topic, kind="title")

    if topic.title != "General":
        general_topic = getTopic("General")
        if general_topic and upOrDown == "up":
            voteArticle("up", item, general_topic)

    session.commit()

def classifyArticleText(topic_title, text):
    safe_topic = topic_title
    c = load_classifier(safe_topic, [safe_topic, "not" + safe_topic])
    prob_dist = c.prob_classify(re.findall(r"\w+", text.lower()))
    classification = prob_dist.max()
    probability = prob_dist.prob(classification)
    return classification, probability

def classifyArticleTitle(topic_title, title):
    safe_topic = topic_title
    c = load_classifier(safe_topic, [safe_topic + "Title", "not" + safe_topic + "Title"], kind="title")
    prob_dist = c.prob_classify(re.findall(r"\w+", title.lower()))
    classification = prob_dist.max()
    probability = prob_dist.prob(classification)
    return classification, probability

def getTopic(topic_title):
    return session.query(Topic).filter_by(title=topic_title).first()

def initTopics():
    if not getTopic("General"):
        addTopic("General")

def assignItemsToTopics(item_list):
    all_topics = listTopics()
    for item in item_list:
        for topic in all_topics:
            if topic not in item.topics:
                item.topics.append(topic)
    session.commit()

def assignFeedsToTopics(feed_list):
    all_topics = listTopics()
    for feed in feed_list:
        for topic in all_topics:
            if topic not in feed.topics:
                feed.topics.append(topic)
    session.commit()
