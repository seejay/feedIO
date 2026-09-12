import pytest
from feedio import settings, models as m
from feedio.preferences_ui import PreferencesDialog
from feedio.speechengine import SpeechEngine
from test_ui import app, window


def test_settings_roundtrip_and_validation():
    preferences = settings.Preferences(refresh_minutes=7, notifications=False, close_to_tray=True, speech_rate=220)
    settings.save(preferences)
    m.session.remove()
    assert settings.load() == preferences
    with pytest.raises(ValueError):
        settings.save(settings.Preferences(refresh_minutes=0))
    assert settings.load() == preferences


def test_cancel_does_not_save_and_accept_applies(window):
    dialog = PreferencesDialog(window)
    dialog.interval.setValue(9)
    dialog.reject()
    assert settings.load().refresh_minutes == 30
    dialog = PreferencesDialog(window)
    dialog.interval.setValue(9)
    dialog.save()
    window.apply_preferences()
    assert window.timer.interval() == 9 * 60 * 1000
    window.notifications(False)
    assert not settings.load().notifications


def test_speech_is_lazy_and_stop_is_safe():
    engine = SpeechEngine()
    assert engine.engine is None
    assert not engine.playing
    engine.stop()
