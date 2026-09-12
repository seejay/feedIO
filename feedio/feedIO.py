"""Application entry point; profile selection precedes database or UI initialization."""
import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description='feedIO desktop reader')
    parser.add_argument('--profile', help='Use a separate profile directory')
    parser.add_argument('--check', action='store_true', help='Initialize and check the profile without opening a window')
    parser.add_argument('--speech-worker', metavar='PAYLOAD', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.speech_worker:
        from feedio.speechengine import run_worker
        return run_worker(args.speech_worker)
    from feedio import config, models, classifier
    if args.profile:
        config.USER_DIR = str(Path(args.profile).expanduser().resolve())
        config.DB_FILE = str(Path(config.USER_DIR) / 'feedIO.sqlite')
        config.CLASSIFIER_DIR = str(Path(config.USER_DIR) / 'classifier')
    config.ensure_dirs()
    handler = RotatingFileHandler(Path(config.USER_DIR) / 'feedio.log', maxBytes=1_000_000, backupCount=2, encoding='utf-8')
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    try:
        models.initDB()
        classifier.initTopics()
        if args.check:
            models.close()
            return 0
        from feedio.ui import initUI
        return initUI()
    except Exception as error:
        logging.error('Startup failed (%s)', type(error).__name__)
        print('feedIO could not start: ' + str(error))
        models.close()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
