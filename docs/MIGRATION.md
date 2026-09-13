# Profiles, migration and recovery

Before upgrading, close every feedIO instance and copy your entire old profile
directory somewhere safe. Use a copy for migration testing.
The modern default directory comes from `platformdirs`; start with `--profile`
to choose an explicit location. The old `~/.feedIO/feedIO.sqlite` is detected but
not imported automatically.

Start an empty modern profile and choose Feeds → Import / restore profile.
Select the old SQLite database or a modern profile backup. Import refuses a
populated target. A snapshot of the target is retained beside its database as
`.before-import-*.bak`. The source is read-only. Legacy conversion uses a temporary
database and preserves a `.pre-v1-*.bak` snapshot before schema replacement.
Conversion leaves the source unchanged. Keep all backups
until you have compared subscription counts, articles, topics and reading flags.

Schema 2 also upgrades development schema 1 through a `.pre-v2-*.bak` snapshot
and temporary rebuild. It prevents IDs being reused after deletion, including
IDs referenced by retained votes. Startup rejects incomplete current schemas
and broken foreign keys; it does not silently create missing tables over them.
The application holds a profile lock so two instances cannot write one profile.

Recognized legacy schemas use feed/topic/item and score tables, including
`models_` prefixes. Ambiguous tables, missing article feeds, corrupt databases
and future schema versions fail safely rather than guessing. Historical profile
variants not represented by fixtures still require testing on a copy.

Feed URLs, topic names, articles and reading/bookmark flags are converted.
Legacy CRM/pickle model files remain untouched and are never deserialized;
retrain by voting. Modern votes/preferences travel in SQLite backups. OPML
contains subscriptions only, not topic assignments, reading history or training.

Use Feeds → Back up profile with a new filename for a consistent SQLite snapshot.
To restore, start another empty `--profile` directory and import that snapshot.
If startup fails, retain the database, backups and bounded `feedio.log`, then
diagnose using copies, keeping the original profile intact.
Logs intentionally omit article bodies, URL credentials and raw SQL exceptions.
