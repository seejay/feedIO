"""Optional speech runs in an isolated child process with explicit cancellation."""
import json
import subprocess
import sys
import threading
import tempfile
from pathlib import Path


class SpeechUnavailable(RuntimeError):
    pass


class SpeechEngine:
    def __init__(self, pitch=None, speed=180, voice=''):
        self.speed = int(speed)
        self.voice = voice
        self.process = None
        self._worker = None
        self.error = None
        self._stopping = False

    @property
    def engine(self):
        return None  # Native engines are deliberately never created in the GUI process.

    @property
    def playing(self):
        return bool(self._worker and self._worker.is_alive())

    def say(self, text):
        if self.playing:
            raise SpeechUnavailable('Speech is already playing. Stop it before starting again.')
        self.error = None
        self._stopping = False
        command = ([sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, '-m', 'feedio'])
        payload = json.dumps({'text': text[:50000], 'rate': self.speed, 'voice': self.voice})
        # Windowed frozen applications have no sys.stdin, even with pipe redirection.
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.json',
                                         prefix='feedio-speech-', delete=False) as handle:
            handle.write(payload)
            payload_path = Path(handle.name)
        try:
            self.process = subprocess.Popen(command + ['--speech-worker', str(payload_path)],
                                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
        except Exception:
            payload_path.unlink(missing_ok=True)
            raise SpeechUnavailable('Could not start the speech worker.') from None
        process = self.process
        def communicate():
            try:
                process.wait()
                if process.returncode and not self._stopping:
                    self.error = 'Speech unavailable. Install feedio[speech] and a native speech backend; check your voice setting.'
            except Exception:
                if not self._stopping:
                    self.error = 'Speech playback failed.'
            finally:
                payload_path.unlink(missing_ok=True)
        self._worker = threading.Thread(target=communicate, daemon=True)
        self._worker.start()

    def stop(self):
        self._stopping = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=1)


def run_worker(payload_path):
    try:
        path = Path(payload_path)
        if path.stat().st_size > 1_000_000:
            return 1
        values = json.loads(path.read_text(encoding='utf-8'))
        path.unlink()  # Minimize the lifetime of article text on disk.
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', int(values['rate']))
        if values.get('voice'):
            engine.setProperty('voice', values['voice'])
        engine.say(values['text'])
        engine.runAndWait()
        return 0
    except Exception:
        return 1
