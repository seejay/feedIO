"""Controller tests use real Qt widgets and a local text-browser substitute."""
import time
import pytest
from PyQt6 import QtWidgets, QtCore
from PyQt6 import QtWebEngineWidgets
from feedio import models as m, classifier, feedmanager as fm, ui
from feedio.network import Response
from pathlib import Path


@pytest.fixture(scope='session')
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication(['feedio-tests'])


@pytest.fixture
def window(app, monkeypatch):
    monkeypatch.setattr(QtWebEngineWidgets, 'QWebEngineView', QtWidgets.QTextBrowser)
    monkeypatch.setattr(ui.reader, 'configure', lambda view: None)
    monkeypatch.setattr(ui.reader, 'show_html', lambda view, html: view.setHtml(html))
    monkeypatch.setattr(QtWidgets.QSystemTrayIcon, 'isSystemTrayAvailable', lambda: False)
    classifier.initTopics()
    result = ui.MainWindow()
    yield result
    result.quit_app()
    wait_idle(result, app)
    result.deleteLater()
    app.processEvents()


def wait_idle(window, app):
    deadline = time.monotonic() + 10
    while window.runner.busy and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    assert not window.runner.busy


def test_action_subscribe_read_bookmark_restart(window, app, monkeypatch):
    content = (Path(__file__).parent / 'fixtures/rss.xml').read_bytes()
    monkeypatch.setattr(fm, 'retrieve', lambda *a, **kw: Response('https://example.test/rss', 200, {}, content))
    monkeypatch.setattr(QtWidgets.QInputDialog, 'getText', lambda *a, **kw: ('https://example.test/rss', True))
    window.ui.actionAddFeed.trigger()
    wait_idle(window, app)
    assert window.ui.listUnread.topLevelItemCount() == 2
    window.ui.listUnread.setCurrentItem(window.ui.listUnread.topLevelItem(0))
    identity = window.current_id
    assert m.session.get(m.Item, identity).age == 2
    assert window.ui.listOld.topLevelItemCount() == 1
    window.ui.actionFavorite.trigger()
    assert m.session.get(m.Item, identity).bookMarked
    window.ui.actionUnread.trigger()
    assert m.session.get(m.Item, identity).isUnread
    m.session.remove()
    assert m.session.get(m.Item, identity).bookMarked


def test_add_topic_action_and_empty_selection(window, monkeypatch):
    monkeypatch.setattr(QtWidgets.QInputDialog, 'getText', lambda *a, **kw: ('World/News', True))
    window.ui.actionAddTopic.trigger()
    assert classifier.getTopic('World/News')
    assert not window.ui.actionUpVote.isEnabled()
    assert not window.ui.actionMinimizeToTray.isEnabled()


def test_shutdown_cancels_worker(window, app):
    def waiting(cancel=None):
        cancel.wait(2)
        return 'Cancelled safely'
    window.runner.submit(waiting)
    window.quit_app()
    wait_idle(window, app)
    assert window._quitting


def test_cancel_button_keeps_window_open(window, app):
    from feedio.network import check_cancel
    def waiting(cancel=None):
        cancel.wait(2)
        check_cancel(cancel)
    window.show()
    window.runner.submit(waiting)
    assert window.cancel_button.isVisible() and window.cancel_button.isEnabled()
    window.cancel_button.click()
    wait_idle(window, app)
    assert window.isVisible() and not window._quitting
    assert not window.cancel_button.isVisible()
    assert 'cancelled' in window.statusBar().currentMessage().lower()


def test_failed_close_write_keeps_window_usable(window, monkeypatch):
    from PyQt6.QtGui import QCloseEvent
    from sqlalchemy.exc import OperationalError
    feed = m.Feed(title='Saved', url='https://example.test/saved')
    item = m.Item(feed=feed, title='Unread')
    m.session.add(item)
    m.session.commit()
    identity = item.id
    real_commit = m.session.commit
    def fail():
        raise OperationalError('private SQL', {}, Exception('disk full'))
    monkeypatch.setattr(m.session, 'commit', fail)
    event = QCloseEvent()
    window.closeEvent(event)
    assert not event.isAccepted() and not window._quitting
    assert window.timer.isActive()
    assert 'could not' in window.statusBar().currentMessage().lower()
    assert 'private' not in window.statusBar().currentMessage()
    assert m.session.get(m.Item, identity).age == 0
    monkeypatch.setattr(m.session, 'commit', real_commit)
    window.closeEvent(event)
    assert event.isAccepted()
    assert m.session.get(m.Item, identity).age == 1


def test_all_historical_articles_accessible_and_globally_ranked(window):
    feed = m.Feed(title='Library', url='https://example.test/library')
    m.session.add(feed)
    m.session.flush()
    topic = classifier.getTopic('General')
    articles = [m.Item(feed_id=feed.id, entry_id=str(i), title=f'Article {i}', updated=i) for i in range(1003)]
    m.session.add_all(articles)
    m.session.flush()
    m.session.add_all([m.ScoreItem(item_id=item.id, topic_id=topic.id, score=9999 if i == 0 else 1000)
                       for i, item in enumerate(articles)])
    m.session.commit()
    window.refresh_views()
    assert window.ui.listUnread.topLevelItem(0).text(0) == 'Article 0'
    seen = set()
    while True:
        for index in range(window.ui.listUnread.topLevelItemCount()):
            seen.add(window.ui.listUnread.topLevelItem(index).data(0, QtCore.Qt.ItemDataRole.UserRole))
        if not window.next_page.isEnabled():
            break
        window.next_page.trigger()
    assert len(seen) == 1003
    assert window.page_offset == 1000
    window.previous_page.trigger()
    assert window.page_offset == 750
    window.page_offset = 0
    window.display_items()
    node = window.ui.listUnread.topLevelItem(0)
    identity = node.data(0, QtCore.Qt.ItemDataRole.UserRole)
    title = node.text(0)
    window.ui.listUnread.setCurrentItem(node)
    assert window.current_id == identity
    assert title in window.ui.viewArticle.toPlainText()
    assert 'Welcome to feedIO' not in window.ui.viewArticle.toPlainText()
    assert window.ui.actionUpVote.isEnabled()
