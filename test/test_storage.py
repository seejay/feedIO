import sqlite3
from pathlib import Path
import pytest
from sqlalchemy import text
from feedio import models as m, config, migration, portability, classifier


def test_redirect_identity_and_duplicate_url_across_feeds():
    first = m.Feed(title='First', url='https://example.test/first')
    second = m.Feed(title='Second', url='https://example.test/second')
    m.session.add_all([first, second])
    m.session.add_all([m.Item(feed=first, entry_id='same', url='https://example.test/a'),
                       m.Item(feed=second, entry_id='same', url='https://example.test/a')])
    m.session.commit()
    first.url = 'https://example.test/redirect'
    m.session.commit()
    m.session.expire_all()
    assert m.session.query(m.Item).filter_by(feed_id=first.id).one().feed.url.endswith('redirect')
    assert m.session.execute(text('PRAGMA foreign_keys')).scalar() == 1


def test_legacy_conversion(profile):
    source = profile / 'old.sqlite'
    with sqlite3.connect(source) as db:
        db.executescript('''CREATE TABLE models_feed (url TEXT, title TEXT);
        CREATE TABLE models_topic (title TEXT);
        CREATE TABLE models_item (url TEXT, title TEXT, feed_url TEXT, age INTEGER, isUnread INTEGER);
        INSERT INTO models_feed VALUES ('https://example.test/rss', 'Old');
        INSERT INTO models_topic VALUES ('General');
        INSERT INTO models_item VALUES ('https://example.test/one', 'Read', 'https://example.test/rss', 2, 0);''')
    migration.import_profile(source)
    assert m.session.query(m.Item).one().age == 2
    assert m.session.query(m.Item).one().feed.title == 'Old'
    assert source.exists()
    assert list(profile.glob('*.before-import-*.bak'))
    with pytest.raises(ValueError, match='empty profile'):
        migration.import_profile(source)


def test_opml_roundtrip_and_snapshot(profile):
    classifier.initTopics()
    m.session.add(m.Feed(url='https://example.test/rss', title='සිංහල & news'))
    m.session.commit()
    portability.export_opml(profile / 'feeds.opml')
    assert portability.import_opml(profile / 'feeds.opml') == 0
    migration.snapshot(config.DB_FILE, profile / 'backup.sqlite')
    with sqlite3.connect(profile / 'backup.sqlite') as db:
        assert db.execute('select title from feed').fetchone()[0] == 'සිංහල & news'


def test_classifier_paths_are_confined(profile):
    assert Path(classifier.get_classifier_path('../escape')).parent == profile / 'classifier'
    assert classifier.get_classifier_path('Data Science') != classifier.get_classifier_path('Data_Science')
    assert classifier.get_classifier_path('Science', 'title') != classifier.get_classifier_path('ScienceTitle')
