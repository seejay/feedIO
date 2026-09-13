# Contributing

Create a virtual environment and install the development dependencies:

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
python -m ruff check .
```

The tests create disposable profiles. For manual testing, use
`python -m feedio --profile /path/to/test-profile` to keep your reading data
separate. See [testing](docs/TESTING.md) for headless Qt setup and desktop checks.

Edit Designer `.ui` sources and run `python scripts/generate_ui.py` for layout
changes. Application behavior belongs in controllers/services, not generated
files. Workers exchange plain values with the UI; database changes use
transactions. The [architecture](docs/ARCHITECTURE.md) and
[migration guide](docs/MIGRATION.md) describe these boundaries.

Include a focused test and a user-facing changelog entry for meaningful behavior
changes, and include the test commands and platforms used in the pull request.
Feed fixtures should be small, reproducible and free of private URLs or credentials.

## Reporting bugs

Include the feedIO, Python and Qt versions, operating system and architecture,
installation method, steps to reproduce, and expected and actual results. Check
whether the problem also occurs with a new profile. For graphics problems,
include the result with `--software-rendering` as well.

A minimal feed or OPML example helps with parsing bugs. Check logs and examples
for private URLs and article content before sharing them. Profiles and core
dumps can contain private reading data; keep them out of public issues.

## Dependency updates

Test dependency changes in a fresh environment with the supported Python and OS
matrix. Qt updates also need generated-source checks and installed wheel and
desktop bundle checks; see [releasing](docs/RELEASING.md).
