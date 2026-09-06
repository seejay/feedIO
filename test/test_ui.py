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
