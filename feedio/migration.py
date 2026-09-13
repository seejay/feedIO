"""Offline, backed-up conversion. Legacy model binaries are never deserialized."""
from contextlib import closing
from pathlib import Path
import os
import sqlite3
import tempfile
import uuid


def snapshot(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Backup destination must differ from the database')
    if destination.exists():
        raise ValueError('Backup destination already exists')
    with closing(sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True)) as old:
        with closing(sqlite3.connect(destination)) as new, new:
            old.backup(new)
    return destination


def _rows(connection, names):
    tables = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    matches = [t for t in tables if t.lower() in names]
    if not matches:
        matches = [t for t in tables if any(t.lower().endswith('_' + n) for n in names)]
    if len(matches) > 1:
        raise ValueError('Ambiguous legacy table names; import requires inspection')
    if not matches:
        return []
    table = matches[0].replace('"', '""')
    return [dict(r) for r in connection.execute(f'SELECT * FROM "{table}"')]


def convert_legacy(source, destination):
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    from . import models as m
    source, destination = Path(source), Path(destination)
    engine = m.make_engine(destination)
    try:
        m.Base.metadata.create_all(engine)
        with closing(sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True)) as old:
            old.row_factory = sqlite3.Row
            feed_rows = _rows(old, ['feed'])
            topic_rows = _rows(old, ['topic'])
            item_rows = _rows(old, ['item'])
            score_feeds = _rows(old, ['score_feed', 'scorefeed'])
            score_items = _rows(old, ['score_item', 'scoreitem'])
        if not feed_rows and not topic_rows and not item_rows:
            raise ValueError('No recognizable legacy feedIO records found')
        with Session(engine) as db, db.begin():
            feeds, topics, items = {}, {}, {}
            for row in feed_rows:
                feed = m.Feed(url=row['url'], title=row.get('title') or row['url'],
                              description=row.get('description') or '')
                db.add(feed)
                feeds[row['url']] = feed
            for row in topic_rows:
                title = row['title']
                topic = m.Topic(title=title)
                db.add(topic)
                topics[title] = topic
            if 'General' not in topics:
                topics['General'] = m.Topic(title='General')
                db.add(topics['General'])
            for row in item_rows:
                feed_key = row.get('feed_url', row.get('feed'))
                if feed_key not in feeds:
                    raise ValueError('Legacy article has no matching feed; original retained')
                item = m.Item(feed=feeds[feed_key], entry_id=row['url'], url=row['url'],
                              title=row.get('title') or 'Untitled article',
                              description=row.get('description') or '',
                              updated=row.get('updated') or 0,
                              age=row.get('age', 0), isUnread=bool(row.get('isUnread', True)),
                              favourite=bool(row.get('favourite', False)),
                              bookMarked=bool(row.get('bookMarked', False)))
                db.add(item)
                items[row['url']] = item
            db.flush()
            feed_scores = {(r.get('feed_url'), r.get('topic_title')): r.get('score', 1) for r in score_feeds}
            item_scores = {(r.get('item_url'), r.get('topic_title')): r.get('score', 1000) for r in score_items}
            for title, topic in topics.items():
                for url, feed in feeds.items():
                    db.add(m.ScoreFeed(feed=feed, topic=topic, score=feed_scores.get((url, title), 1)))
                for url, item in items.items():
                    db.add(m.ScoreItem(item=item, topic=topic, score=item_scores.get((url, title), 1000)))
            db.add(m.Setting(key='migration_notice', value='Legacy reading history imported. CRM/pickle training is not loaded; vote to retrain. Original files were preserved.'))
            db.execute(text(f'PRAGMA user_version={m.SCHEMA_VERSION}'))
        return len(feeds), len(items)
    finally:
        engine.dispose()


def prepare_database(path):
    from .models import SCHEMA_VERSION
    if not path.exists() or not path.stat().st_size:
        return
    with closing(sqlite3.connect(path)) as db:
        version = db.execute('PRAGMA user_version').fetchone()[0]
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        if version == SCHEMA_VERSION:
            from .models import Base
            for table in Base.metadata.sorted_tables:
                columns = {r[1] for r in db.execute(f'PRAGMA table_info("{table.name}")')}
                if not {column.name for column in table.columns}.issubset(columns):
                    raise ValueError('Profile schema is incomplete or damaged; restore a verified backup')
            if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise ValueError('Profile integrity check failed')
            if db.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Profile contains broken relationships')
            return
        if version > SCHEMA_VERSION:
            raise ValueError('This profile requires a newer version of feedIO')
        if not tables:
            return
    backup = path.with_name(path.name + f'.pre-v{2 if version == 1 else 1}-' + uuid.uuid4().hex[:8] + '.bak')
    snapshot(path, backup)
    descriptor, temporary = tempfile.mkstemp(prefix='migration-', suffix='.sqlite', dir=path.parent)
    os.close(descriptor)
    try:
        if version == 1:
            upgrade_v1(backup, temporary)
        else:
            convert_legacy(backup, temporary)
        prepare_database(Path(temporary))
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def upgrade_v1(source, destination):
    """Rebuild the development v1 schema so IDs cannot be reused after deletion."""
    from . import models as m
    engine = m.make_engine(destination)
    try:
        m.Base.metadata.create_all(engine)
        with closing(sqlite3.connect(destination, uri=True)) as target, target:
            target.execute('PRAGMA foreign_keys=ON')
            target.execute('ATTACH DATABASE ? AS old', (Path(source).resolve().as_uri() + '?mode=ro',))
            for table in m.Base.metadata.sorted_tables:
                columns = ','.join('"' + column.name + '"' for column in table.columns)
                target.execute(f'INSERT INTO "{table.name}" ({columns}) SELECT {columns} FROM old."{table.name}"')
            # Historical votes may outlive their deleted subscriptions. Reserve
            # their IDs as well so later subscriptions cannot inherit evidence.
            old_feed_ids = [int(row[0].split(':', 1)[0]) for row in target.execute('SELECT item_key FROM vote')
                            if row[0].split(':', 1)[0].isdigit()]
            maximum = max(old_feed_ids + [target.execute('SELECT coalesce(max(id),0) FROM feed').fetchone()[0]])
            target.execute("UPDATE sqlite_sequence SET seq=? WHERE name='feed'", (maximum,))
            if not target.execute("SELECT 1 FROM sqlite_sequence WHERE name='feed'").fetchone():
                target.execute("INSERT INTO sqlite_sequence(name,seq) VALUES ('feed',?)", (maximum,))
            target.execute(f'PRAGMA user_version={m.SCHEMA_VERSION}')
    finally:
        engine.dispose()


def import_profile(source):
    """Import into an empty active profile; caller must have stopped all workers."""
    from . import models as m, config
    source = Path(source)
    if not source.is_file():
        raise ValueError('Select a feedIO SQLite database')
    if (m.session.query(m.Feed).count() or m.session.query(m.Vote).count()
            or m.session.query(m.Topic).filter(m.Topic.title != 'General').count()
            or m.session.query(m.Setting).filter(m.Setting.key != 'migration_notice').count()):
        raise ValueError('Import requires an empty profile. Back up and use a new profile directory.')
    if source.resolve() == Path(config.DB_FILE).resolve():
        raise ValueError('Cannot import the active database into itself')
    snapshot(config.DB_FILE, str(config.DB_FILE) + '.before-import-' + uuid.uuid4().hex[:8] + '.bak')
    descriptor, temporary = tempfile.mkstemp(suffix='.sqlite', dir=Path(config.DB_FILE).parent)
    os.close(descriptor)
    Path(temporary).unlink()
    try:
        snapshot(source, temporary)
        prepare_database(Path(temporary))
        with closing(sqlite3.connect(temporary)) as check:
            if check.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Profile integrity check failed')
            if check.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Profile contains broken relationships')
        m.close()
        os.replace(temporary, config.DB_FILE)
        m.initDB()
    finally:
        Path(temporary).unlink(missing_ok=True)


def legacy_profile():
    candidate = Path.home() / '.feedIO' / 'feedIO.sqlite'
    return candidate if candidate.is_file() else None
