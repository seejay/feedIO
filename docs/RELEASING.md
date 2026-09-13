# Build and release procedure

Build from a clean checkout in a fresh virtual environment. Install `.[dev]`,
run the [tests](TESTING.md), regenerate Designer Python, and check for unexpected
generated changes:

```sh
python scripts/generate_ui.py
python scripts/generate_resources.py --rcc /path/to/Qt6/rcc
git diff --exit-code -- feedio/UI
```

Resource generation requires Qt 6 development tools and rebuilds
`feedIOicons_rc.py` from `.qrc` and PNG sources. It omits file
timestamps and compression to be reproducible. Its registration is tested by
the real WebEngine smoke check. All source assets ship in the wheel.

`python -m build` creates source and wheel distributions. Install the wheel into
a separate environment, leave the checkout directory, and run
`python -m feedio --profile <new-directory> --check` and a real desktop launch.
Check that icons, packaged license/authors and WebEngine subprocesses are present.
`python scripts/check_artifacts.py --wheel dist/<wheel-name>.whl` automates the
fresh environment, external working directory, Unicode profile and browser probe,
plus the longer workflow against the installed wheel via `--installed`.
Pass `--desktop <native-executable>` to check a complete local bundle as well.

The [desktop workflow](TESTING.md#desktop-checks) exercises reading and profile
operations with disposable data. CI retains its JSON report and pytest JUnit
results. Manual platform checks cover visual appearance, native speech,
notification delivery and external-browser integration.

`python scripts/build_desktop.py` builds a PyInstaller one-directory bundle under
`dist/desktop`. Build on each target OS/architecture; bundles are not cross-built.
Keep the complete directory, not only its executable. macOS produces an app
bundle; Windows uses a windowed executable. Speech is intentionally excluded
from default bundles. WebEngine's sandbox remains enabled in packaged builds.
CI uploads development artifacts for testing.

For the 2.0.0b1 beta, set the version in `feedio/__init__.py`, update CHANGELOG.md
and rebuild from that revision. Before a stable release, complete the remaining
[platform checks](TESTING.md#platform-status).
Generate checksums, attach source/license and dependency notices, sign Windows
and macOS artifacts, and notarize macOS using maintainer-managed credentials.
Release notes should list the tested operating systems and architectures and any
known limitations. Unsigned bundles are suitable for development testing.
