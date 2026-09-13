"""Actual WebEngine smoke test with a temporary profile and no remote content."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from feedio.feedIO import main

with tempfile.TemporaryDirectory(prefix='feedio-smoke-') as profile:
    result = main(['--profile', profile, '--smoke-test', '--software-rendering'])
    if result:
        raise SystemExit('WebEngine did not render the local page')
    print('Actual WebEngine rendering and clean shutdown passed (software rendering)')
