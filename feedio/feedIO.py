"""Application entry point; profile selection precedes database or UI initialization."""
import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description='feedIO desktop reader')
    parser.add_argument('--profile', help='Use a separate profile directory')
    parser.add_argument('--check', action='store_true', help='Initialize and check the profile without opening a window')
    parser.add_argument('--speech-worker', metavar='PAYLOAD', help=argparse.SUPPRESS)
    parser.add_argument('--software-rendering', action='store_true', help='Disable WebEngine GPU acceleration for graphics troubleshooting')
    parser.add_argument('--smoke-test', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.speech_worker:
        from feedio.speechengine import run_worker
        return run_worker(args.speech_worker)
    if args.software_rendering:
        os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = (os.environ.get('QTWEBENGINE_CHROMIUM_FLAGS', '') + ' --disable-gpu').strip()
    from feedio import config, models, classifier
    if args.profile:
        config.USER_DIR = str(Path(args.profile).expanduser().resolve())
        config.DB_FILE = str(Path(config.USER_DIR) / 'feedIO.sqlite')
        config.CLASSIFIER_DIR = str(Path(config.USER_DIR) / 'classifier')
    lock = None
    handler = None
    try:
        config.ensure_dirs()
        from PyQt6.QtCore import QLockFile
        lock = QLockFile(str(Path(config.USER_DIR) / 'feedio.lock'))
        if not lock.tryLock(0):
            raise ValueError('This profile is already open in another feedIO instance')
        handler = RotatingFileHandler(Path(config.USER_DIR) / 'feedio.log', maxBytes=1_000_000, backupCount=2, encoding='utf-8')
        logging.basicConfig(level=logging.INFO, handlers=[handler])
        models.initDB()
        classifier.initTopics()
        if args.check:
            models.close()
            return 0
        if args.smoke_test:
            from feedio.smoke import run
            return run()
        from feedio.ui import initUI
        return initUI()
    except Exception as error:
        logging.error('Startup failed (%s)', type(error).__name__)
        message = 'feedIO could not start. Close other instances using this profile and check its location, permissions and database version; your saved data has been retained.'
        if sys.stderr is not None:
            print(message, file=sys.stderr)
        if not args.check and not args.smoke_test:
            from PyQt6 import QtWidgets
            app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(['feedIO'])
            QtWidgets.QMessageBox.critical(None, 'Cannot start feedIO', message)
        models.close()
        return 1
    finally:
        if lock is not None:
            lock.unlock()
        if handler is not None:
            logging.getLogger().removeHandler(handler)
            handler.close()


if __name__ == '__main__':
    raise SystemExit(main())
