"""Disposable 10,000-article database/ranking budget, including ORM persistence."""
import os
from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory(prefix='feedio-library-') as profile:
    os.environ['FEEDIO_PROFILE'] = profile
    from feedio import models as m, classifier, prioritizer
    from sqlalchemy import event
    m.initDB()
    feed = m.Feed(title='Benchmark', url='https://example.test/benchmark')
    m.session.add(feed)
    m.session.flush()
    m.session.add_all([m.Item(feed_id=feed.id, entry_id=str(i), title='Space science research',
                      description='Astronomy missions discover new planets and distant galaxies. ' * 20)
                      for i in range(10000)])
    m.session.commit()
    start = time.perf_counter()
    topic = classifier.initTopics()
    topic_seconds = time.perf_counter() - start
    statements = []
    @event.listens_for(m.engine, 'before_cursor_execute')
    def count(connection, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith('SELECT'):
            statements.append(statement)
    ranker = prioritizer.Prioritizer(topic)
    start = time.perf_counter()
    ranker.setScores(ranker.listScoreItems())
    seconds = time.perf_counter() - start
    assert len(statements) <= 5, 'Per-article SQL queries have returned'
    assert seconds < 25 and topic_seconds < 5, 'Library responsiveness budget exceeded'
    print(f'10,000 articles: topic creation {topic_seconds:.3f}s; database ranking {seconds:.3f}s; {len(statements)} SELECTs')
    m.close()
