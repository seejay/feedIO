from feedio import classifier as c, models as m, prioritizer


def article(feed, key, title, body):
    item = m.Item(feed=feed, entry_id=key, title=title, description=body)
    m.session.add(item)
    m.session.commit()
    return item


def test_learning_is_durable_idempotent_and_topic_local():
    topic = c.initTopics()
    other = c.addTopic('GeneralTitle')
    feed = m.Feed(title='Test', url='https://example.test/feed')
    m.session.add(feed)
    m.session.commit()
    positive = article(feed, 'one', 'Python programming', 'Python software development')
    held_out = article(feed, 'two', 'Python release', 'Software programming updates')
    baseline = c.model_for(topic.id).score(held_out)
    c.voteArticle('up', positive, topic)
    increased = c.model_for(topic.id).score(held_out)
    assert increased > baseline
    c.voteArticle('up', positive, topic)
    assert m.session.query(m.Vote).count() == 1
    assert c.model_for(topic.id).score(held_out) == increased
    assert c.model_for(other.id).score(held_out) == baseline
    topic_id, item_id = topic.id, held_out.id
    m.session.remove()
    assert c.model_for(topic_id).score(m.session.get(m.Item, item_id)) == increased
    c.voteArticle('down', m.session.query(m.Item).filter_by(entry_id='one').one(), m.session.get(m.Topic, topic_id))
    assert c.model_for(topic_id).score(m.session.get(m.Item, item_id)) < baseline
    c.reset(topic_id)
    assert c.model_for(topic_id).score(m.session.get(m.Item, item_id)) == baseline


def test_unsafe_names_and_corrupt_legacy_models_are_irrelevant(profile):
    (profile / 'classifier' / 'broken.pickle').write_bytes(b'not a model')
    topics = [c.addTopic(name) for name in ('Data Science', 'Data_Science', '../escape', 'ScienceTitle')]
    assert len({topic.id for topic in topics}) == 4
    assert all(c.model_for(topic.id).probability('unknown', 'title') == 0.5 for topic in topics)
