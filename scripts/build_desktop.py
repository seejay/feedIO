"""Build an unsigned native development bundle for local testing."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
           '--exclude-module', 'pyttsx3',
           '--name', 'feedio', '--collect-data', 'feedio',
           '--specpath', str(ROOT / 'build'), '--workpath', str(ROOT / 'build' / 'pyinstaller'),
           '--distpath', str(ROOT / 'dist' / 'desktop'), '--paths', str(ROOT)]
if sys.platform in ('win32', 'darwin'):
    command.append('--windowed')
command.append(str(ROOT / 'packaging' / 'launcher.py'))
subprocess.run(command, cwd=ROOT, check=True)
