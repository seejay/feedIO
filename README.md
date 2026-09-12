# feedIO

A desktop RSS/Atom reader with offline reading, topic-specific voting and learned
ranking. Version 2.0 is under development.

## Run from source

Requires Python 3.10–3.14 and a desktop capable of running Qt 6 WebEngine.
See [platform status](docs/TESTING.md#platform-status) for tested configurations
and known limitations. Create and activate a virtual environment:

```sh
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
python -m feedio
```

`feedio` is also installed as a desktop entry command. Use
`python -m feedio --profile /path/to/new-profile --check` to initialize an isolated
profile without opening a window; omit `--check` to use it interactively.
Each running instance needs its own profile. The default profile uses the OS
user-data directory (`platformdirs`); `FEEDIO_PROFILE` overrides it.

## Everyday use

Add an RSS/Atom or website URL from Feeds, or import OPML, then refresh. Selecting
an article marks it read. Votes train only the selected interest. Bookmarks are
local and included in profile backups. Article HTML is sanitized; scripts and
remote resources are blocked. Original links open in your system browser.
Preferences control periodic refresh, notifications, close-to-tray and speech.
Closing exits by default; tray behavior depends on desktop support.

Speech is optional: `python -m pip install '.[speech]'`. It also requires an OS
speech backend (for example eSpeak on Linux). Reading works without a speech
backend. Speech is not included in the default desktop bundle.
Pocket and authenticated Twitter integrations have been removed. Translation
is currently unavailable.

Existing users: read [migration and recovery](docs/MIGRATION.md) before importing
your profile. Old CRM/pickle training files are never executed or loaded.

## Development and distribution

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check .
python scripts/generate_ui.py
python -m build
python scripts/build_desktop.py
```

See the [contribution guide](CONTRIBUTING.md), [test commands](docs/TESTING.md),
[architecture](docs/ARCHITECTURE.md), and [build instructions](docs/RELEASING.md).
GPL-3.0-or-later; see [license](LICENSE.txt) and [authors](AUTHORS.txt).
