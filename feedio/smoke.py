"""Short actual-browser acceptance probe shared by source and frozen builds."""
def run():
    from feedio import models
    from feedio.ui import MainWindow
    from PyQt6 import QtWidgets, QtCore, QtGui
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(['feedio-smoke'])
    window = MainWindow()
    result = []

    def finish(text):
        result.append('Welcome to feedIO' in text)
        # Never destroy/stop the browser inside its own Chromium callback.
        QtCore.QTimer.singleShot(0, stop)

    def loaded(ok):
        if ok:
            window.ui.viewArticle.page().toPlainText(finish)

    def stop():
        window.quit_app()
        app.quit()

    window.ui.viewArticle.loadFinished.connect(loaded)
    window.show()
    QtCore.QTimer.singleShot(15000, stop)
    app.exec()
    valid = bool(result and all(result) and not QtGui.QPixmap(':/images/feedIO.png').isNull())
    window.runner.shutdown()
    window.deleteLater()
    app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    app.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    models.close()
    return 0 if valid else 1
