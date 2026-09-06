"""Qt application controller. Designer owns layout; services own persistence."""
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from .UI.feedIO_ui import Ui_feedIO
from . import models as m, classifier, feedmanager as fm, prioritizer, purify
from . import portability, migration, reader
from .workers import TaskRunner
from .speechengine import SpeechEngine, SpeechUnavailable
from . import __version__


def refresh_job(feed_id=None, cancel=None):
    result = fm.updateFeed(feed_id, cancel) if feed_id else fm.updateAll(cancel)
    for topic in classifier.listTopics():
        if cancel.is_set():
            break
        p = prioritizer.Prioritizer(topic)
        p.setScores(p.listScoreItems(), cancel)
    return result


def rank_job(topic_id=None, cancel=None):
    for topic in classifier.listTopics():
        if cancel.is_set():
            break
        if topic_id is None or topic.id == topic_id:
            p = prioritizer.Prioritizer(topic)
            p.setScores(p.listScoreItems(), cancel)
    return 'Ranking recalculated'


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_feedIO()
        self.ui.setupUi(self)
        reader.configure(self.ui.viewArticle)
        self.runner = TaskRunner(self)
        self.runner.succeeded.connect(self.finished)
        self.runner.failed.connect(self.failed)
        self.runner.busyChanged.connect(self.busy_changed)
        self._quitting = False
        self._ready_to_close = False
        self.current_id = None
        self.bookmarks_only = False
        self.speech = SpeechEngine()
        self.close_to_tray = False
        self.notifications_enabled = True
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.fetch_all)
        self.timer.start(30 * 60 * 1000)
        self.speech_timer = QtCore.QTimer(self)
        self.speech_timer.timeout.connect(self.speech_status)
        self.speech_timer.start(500)
        self.tray = None
        self._setup_tray()
        bindings = {
            'actionAddFeed': self.add_feed, 'actionRemoveFeed': self.remove_feed,
            'actionManageFeeds': self.manage_feeds, 'actionFetchFeed': self.fetch_feed,
            'actionFetchAllFeeds': self.fetch_all, 'actionAddTopic': self.add_topic,
            'actionRemoveTopic': self.remove_topic, 'actionManageTopics': self.manage_topics,
            'actionExit': self.quit_app, 'actionMinimizeToTray': self.minimize,
            'actionVisitPage': self.visit_page, 'actionUpVote': lambda: self.vote('up'),
            'actionDownVote': lambda: self.vote('down'), 'actionUnread': self.mark_unread,
            'actionReCalculateScores': lambda: self.runner.submit(rank_job),
            'actionReCalculateTopicScores': lambda: self.runner.submit(rank_job, self.topic_id()),
            'actionRead': self.speak, 'actionFavorite': self.bookmark,
            'actionReadItLater': self.bookmark, 'actionPostToTwitter': self.copy_link,
            'actionPreferences': self.preferences, 'actionHelp': self.help,
            'actionAbout': self.about, 'actionTurnOffNotifications': lambda: self.notifications(False),
            'actionTurnOnNotifications': lambda: self.notifications(True),
        }
        for name, handler in bindings.items():
            getattr(self.ui, name).triggered.connect(lambda checked=False, fn=handler: self.invoke(fn))
        for name in ('actionSignInToTwitter', 'actionSignOffFromTwitter', 'actionSignInToRIL',
                     'actionSignOffFromRIL', 'actionTranslate_the_article'):
            getattr(self.ui, name).setVisible(False)
        self.ui.menu_Twitter.menuAction().setVisible(False)
        self.ui.menu_Read_It_Later.menuAction().setVisible(False)
        self.ui.actionReadItLater.setText('Save / unsave locally')
        self.ui.actionFavorite.setText('Toggle bookmark')
        self.ui.actionPostToTwitter.setText('Copy article link')
        self.ui.actionVisitPage.setText('Open original in browser')
        self.ui.actionMinimizeToTray.setEnabled(self.tray is not None)
        self.ui.btnUp.clicked.connect(lambda: self.invoke(lambda: self.vote('up')))
        self.ui.btnDown.clicked.connect(lambda: self.invoke(lambda: self.vote('down')))
        self.ui.comboFeed.currentIndexChanged.connect(self.display_items)
        self.ui.comboTopic.currentIndexChanged.connect(self.display_items)
        self.ui.listUnread.currentItemChanged.connect(lambda item, old: self.select_item(item))
        self.ui.listOld.currentItemChanged.connect(lambda item, old: self.select_item(item))
        self.ui.listUnread.itemDoubleClicked.connect(lambda item, column: self.visit_page())
        self.ui.listOld.itemDoubleClicked.connect(lambda item, column: self.visit_page())
        self._add_action(self.ui.menuFile, 'Import subscriptions (OPML)…', self.import_opml)
        self._add_action(self.ui.menuFile, 'Export subscriptions (OPML)…', self.export_opml)
        self._add_action(self.ui.menuFile, 'Back up profile…', self.backup)
        self._add_action(self.ui.menuFile, 'Import / restore profile…', self.import_profile)
        self.bookmark_action = self._add_action(self.ui.menuArticle, 'Show bookmarks only', self.toggle_bookmarks)
        self.bookmark_action.setCheckable(True)
        self._add_action(self.ui.menuArticle, 'Mark displayed articles read', self.mark_all_read)
        self._add_action(self.ui.menuTopics, 'Reset current topic learning', self.reset_learning)
        self.refresh_views()
        legacy = migration.legacy_profile()
        if legacy and not fm.listFeeds():
            self.statusBar().showMessage('Legacy profile found. Use Feeds → Import / restore profile to preserve your history.')
        notice = m.session.get(m.Setting, 'migration_notice')
        if notice:
            self.statusBar().showMessage(notice.value)
        self.setWindowTitle('feedIO ' + __version__)

    def _add_action(self, menu, title, handler):
        action = menu.addAction(title)
        action.triggered.connect(lambda checked=False: self.invoke(handler))
        return action

    def invoke(self, function):
        try:
            function()
        except Exception as error:
            m.session.rollback()
            self.failed(str(error) if isinstance(error, (ValueError, fm.FeedError, SpeechUnavailable))
                        else 'The operation failed. Saved data has been retained.')

    def _setup_tray(self):
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(':/images/feedIO.png'), self)
        menu = QtWidgets.QMenu(self)
        self._add_action(menu, 'Show feedIO', self.show_normal)
        self._add_action(menu, 'Refresh feeds', self.fetch_all)
        self._add_action(menu, 'Preferences', self.preferences)
        self._add_action(menu, 'Quit', self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda reason: self.show_normal()
            if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.setToolTip('feedIO')
        self.tray.show()

    def show_normal(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def feed_id(self):
        return self.ui.comboFeed.currentData()

    def topic_id(self):
        return self.ui.comboTopic.currentData()

    def refresh_views(self):
        m.session.expire_all()
        feed_id, topic_id = self.feed_id(), self.topic_id()
        for combo, values, previous, all_feeds in (
            (self.ui.comboFeed, fm.listFeeds(), feed_id, True),
            (self.ui.comboTopic, classifier.listTopics(), topic_id, False)):
            blocker = QtCore.QSignalBlocker(combo)
            combo.clear()
            if all_feeds:
                combo.addItem('All feeds', None)
            for value in values:
                combo.addItem(value.title, value.id)
            index = combo.findData(previous)
            combo.setCurrentIndex(index if index >= 0 else 0)
            del blocker
        self.display_items()

    def display_items(self, *args):
        previous = self.current_id
        self.current_id = None
        blockers = [QtCore.QSignalBlocker(self.ui.listUnread), QtCore.QSignalBlocker(self.ui.listOld)]
        self.ui.listUnread.clear()
        self.ui.listOld.clear()
        query = m.session.query(m.Item)
        if self.feed_id() is not None:
            query = query.filter_by(feed_id=self.feed_id())
        if self.bookmarks_only:
            query = query.filter_by(bookMarked=True)
        topic_id = self.topic_id()
        scores = dict(m.session.query(m.ScoreItem.item_id, m.ScoreItem.score).filter_by(topic_id=topic_id).all())
        items = query.order_by(m.Item.updated.desc(), m.Item.id.desc()).limit(1000).all()
        items.sort(key=lambda i: (not i.isUnread, -scores.get(i.id, 1000), -(i.updated or 0), -i.id))
        selected = None
        for item in items:
            node = QtWidgets.QTreeWidgetItem([('★ ' if item.bookMarked else '') + item.title])
            node.setData(0, QtCore.Qt.ItemDataRole.UserRole, item.id)
            node.setIcon(0, QtGui.QIcon(':/images/article.png'))
            node.setToolTip(0, f'{item.feed.title} · Score {scores.get(item.id, 1000)}')
            target = self.ui.listUnread if item.isUnread else self.ui.listOld
            target.addTopLevelItem(node)
            if item.id == previous:
                selected = (target, node)
        if selected:
            selected[0].setCurrentItem(selected[1])
            self.current_id = previous
        del blockers
        if self.current_id is None:
            self.ui.viewArticle.setHtml(reader.article_html('Welcome to feedIO',
                '<p>Add a feed or import subscriptions to begin. Select an article to read it offline.</p>'))
        self.update_actions()

    def select_item(self, node):
        if node is None:
            return
        identity = node.data(0, QtCore.Qt.ItemDataRole.UserRole)
        item = m.session.get(m.Item, identity)
        if item is None:
            return
        self.current_id = identity
        self.ui.viewArticle.setHtml(reader.article_html(item.title, item.description, item.feed.title))
        self.setWindowTitle(item.title + ' — feedIO')
        if item.isUnread:
            fm.setItemFlag(item, 2)
            self.display_items()
        self.update_actions()

    def update_actions(self):
        enabled = self.current_id is not None and not self.runner.busy
        for name in ('actionUpVote', 'actionDownVote', 'actionUnread', 'actionRead',
                     'actionVisitPage', 'actionFavorite', 'actionReadItLater', 'actionPostToTwitter'):
            getattr(self.ui, name).setEnabled(enabled)
        self.ui.btnUp.setEnabled(enabled)
        self.ui.btnDown.setEnabled(enabled)
        self.ui.actionRemoveFeed.setEnabled(self.feed_id() is not None and not self.runner.busy)
        self.ui.actionFetchFeed.setEnabled(self.feed_id() is not None and not self.runner.busy)

    def busy_changed(self, busy):
        self.ui.menuFile.setEnabled(not busy)
        self.ui.menuTopics.setEnabled(not busy)
        self.ui.menuTools.setEnabled(not busy)
        self.ui.listUnread.setEnabled(not busy)
        self.ui.listOld.setEnabled(not busy)
        self.ui.comboFeed.setEnabled(not busy)
        self.ui.comboTopic.setEnabled(not busy)
        for name in ('actionAddFeed', 'actionFetchAllFeeds', 'actionPreferences'):
            getattr(self.ui, name).setEnabled(not busy)
        self.update_actions()
        if busy:
            self.statusBar().showMessage('Working…')

    def finished(self, result):
        self.refresh_views()
        results = result if isinstance(result, list) else [result]
        errors = [r.error for r in results if isinstance(r, fm.RefreshResult) and r.error]
        added = sum(r.added for r in results if isinstance(r, fm.RefreshResult))
        message = '; '.join(errors) if errors else (result if isinstance(result, str) else f'Updated. {added} new articles.')
        self.statusBar().showMessage(message)
        if added and self.tray and self.notifications_enabled:
            self.tray.showMessage('feedIO', message)
        if self._quitting:
            self._ready_to_close = True
            self.close()

    def failed(self, message):
        self.statusBar().showMessage(message)
        if self._quitting:
            self._ready_to_close = True
            self.close()

    def add_feed(self):
        url, accepted = QtWidgets.QInputDialog.getText(self, 'Add feed', 'RSS, Atom, or website URL:')
        if accepted and url.strip():
            self.runner.submit(fm.addFeed, url.strip())

    def remove_feed(self):
        identity = self.feed_id()
        if identity is None:
            return
        if QtWidgets.QMessageBox.question(self, 'Remove feed', 'Remove this subscription and its saved articles?') == QtWidgets.QMessageBox.StandardButton.Yes:
            fm.removeFeed(identity)
            self.refresh_views()

    def manage_feeds(self):
        self.manage('Feeds', False)

    def manage_topics(self):
        self.manage('Topics', True)

    def manage(self, title, topics):
        values = classifier.listTopics() if topics else fm.listFeeds()
        values = [value for value in values if not topics or value.title != 'General']
        if not values:
            self.add_topic() if topics else self.add_feed()
            return
        labels = [f'{v.title} [{v.id}]' for v in values]
        label, accepted = QtWidgets.QInputDialog.getItem(self, 'Manage ' + title, 'Select to remove:', labels, editable=False)
        if accepted:
            value = values[labels.index(label)]
            if QtWidgets.QMessageBox.question(self, 'Confirm removal', 'Remove ' + value.title + '?') == QtWidgets.QMessageBox.StandardButton.Yes:
                classifier.removeTopic(value) if topics else fm.removeFeed(value)
                self.refresh_views()

    def add_topic(self):
        title, accepted = QtWidgets.QInputDialog.getText(self, 'Add topic', 'Interest name:')
        if accepted and title.strip():
            classifier.addTopic(title.strip())
            self.refresh_views()

    def remove_topic(self):
        topic = m.session.get(m.Topic, self.topic_id()) if self.topic_id() else None
        if topic is None or topic.title == 'General':
            self.statusBar().showMessage('The General topic cannot be removed.')
            return
        if QtWidgets.QMessageBox.question(self, 'Remove topic', 'Remove this interest and its learned preferences?') == QtWidgets.QMessageBox.StandardButton.Yes:
            classifier.removeTopic(topic)
            self.refresh_views()

    def fetch_feed(self):
        if self.feed_id() is not None:
            self.runner.submit(refresh_job, self.feed_id())

    def fetch_all(self):
        if not self._quitting:
            self.runner.submit(refresh_job)

    def current_item(self):
        return m.session.get(m.Item, self.current_id) if self.current_id else None

    def vote(self, value):
        item, topic = self.current_item(), m.session.get(m.Topic, self.topic_id())
        if item and topic:
            classifier.voteArticle(value, item, topic)
            self.runner.submit(rank_job, topic.id)

    def mark_unread(self):
        item = self.current_item()
        if item:
            fm.setItemFlag(item, 1)
            self.display_items()

    def mark_all_read(self):
        for widget in (self.ui.listUnread, self.ui.listOld):
            for index in range(widget.topLevelItemCount()):
                identity = widget.topLevelItem(index).data(0, QtCore.Qt.ItemDataRole.UserRole)
                fm.setItemFlag(identity, 2, False)
        m.session.commit()
        self.display_items()

    def bookmark(self):
        item = self.current_item()
        if item:
            item.bookMarked = not item.bookMarked
            item.favourite = item.bookMarked
            m.session.commit()
            self.display_items()

    def toggle_bookmarks(self):
        self.bookmarks_only = self.bookmark_action.isChecked()
        self.display_items()

    def visit_page(self):
        item = self.current_item()
        if item and item.url:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(portability.http_url(item.url)))

    def copy_link(self):
        item = self.current_item()
        if item:
            QtWidgets.QApplication.clipboard().setText(item.url)
            self.statusBar().showMessage('Article link copied.' if item.url else 'This entry has no original URL.')

    def speak(self):
        if self.speech.playing:
            self.speech.stop()
        elif self.current_item():
            item = self.current_item()
            self.speech.say(purify.cleanText(item.title + '. ' + item.description))

    def speech_status(self):
        if self.speech.error:
            self.statusBar().showMessage(self.speech.error)
            self.speech.error = None

    def import_opml(self):
        source, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Import subscriptions', '', 'OPML (*.opml *.xml)')
        if source:
            added = portability.import_opml(source)
            self.refresh_views()
            self.statusBar().showMessage(f'Imported {added} subscriptions. Refresh to retrieve articles.')

    def export_opml(self):
        destination, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Export subscriptions', 'feeds.opml', 'OPML (*.opml)')
        if destination:
            portability.export_opml(destination)

    def backup(self):
        destination, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Back up profile (choose a new filename)', 'feedio-backup.sqlite', 'SQLite (*.sqlite)')
        if destination:
            from .config import DB_FILE
            migration.snapshot(DB_FILE, destination)
            self.statusBar().showMessage('Profile backed up, including reading history and votes.')

    def import_profile(self):
        source, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Import into an empty profile', str(migration.legacy_profile() or ''), 'SQLite (*.sqlite *.db)')
        if source:
            migration.import_profile(source)
            classifier.initTopics()
            self.refresh_views()
            self.statusBar().showMessage('Profile imported. Legacy model binaries are preserved but not loaded.')

    def reset_learning(self):
        if self.topic_id() is not None:
            answer = QtWidgets.QMessageBox.question(self, 'Reset learning',
                'Remove this topic’s votes and reset its ranking? Reading history is preserved.')
            if answer == QtWidgets.QMessageBox.StandardButton.Yes:
                classifier.reset(self.topic_id())
                self.display_items()
                self.statusBar().showMessage('Topic learning reset.')

    def preferences(self):
        QtWidgets.QMessageBox.information(self, 'Preferences', 'Preferences are being migrated to profile storage.')

    def notifications(self, enabled):
        self.notifications_enabled = enabled

    def help(self):
        QtWidgets.QMessageBox.information(self, 'feedIO Help',
            'Feeds → Add feed accepts RSS, Atom, or website URLs. Refresh downloads articles for offline reading. '
            'Select an article to mark it read; use Mark as Unread to restore it. Vote under an interest to train ranking. '
            'Original pages open in your browser. Remote images and scripts are blocked in the reader. '
            'OPML transfers subscriptions; profile backups also preserve history and preferences. '
            'Lists show the latest 1,000 matching articles.')

    def about(self):
        QtWidgets.QMessageBox.about(self, 'About feedIO',
            'feedIO ' + __version__ + '\nA reader that learns your interests.\n'
            'Copyright 2011 SLIIT and feedIO contributors.\nGPL-3.0-or-later.\n'
            'Chanaka Jayamal, Lanka Amarasekara, Kolitha Gajanayake, Chamika Viraj.')

    def minimize(self):
        if self.tray:
            self.hide()
        else:
            self.showMinimized()

    def quit_app(self):
        self._quitting = True
        self.close()

    def closeEvent(self, event):
        if self.close_to_tray and self.tray and not self._quitting:
            self.hide()
            event.ignore()
            return
        self._quitting = True
        self.timer.stop()
        if self.runner.busy:
            self.runner.cancel.set()
            self.statusBar().showMessage('Finishing active request before closing…')
            event.ignore()
            return
        for item in fm.listNew():
            fm.setItemFlag(item, 1, False)
        m.session.commit()
        self.speech.stop()
        self.runner.shutdown()
        reader.close(self.ui.viewArticle)
        if self.tray:
            self.tray.hide()
        event.accept()


mainUI = MainWindow


def initUI():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setApplicationName('feedIO')
    app.setOrganizationName('feedIO')
    window = MainWindow()
    window.show()
    result = app.exec()
    window.deleteLater()
    app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    m.close()
    return result
