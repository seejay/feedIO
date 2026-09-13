"""Exercise actual Qt/WebEngine workflows with a disposable offline library."""
import argparse
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import time

parser = argparse.ArgumentParser()
parser.add_argument('--platform', choices=['offscreen', 'wayland', 'xcb'], default='offscreen')
parser.add_argument('--software-rendering', action='store_true')
parser.add_argument('--cycles', type=int, default=20)
parser.add_argument('--output', type=Path)
parser.add_argument('--screenshot', type=Path)
parser.add_argument('--installed', action='store_true', help='Use the installed package instead of this checkout')
args = parser.parse_args()
if args.cycles < 1:
    parser.error('--cycles must be positive')
os.environ['QT_QPA_PLATFORM'] = args.platform
os.environ['QT_QPA_PLATFORMTHEME'] = 'generic'
if args.software_rendering:
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = (
        os.environ.get('QTWEBENGINE_CHROMIUM_FLAGS', '') + ' --disable-gpu').strip()
if not args.installed:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

with tempfile.TemporaryDirectory(prefix='feedio-acceptance-') as profile:
    os.environ['FEEDIO_PROFILE'] = profile
    from feedio import classifier, config, models as m, migration, settings
    from feedio.ui import MainWindow, rank_job
    from PyQt6 import QtCore, QtGui, QtWidgets, QtTest

    app = QtWidgets.QApplication(['feedio-acceptance'])
    app.setQuitOnLastWindowClosed(False)
    m.initDB()
    topic = classifier.initTopics()
    feed = m.Feed(title='Acceptance library', url='https://example.test/rss')
    m.session.add(feed)
    m.session.flush()
    # The lead article exceeds WebEngine setHtml's data-URL size limit.
    long_body = '<p>' + ('Offline long article. ' * 110000) + '</p><p>END-OF-LONG-ARTICLE</p>'
    items = [m.Item(feed_id=feed.id, entry_id=str(i), title=f'Acceptance article {i}',
                    description=long_body if i == 0 else '<p>Offline science article.</p>',
                    updated=2000 - i, url=f'https://example.test/article/{i}')
             for i in range(1500)]
    m.session.add_all(items)
    m.session.flush()
    m.session.add_all([m.ScoreItem(topic_id=topic.id, item_id=item.id, score=5000) for item in items])
    m.session.commit()
    long_id = items[0].id
    del items
    window = MainWindow()
    report = {'platform': args.platform, 'software_rendering': args.software_rendering,
              'python': platform.python_version(), 'machine': platform.machine(),
              'qt': QtCore.qVersion(), 'cycles': args.cycles, 'articles': 1500,
              'article_bytes': len(long_body.encode()), 'checks': []}

    def wait_until(predicate, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            app.processEvents()
            if predicate():
                return
            time.sleep(0.01)
        raise AssertionError('Desktop operation timed out')

    def browser_contains(marker):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            result = []
            window.ui.viewArticle.page().toPlainText(result.append)
            wait_until(lambda: bool(result), timeout=5)
            if marker in result[0]:
                return
            QtTest.QTest.qWait(50)
        raise AssertionError('Browser did not render expected article content')

    try:
        window.show()
        browser_contains('Welcome to feedIO')
        window.ui.listUnread.setCurrentItem(window.ui.listUnread.topLevelItem(0))
        assert window.current_id == long_id
        browser_contains('END-OF-LONG-ARTICLE')
        report['checks'].append('long article rendered completely')
        window.ui.actionFavorite.trigger()
        assert m.session.get(m.Item, long_id).bookMarked
        window.ui.actionUnread.trigger()
        assert m.session.get(m.Item, long_id).isUnread
        report['checks'].append('read/unread and bookmark actions')

        heartbeat, gaps = [time.monotonic()], []
        timer = QtCore.QTimer()
        def tick():
            now = time.monotonic()
            gaps.append(now - heartbeat[0])
            heartbeat[0] = now
        timer.timeout.connect(tick)
        timer.start(20)
        start = time.monotonic()
        for cycle in range(args.cycles):
            window.page_offset = 0
            window.refresh_views()
            window.next_page.trigger()
            window.ui.listUnread.setFocus()
            QtTest.QTest.keyClick(window.ui.listUnread, QtCore.Qt.Key.Key_Down)
            assert window.current_id is not None
            window.ui.actionUpVote.trigger()
            wait_until(lambda: not window.runner.busy)
            window.ui.actionFavorite.trigger()
            # Reload ORM state between cycles to check durable flags/votes.
            m.session.remove()
            window.refresh_views()
        timer.stop()
        report['workflow_seconds'] = round(time.monotonic() - start, 3)
        report['maximum_event_gap_seconds'] = round(max(gaps, default=0), 3)
        assert max(gaps, default=0) < 5, 'GUI event loop stalled'
        report['checks'].append('repeated keyboard navigation/vote/rank/bookmark cycles')
        if args.screenshot:
            browser_contains(window.current_item().title)
            QtTest.QTest.qWait(200)
            args.screenshot.parent.mkdir(parents=True, exist_ok=True)
            assert window.grab().save(str(args.screenshot)), 'Could not save desktop screenshot'

        window.runner.submit(rank_job)
        window.cancel_button.click()
        wait_until(lambda: not window.runner.busy)
        assert window.isVisible() and not window._quitting
        report['checks'].append('cancel leaves window usable')

        # Clipboard contents are restored, including non-text formats.
        clipboard = app.clipboard()
        original = QtCore.QMimeData()
        previous = clipboard.mimeData()
        for mime in previous.formats() if previous is not None else []:
            original.setData(mime, previous.data(mime))
        try:
            window.copy_link()
            assert clipboard.text() == window.current_item().url
        finally:
            clipboard.setMimeData(original)
        report['checks'].append('clipboard copy and restore')

        if window.tray:
            window.close_to_tray = True
            window.close()
            assert not window.isVisible()
            window.show_normal()
            assert window.isVisible()
            report['checks'].append('tray close and reopen')
        report['tray_available'] = window.tray is not None
        report['screen_dpi'] = round(window.screen().logicalDotsPerInch(), 2)
        assert not QtGui.QPixmap(':/images/feedIO.png').isNull()

        idle_start = time.process_time()
        QtTest.QTest.qWait(1000)
        report['idle_main_process_cpu_seconds'] = round(time.process_time() - idle_start, 3)
        assert report['idle_main_process_cpu_seconds'] < 0.5, 'Excessive idle CPU use'

        settings.save(settings.Preferences(refresh_minutes=17))
        snapshot = Path(profile) / 'acceptance-backup.sqlite'
        migration.snapshot(config.DB_FILE, snapshot)
        votes = m.session.query(m.Vote).count()
        window.quit_app()
        assert not window.isVisible() and not window.runner.busy
        report['checks'].append('orderly quit')
        window.deleteLater()
        app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        window = None
        m.close()
        restored = Path(profile) / 'restored'
        config.USER_DIR = str(restored)
        config.DB_FILE = str(restored / 'feedIO.sqlite')
        config.CLASSIFIER_DIR = str(restored / 'classifier')
        m.initDB()
        migration.import_profile(snapshot)
        classifier.initTopics()
        window = MainWindow()
        window.show()
        assert m.session.query(m.Item).count() == 1500
        assert m.session.query(m.Vote).count() == votes
        assert m.session.get(m.Item, long_id).bookMarked
        assert window.timer.interval() == 17 * 60 * 1000
        window.page_offset = 0
        window.refresh_views()
        browser_contains('Welcome to feedIO')
        report['checks'].append('backup/restore and reopened desktop preserve data/settings')
        report['passed'] = True
    except Exception as error:
        report['passed'] = False
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        if window is not None:
            window.quit_app()
            wait_until(lambda: not window.runner.busy)
            window.deleteLater()
            app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
            app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
        m.close()
        text = json.dumps(report, indent=2)
        print(text)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + '\n', encoding='utf-8')
