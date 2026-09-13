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

Tests use temporary profiles and block outbound HTTP. Network integration tests
run a loopback HTTP server to exercise redirects, conditional refresh, retries,
truncated responses, size limits and cancellation. SQLite tests cover reading
state, topic voting, schema upgrades, profile locking and backup recovery.

## Desktop checks

Most UI unit tests replace WebEngine with a lightweight widget. A separate smoke
test renders real browser content and checks embedded icons and shutdown:

```sh
python scripts/smoke_desktop.py
```

The longer workflow uses 1,500 temporary articles, including a 2.4 MB article. It
exercises navigation, read state, bookmarks, voting, ranking, cancellation,
preferences, clipboard operations, backup and restoration:

```sh
python scripts/accept_desktop.py --software-rendering --output build/desktop-acceptance.json
```

Use `--platform wayland` or `--platform xcb` on the corresponding Linux desktop.
Omit `--software-rendering` to test GPU acceleration. The XCB backend on a Wayland
desktop exercises XWayland; native X11 needs a separate desktop session.
`--cycles 100` extends the repeated workflow. Reports record platform and runtime
versions, timings and completed checks.

`scripts/benchmark_library.py` measures database operations with a large library;
`scripts/benchmark_ranking.py` measures model construction. These are diagnostic
tools, with timings that depend on the machine and workload.

See [releasing](RELEASING.md) for installed wheel and native bundle checks.

## Platform status

The development version has been tested on Linux ARM64 with Python 3.10 and 3.14.
The regression suite, software-rendered browser checks, Wayland and XWayland
workflows, installed wheel and native development bundle have passed there.
CI is configured for Linux, Windows and macOS with Python 3.10, 3.12 and 3.14;
Windows and macOS results have not yet been verified.

An offscreen WebEngine shutdown crash has been observed with GPU acceleration on
Linux ARM64. Software rendering avoids it in the tested configuration. Wayland
and XWayland workflows passed with default graphics settings, although Wayland
emitted Chromium graphics diagnostics. Other GPUs and desktop configurations
still need testing.

Before a stable release, remaining checks include native X11, Windows and macOS
desktops; DPI, focus and accessibility; native speech and notifications; browser
integration; representative legacy profile copies; prolonged refresh and
sleep/wake use; and signed bundles on clean target machines. Synthetic migration
fixtures and short desktop runs cover only part of this behavior.

HTTP operations use a checked 30-second budget, 5/10-second connect/read timeouts,
six redirect hops, one transient retry and a 5 MB decoded-body limit. Cancellation
is cooperative between reads. DNS and socket stalls can exceed the checked
budget, so these limits are not hard real-time guarantees.
