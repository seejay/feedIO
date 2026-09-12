# Testing

Install the development dependencies with `python -m pip install -e '.[dev]'`.

```sh
python -m pytest -q
python -m ruff check .
```

On headless Linux, set these variables before running Qt tests:

```sh
export QT_QPA_PLATFORM=offscreen
export QT_QPA_PLATFORMTHEME=generic
```

Tests use disposable profiles and block outbound HTTP. They cover SQLite
persistence, feed parsing, topic voting and Qt widgets. Most UI tests replace
WebEngine with a lightweight view.

## Desktop checks

`python scripts/smoke_desktop.py` renders real WebEngine content and checks
embedded icons and shutdown. `scripts/benchmark_ranking.py` measures bounded
model construction; it does not measure full desktop responsiveness.

See [releasing](RELEASING.md) for wheel and desktop bundle checks.

## Platform status

Linux, Windows and macOS are development targets. CI is configured for Python
3.10, 3.12 and 3.14 on those operating systems; platform support depends on
successful automated and desktop checks on each target.

Before a stable release, test navigation, focus, DPI, tray behavior, graphics,
clipboard and browser integration on real desktops. Native speech and
notifications need testing with the operating system's backends and permissions.
Migration testing should include copies of representative legacy profiles and
recovery from backups. Large libraries, long articles, slow feeds and sleep/wake
use need extended desktop runs. Built bundles also need clean target machines
and platform signing checks.
