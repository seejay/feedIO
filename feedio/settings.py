"""Validated settings live inside the profile database and its backups."""
from dataclasses import dataclass, asdict
import json
from .models import session, Setting


@dataclass
class Preferences:
    refresh_minutes: int = 30
    notifications: bool = True
    close_to_tray: bool = False
    speech_rate: int = 180
    speech_voice: str = ''

    def validate(self):
        if type(self.refresh_minutes) is not int or not 1 <= self.refresh_minutes <= 1440:
            raise ValueError('Refresh interval must be 1–1440 minutes')
        if type(self.speech_rate) is not int or not 80 <= self.speech_rate <= 400:
            raise ValueError('Speech rate must be 80–400 words per minute')
        if type(self.notifications) is not bool or type(self.close_to_tray) is not bool:
            raise ValueError('Notification and tray preferences must be boolean')
        if not isinstance(self.speech_voice, str) or len(self.speech_voice) > 500:
            raise ValueError('Invalid speech voice identifier')


def load():
    row = session.get(Setting, 'preferences')
    if row:
        try:
            preferences = Preferences(**json.loads(row.value))
            preferences.validate()
            return preferences
        except (TypeError, ValueError):
            pass
    return Preferences()


def save(preferences):
    preferences.validate()
    row = session.get(Setting, 'preferences') or Setting(key='preferences')
    row.value = json.dumps(asdict(preferences))
    session.add(row)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
