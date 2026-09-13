# Architecture

`feedIO.main` selects the profile, configures bounded logs and initializes the
schema before loading Qt. `ui.MainWindow` owns GUI state and explicit action
bindings; Designer sources and generated modules own layout only.

`workers.TaskRunner` serializes refresh/ranking in one worker, sends value results
back by Qt signals and removes the worker's scoped SQLAlchemy session. ORM
instances stay in the thread that owns their session. Quit requests cancellation and
waits for the active bounded operation to finish before disposing GUI resources.

`network` streams HTTP with time/size/redirect bounds and conditional validators.
It retries transient transport/5xx failures at most once after a cancellable
half-second delay within the same request budget; other HTTP failures are surfaced.
`feedmanager` normalizes RSS/Atom into feed-scoped durable identities and commits
entries and validators together. Redirects change URLs, not feed IDs. Refresh
errors do not delete saved articles. Parsing uses the final feed URL to resolve
relative article and body links. `reader` sanitizes HTML and independently
blocks WebEngine network/file requests and downloads. Its registered `feedio`
scheme serves only the current article from memory, avoiding the 2 MB data-URL
limit without temporary article files. The scheme is registered before
QApplication creation. The handler retains request buffers for Qt callbacks.

`models` defines the versioned SQLite schema and foreign-key enforcement.
`migration` snapshots databases and converts recognized legacy tables into a
temporary database before replacement. `portability` imports/exports OPML.
`settings` stores validated JSON preferences in SQLite.

Votes are durable, topic-local training examples with content snapshots, not
executable model files. `classifier` builds a bounded deterministic model from
the most recent 2,000 votes with up to 256 tokens/document and 20,000 vocabulary
terms. `prioritizer` computes scores in a transaction; cancellation rolls it back.
Voting is idempotent for each topic/article pair. Reset removes only that topic's
training. `speechengine` isolates optional native speech in a cancellable child.
The status-bar Cancel button signals cooperative worker cancellation. Closing
ages new items in one database update; a failed commit rolls back and leaves
the window open with a recovery message.

Startup works offline. Feed retrieval is the only reader operation that accesses
the network; article rendering uses stored, sanitized content. Profiles contain
SQLite data rather than executable classifier models.
