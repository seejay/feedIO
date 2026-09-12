"""Optional speech runs in an isolated child process with explicit cancellation."""
import json
import subprocess
import sys
import threading


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
        self.process = subprocess.Popen(command + ['--speech-worker'], stdin=subprocess.PIPE,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                        text=True, encoding='utf-8')
        process = self.process
        payload = json.dumps({'text': text[:50000], 'rate': self.speed, 'voice': self.voice})
        def communicate():
            try:
                _, error = process.communicate(payload)
                if process.returncode and not self._stopping:
                    self.error = 'Speech unavailable. Install feedio[speech] and a native speech backend; check your voice setting.'
            except Exception:
                if not self._stopping:
                    self.error = 'Speech playback failed.'
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


def run_worker():
    try:
        import pyttsx3
        values = json.loads(sys.stdin.read(250000))
        engine = pyttsx3.init()
        engine.setProperty('rate', int(values['rate']))
        if values.get('voice'):
            engine.setProperty('voice', values['voice'])
        engine.say(values['text'])
        engine.runAndWait()
        return 0
    except Exception:
        print('Speech backend unavailable', file=sys.stderr)
        return 1
