# Q — Phase 2A data foundation

**Phase 0 COMPLETE · Phase 1 LIVE_VALIDATION_PENDING · Phase 2A COMPLETE · Phase 2B NOT STARTED**

Offline Python/SQLite project. No external runtime dependencies, network client,
provider fetch, wallet, transaction, scanner, scheduler or trading implementation.
Python 3.10+ and SQLite JSON1 support are required. Use from the extracted project
root; installation is optional and not required.

The included `data/foundation.sqlite3` is an initialized empty database with three
partition rows and two applied migrations. All sample data lives in temporary test
databases, not this file.

Commands for a later developer session (not a request to run them now):

```bash
python -m unittest discover -s tests -v
python -m qfoundation init --db data/foundation.sqlite3
python -m qfoundation inspect --db data/foundation.sqlite3
```

`init` applies missing migrations transactionally. Repeating it is safe. `inspect`
also opens through Store and validates/applies known migrations; do not use it as a
read-only forensic command on an unknown database. For forensic reads use SQLite
read-only mode on a backup. Existing migration checksums cannot be changed.

Public entry points:

- `Store`: candidate identity, discoveries, snapshot capture from **supplied bytes**,
  immutable versions, API error events, forward plans/events and online backup.
- `ParserRegistry`: exact parser version to offline implementation binding.
- `ReplayEngine.run`: stored bytes → registered parser → immutable config → shadow
  filter → research decision. No API fallback.
- `RugCheckAdapter`, `DexScreenerAdapter`, `JupiterAdapter`, `XAIAdapter`: all return
  UNCONFIRMED with no normalized observations until Phase 1 mappings are approved.

Read `PHASE2A_COMPLETION_REPORT.md` for the requested 20-item completion report,
`ARCHITECTURE.md` for invariants, `DATA_SCHEMA.md` for every table/column,
`DECISIONS.md` for design choices and risks, and `HANDOFF.md` before continuing.

The archived Phase 1 validator is historical and was copied without execution.
Its old instruction to stop all Phase 2 work is superseded by this project's current
status and the user's explicit Phase 2A authorization. Phase 1 remains pending.
