"""Regenerate Designer bindings, converting legacy font weights in memory."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
for source in sorted((root / 'feedio/UI').glob('*.ui')):
    xml = source.read_text()
    xml = re.sub(r'<weight>75</weight>', '<weight>700</weight>', xml)
    xml = re.sub(r'<weight>50</weight>', '<weight>400</weight>', xml)
    xml = xml.replace('http://www.feedio.org/', 'about:blank')
    with tempfile.TemporaryDirectory() as directory:
        temporary = Path(directory) / source.name
        temporary.write_text(xml)
        result = subprocess.run([sys.executable, '-m', 'PyQt6.uic.pyuic', str(temporary)],
                                check=True, capture_output=True, text=True)
    code = result.stdout.replace(str(temporary), source.name)
    source.with_name(source.stem + '_ui.py').write_text(code)
