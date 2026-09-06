"""Repeatable local scoring benchmark; no personal profile is accessed."""
import sys
import time
import tempfile
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from feedio.classifier import PreferenceModel

votes = [SimpleNamespace(title='Python software development', body='Programming desktop applications',
                         value=1 if i % 2 else -1, item_key=f'{i % 20}:{i}') for i in range(2000)]
started = time.perf_counter()
model = PreferenceModel(votes)
article = SimpleNamespace(title='Python release', description='Desktop software programming', feed_id=1)
for i in range(10000):
    model.score(article)
elapsed = time.perf_counter() - started
print(f'2,000-vote model plus 10,000 articles: {elapsed:.3f}s')
assert elapsed < 15, 'Ranking exceeds the local 15-second batch budget'
