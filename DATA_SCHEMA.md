# Data schema

SQLite database: `data/foundation.sqlite3`. Applied migrations: 001 and 002.

16 tables. Original SQL and trigger definitions are in `qfoundation/migrations/`.

| Table | Role |
|---|---|
| `partitions` | RESEARCH / VALIDATION / FINAL_OOS partition definitions. |
| `candidates` | One immutable chain+mint identity and partition membership. |
| `candidate_discoveries` | Many discovery events per candidate, source/event key and event/ingestion clocks. |
| `raw_api_snapshots` | Original BLOB payload, metadata, SHA-256, HTTP status and provenance; source of truth. |
| `market_observations` | Versioned market observation JSON derived from one replay; real-provider mappings unconfirmed. |
| `filter_results` | Shadow PASS/FAIL/SKIP/UNCONFIRMED and CONTINUE tracking, linked to replay. |
| `social_observations` | Versioned social observation JSON derived from one replay; real-provider mappings unconfirmed. |
| `decisions` | Research-only PASS/SKIP, never trading; tracking always CONTINUE. |
| `forward_observations` | Append-only plans/recorded/missing events for seven horizons, both PASS and SKIP. |
| `api_events` | Transport/provider event history and explicit error taxonomy, independent of payload availability. |
| `config_versions` | Immutable named config versions with canonical JSON and content hash. |
| `pipeline_versions` | Immutable parser/filter/foundation/runtime manifest and hash. |
| `parser_versions` | Provider/name/version, code hash and schema confirmation status. |
| `replay_runs` | Raw → parser/config/pipeline lineage and status; unique version tuple. |
| `idempotency_keys` | Scope+key to request hash/result id; different input on same key is rejected. |
| `schema_migrations` | Applied ordered SQL filenames/checksums/timestamps. |

## Constraints and relationships

Every candidate-scoped evidence/observation row carries partition_id. Composite foreign keys prevent cross-candidate/partition lineage. Raw snapshots reference candidates; replay references raw plus immutable versions; observations and filters reference replay; decisions reference filters; forwards reference decisions and optional raw evidence. API events may be global in a partition; linked snapshots must match provider/candidate/partition.

All tables are append-only after migration 002. There is no DELETE cascade. Candidate identity is UNIQUE(chain,mint), discovery identity is UNIQUE(candidate_id,source,event_key), replay identity is UNIQUE(snapshot_id,parser_version_id,config_version_id,pipeline_version_id). Each replay has at most one market object, social object, filter result and decision; arrays/multiple pools can reside in JSON until confirmed typed schema is designed.

Forward identity is UNIQUE(decision_id,horizon_seconds,event_key). Planning uses event_key=plan. Recording appends with a distinct stable key. Allowed horizons: 600/1800/3600/10800/21600/43200/86400 seconds. SQL triggers validate decision-relative due times, no early observations and forward snapshot time interval.

Canonical timestamps ending `_us` are INTEGER UTC Unix microseconds. Raw payload is BLOB; JSON documents are TEXT guarded with json_valid. UUID text is used for entity ids; partition ids are the three explicit enum names. CHECK constraints and triggers are authoritative in the SQL files.

## partitions

RESEARCH / VALIDATION / FINAL_OOS partition definitions.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `description` | TEXT | True | 0 |

## candidates

One immutable chain+mint identity and partition membership.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `chain` | TEXT | True | 0 |
| `mint` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## candidate_discoveries

Many discovery events per candidate, source/event key and event/ingestion clocks.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `source` | TEXT | True | 0 |
| `event_key` | TEXT | True | 0 |
| `occurred_at_us` | INTEGER | True | 0 |
| `ingested_at_us` | INTEGER | True | 0 |
| `metadata_json` | TEXT | True | 0 |
| `request_sha256` | TEXT | True | 0 |

## raw_api_snapshots

Original BLOB payload, metadata, SHA-256, HTTP status and provenance; source of truth.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `provider` | TEXT | True | 0 |
| `endpoint` | TEXT | True | 0 |
| `captured_at_us` | INTEGER | True | 0 |
| `ingested_at_us` | INTEGER | True | 0 |
| `http_status` | INTEGER | False | 0 |
| `provenance` | TEXT | True | 0 |
| `content_type` | TEXT | True | 0 |
| `payload` | BLOB | True | 0 |
| `payload_sha256` | TEXT | True | 0 |
| `byte_length` | INTEGER | True | 0 |
| `metadata_json` | TEXT | True | 0 |

## market_observations

Versioned market observation JSON derived from one replay; real-provider mappings unconfirmed.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `replay_run_id` | TEXT | True | 0 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `observed_at_us` | INTEGER | True | 0 |
| `mapping_status` | TEXT | True | 0 |
| `data_json` | TEXT | True | 0 |

## filter_results

Shadow PASS/FAIL/SKIP/UNCONFIRMED and CONTINUE tracking, linked to replay.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `replay_run_id` | TEXT | True | 0 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `outcome` | TEXT | True | 0 |
| `mode` | TEXT | True | 0 |
| `research_tracking` | TEXT | True | 0 |
| `details_json` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## social_observations

Versioned social observation JSON derived from one replay; real-provider mappings unconfirmed.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `replay_run_id` | TEXT | True | 0 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `observed_at_us` | INTEGER | True | 0 |
| `mapping_status` | TEXT | True | 0 |
| `data_json` | TEXT | True | 0 |

## decisions

Research-only PASS/SKIP, never trading; tracking always CONTINUE.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `filter_result_id` | TEXT | True | 0 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `outcome` | TEXT | True | 0 |
| `kind` | TEXT | True | 0 |
| `research_tracking` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## forward_observations

Append-only plans/recorded/missing events for seven horizons, both PASS and SKIP.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `decision_id` | TEXT | True | 0 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `horizon_seconds` | INTEGER | True | 0 |
| `due_at_us` | INTEGER | True | 0 |
| `recorded_at_us` | INTEGER | False | 0 |
| `state` | TEXT | True | 0 |
| `snapshot_id` | TEXT | False | 0 |
| `data_json` | TEXT | True | 0 |
| `event_key` | TEXT | True | 0 |
| `request_sha256` | TEXT | True | 0 |

## api_events

Transport/provider event history and explicit error taxonomy, independent of payload availability.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `candidate_id` | TEXT | False | 0 |
| `partition_id` | TEXT | True | 0 |
| `provider` | TEXT | True | 0 |
| `snapshot_id` | TEXT | False | 0 |
| `occurred_at_us` | INTEGER | True | 0 |
| `http_status` | INTEGER | False | 0 |
| `error_code` | TEXT | True | 0 |
| `retryable` | INTEGER | True | 0 |
| `details_json` | TEXT | True | 0 |

## config_versions

Immutable named config versions with canonical JSON and content hash.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `name` | TEXT | True | 0 |
| `version` | TEXT | True | 0 |
| `content_json` | TEXT | True | 0 |
| `content_sha256` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## pipeline_versions

Immutable parser/filter/foundation/runtime manifest and hash.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `name` | TEXT | True | 0 |
| `version` | TEXT | True | 0 |
| `parser_version_id` | TEXT | True | 0 |
| `manifest_json` | TEXT | True | 0 |
| `content_sha256` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## parser_versions

Provider/name/version, code hash and schema confirmation status.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `provider` | TEXT | True | 0 |
| `name` | TEXT | True | 0 |
| `version` | TEXT | True | 0 |
| `code_sha256` | TEXT | True | 0 |
| `schema_status` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## replay_runs

Raw → parser/config/pipeline lineage and status; unique version tuple.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `id` | TEXT | False | 1 |
| `snapshot_id` | TEXT | True | 0 |
| `candidate_id` | TEXT | True | 0 |
| `partition_id` | TEXT | True | 0 |
| `parser_version_id` | TEXT | True | 0 |
| `config_version_id` | TEXT | True | 0 |
| `pipeline_version_id` | TEXT | True | 0 |
| `started_at_us` | INTEGER | True | 0 |
| `status` | TEXT | True | 0 |
| `details_json` | TEXT | True | 0 |

## idempotency_keys

Scope+key to request hash/result id; different input on same key is rejected.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `scope` | TEXT | True | 1 |
| `key` | TEXT | True | 2 |
| `request_sha256` | TEXT | True | 0 |
| `result_id` | TEXT | True | 0 |
| `created_at_us` | INTEGER | True | 0 |

## schema_migrations

Applied ordered SQL filenames/checksums/timestamps.

| Column | SQLite type | NOT NULL | PK |
|---|---|---|---|
| `version` | INTEGER | False | 1 |
| `filename` | TEXT | True | 0 |
| `sha256` | TEXT | True | 0 |
| `applied_at_us` | INTEGER | True | 0 |

## API error taxonomy

NONE, DNS, CONNECT, TIMEOUT, TLS, AUTH, RATE_LIMIT, BAD_REQUEST, NOT_FOUND, NO_ROUTE, SERVER, HTTP_OTHER, PARSE_ERROR, SCHEMA_CHANGED, UNCONFIRMED, UNKNOWN.

HTTP failures remain distinct from route availability. Transport errors have explicit categories; retryable is advisory metadata and does not start a retry. NO_ROUTE is accepted only as an explicit future confirmed-adapter observation; no current adapter maps it.

## Phase 2A.5: no DDL change

The existing 16 tables/two migrations remain byte-for-byte unchanged. No protocol or
ledger table is claimed to exist. Future backward-compatible additions are described
in EXPERIMENT_LEDGER_SCHEMA.md: explicit anchors, source/cohort versions, availability
clocks, pool selection events, capture attempts/quality annotations, outcome events,
protocol/strategy/dataset/experiment ledgers and partition access audit.

Current observed_at_us is a capture proxy, not provider event time. Current forward
rows anchor to decisions, not discovery/baseline/eligibility. Current candidate
RESEARCH default must not become a future implicit collector partition assignment.
The source registry/split/activation manifest must supply explicit assignment.
The required missing-state taxonomy belongs to future typed annotations; it must not
be confused with existing transport error_code or filter outcome enumerations.
