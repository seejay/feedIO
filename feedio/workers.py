"""One managed background queue; results contain values, never live ORM objects."""
from concurrent.futures import ThreadPoolExecutor
import logging
import threading
from PyQt6.QtCore import QObject, pyqtSignal
from . import models
from .network import FetchError


class TaskRunner(QObject):
    succeeded = pyqtSignal(object)
    failed = pyqtSignal(str)
    busyChanged = pyqtSignal(bool)
    completed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='feedio')
        self.busy = False
        self.cancel = threading.Event()
        self.completed.connect(self._finish)

    def submit(self, function, *args):
        if self.busy:
            return False
        self.busy = True
        self.cancel.clear()
        self.busyChanged.emit(True)
        def execute():
            try:
                value = function(*args, cancel=self.cancel)
                outcome = (True, value)
            except Exception as error:
                logging.error('Background operation failed: %s', type(error).__name__)
                message = str(error) if isinstance(error, (ValueError, FetchError)) else 'Operation failed. Your saved data is retained.'
                outcome = (False, message)
            finally:
                models.session.remove()
            self.completed.emit(outcome)
        self.pool.submit(execute)
        return True

    def _finish(self, outcome):
        self.busy = False
        self.busyChanged.emit(False)
        if outcome[0]:
            self.succeeded.emit(outcome[1])
        else:
            self.failed.emit(outcome[1])

    def shutdown(self):
        self.cancel.set()
        if not self.busy:
            self.pool.shutdown(wait=False, cancel_futures=True)
