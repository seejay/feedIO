"""All tests use disposable profiles; outbound HTTP is forbidden by default."""
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_PLATFORMTHEME", "generic")

import pytest
import requests
from feedio import config, models


@pytest.fixture(autouse=True)
def profile(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "USER_DIR", str(tmp_path))
    monkeypatch.setattr(config, "DB_FILE", str(tmp_path / "feedIO.sqlite"))
    monkeypatch.setattr(config, "CLASSIFIER_DIR", str(tmp_path / "classifier"))
    models.initDB(config.DB_FILE)
    yield Path(tmp_path)
    models.close()


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Tests must use local HTTP fixtures")
    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
