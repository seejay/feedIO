"""Optional speech: no native backend is initialized during startup."""
import threading


class SpeechUnavailable(RuntimeError):
    pass


class SpeechEngine:
    def __init__(self, pitch=None, speed=200):
        self.speed = int(speed)
        self.engine = None
        self._worker = None
        self.error = None

    def say(self, text):
        if self.playing:
            raise SpeechUnavailable("Speech is already playing. Stop it before starting again.")
        self.error = None
        def speak():
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', self.speed)
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                self.error = 'Speech unavailable. Install feedio[speech] and a native speech backend.'
            finally:
                self.engine = None
        self._worker = threading.Thread(target=speak, daemon=True)
        self._worker.start()

    def stop(self):
        if self.engine:
            self.engine.stop()

    @property
    def playing(self):
        return bool(self._worker and self._worker.is_alive())
