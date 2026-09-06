"""Actual WebEngine smoke test with a temporary profile and no remote content."""
import os
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
with tempfile.TemporaryDirectory(prefix='feedio-smoke-') as profile:
    os.environ['FEEDIO_PROFILE'] = profile
    from feedio import models, classifier
    from feedio.ui import MainWindow
    from PyQt6 import QtWidgets, QtCore, QtGui
    models.initDB()
    classifier.initTopics()
    app = QtWidgets.QApplication(['feedio-smoke'])
    window = MainWindow()
    assert not QtGui.QPixmap(':/images/feedIO.png').isNull()
    result = []
    def loaded(ok):
        if ok:
            window.ui.viewArticle.page().toPlainText(lambda text: finish(text))
    def finish(text):
        result.append('Welcome to feedIO' in text)
        QtCore.QTimer.singleShot(0, stop)
    def stop():
        window.quit_app()
        app.quit()
    window.ui.viewArticle.loadFinished.connect(loaded)
    window.show()
    QtCore.QTimer.singleShot(15000, app.quit)
    app.exec()
    window.runner.shutdown()
    window.deleteLater()
    app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    models.close()
    assert result and all(result), 'WebEngine did not render the local page'
    print('Actual WebEngine rendering and clean shutdown passed')
