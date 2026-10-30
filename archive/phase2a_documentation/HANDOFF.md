# Handoff — Phase 2A complete, stop here

## Authoritative current status

PHASE 0 = COMPLETE
PHASE 1 = LIVE_VALIDATION_PENDING
PHASE 2A = COMPLETE
PHASE 2B = NOT STARTED

The latest user explicitly authorized Phase 2A without waiting for Phase 1. Do not
reinterpret Phase 1 pending as a reason to undo or block this completed infrastructure.
Do not execute the archived Phase 1 validator or ask the user to use a PC now.

## What exists

Offline Python package, two SQLite migrations, 16 tables, 41 passing tests, initialized
empty database, versioned replay and required project documentation. No API mappings,
network clients, token scanners, live tracking, thresholds/strategy optimization,
paper PNL optimization, Grok trading decisions, wallets or transactions. No agents.

`reports/test_results.txt` is the executed test log. All payloads used in tests were
synthetic, including public mint identifiers; no API request was made. Provider
adapter outputs remain UNCONFIRMED. The database contains only partition seeds and
migration history; tests use temporary independent databases.

## After Phase 1 is completed later

1. Preserve actual live captures and their HTTP status, endpoint, capture time and
   provenance. Import original bytes; do not reserialize normalized JSON as raw.
2. Review schema requirements/nullability/units/error semantics using actual fixtures.
3. Create versioned confirmed provider parsers with contract tests. Deliberately revise
   the current registration/replay gate only after mapping approval; no silent fallback.
4. Pin config, parser, filter and runtime fingerprints. Replay archived snapshots and
   compare versioned outputs without overwriting earlier runs.
5. Preserve Phase 1 pending status until that work is actually validated; this project
   did not complete or retry any Phase 1 live validation.

## Phase 2B proposed scope — not executed, approval required

Use this as a proposed next checklist, not a claim to have retrieved an unseen older
HANDOFF: connect only approved parsers, implement narrowly scoped ingestion orchestration
and rate/error handling, test observation quality/freshness, define forward scheduling
and missing/late-data rules, enforce partition/embargo protocol, and add integration
contract tests. Validate provenance and lineage across ingestion/replay. Collectors and
tracking require explicit authorized scope. No threshold/strategy/PNL optimization or
trading functionality is implied by Phase 2B approval.

## Developer continuity

Run tests from the project root. Any source/runtime change creates a new foundation
fingerprint, so create a new pipeline version; keep old source/runtime for exact replay.
Never edit already-applied migrations. Use a new numbered migration. Each worker gets
its own Store connection. Stable event/capture keys are the caller's responsibility.
Back up with Store.backup before migrations on a populated database.

STOP. Phase 2B must not begin without explicit user approval.
