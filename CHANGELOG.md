# Changelog

## 2.0.0.dev0 (unreleased)

- Modern Python/Qt packaging and offline, resource-complete startup.
- Versioned SQLite profiles, stable identities, backed-up legacy import and OPML.
- Bounded RSS/Atom retrieval, conditional refresh and durable reading state.
- Managed background work, secure offline reader and restored desktop actions.
- Durable topic-local learning without CRM, downloaded corpora or pickle files.
- Persisted preferences, local bookmarks and isolated optional speech.
- Retired Pocket/Twitter account integrations and deferred translation.
- Regression tests, target-platform CI and development distribution tooling.
- Profile locking, stricter schema validation, non-reused identities and full-library pagination.
- Close SQLite handles before profile upgrades and restores replace database files.
- Resolve relative article links against the downloaded feed's final URL.
- Display long articles through an offline in-memory document handler without the
  former 2 MB browser limit.
- Cancel background work from the status bar; retain a usable window if saving
  reading state during close fails.
- Real loopback HTTP regression tests and repeatable desktop acceptance reports.
- Give the article reader more space in the initial window layout.

See [platform status](docs/TESTING.md#platform-status) for testing coverage and
known limitations.
