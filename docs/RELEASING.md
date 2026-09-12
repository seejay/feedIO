# Build and release procedure

Build from a clean checkout in a fresh virtual environment. Install `.[dev]`,
run tests/lint, regenerate Designer Python with `scripts/generate_ui.py`, and
check there is no generated diff. Embedded `feedIOicons_rc.py` carries the Qt
resource bytes; its registration is tested by the real WebEngine smoke check.
Designer `.ui`, `.qrc` and PNG sources ship in the wheel for future regeneration.

`python -m build` creates source and wheel distributions. Install the wheel into
a separate environment, leave the checkout directory, and run
`python -m feedio --profile <new-directory> --check` and a real desktop launch.
Check that icons, packaged license/authors and WebEngine subprocesses are present.

`python scripts/build_desktop.py` builds a PyInstaller one-directory bundle under
`dist/desktop`. Build on each target OS/architecture; bundles are not cross-built.
Keep the complete directory, not only its executable. macOS produces an app
bundle; Windows uses a windowed executable. Speech is intentionally excluded
from default bundles. WebEngine's sandbox remains enabled in packaged builds.
CI uploads development artifacts for testing.

Before a stable release, complete the remaining [platform checks](TESTING.md#platform-status),
select a version in `feedio/__init__.py`, update CHANGELOG.md and rebuild from that revision.
Generate checksums, include the source, license and dependency notices, and sign
Windows and macOS artifacts. macOS distribution also needs notarization.
Release notes should list tested operating systems, architectures and known
limitations. Unsigned bundles are suitable for development testing.
