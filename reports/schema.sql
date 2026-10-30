CREATE INDEX discoveries_candidate_time ON candidate_discoveries(candidate_id,occurred_at_us);
CREATE INDEX errors_provider_time ON api_events(provider,occurred_at_us);
CREATE INDEX forwards_due ON forward_observations(partition_id,state,due_at_us);
CREATE INDEX replay_partition ON replay_runs(partition_id,started_at_us);
CREATE INDEX snapshots_candidate_time ON raw_api_snapshots(candidate_id,captured_at_us);
CREATE INDEX snapshots_payload_hash ON raw_api_snapshots(payload_sha256);
CREATE TABLE api_events (
 id TEXT PRIMARY KEY,
 candidate_id TEXT,
 partition_id TEXT NOT NULL REFERENCES partitions(id),
 provider TEXT NOT NULL,
 snapshot_id TEXT REFERENCES raw_api_snapshots(id),
 occurred_at_us INTEGER NOT NULL,
 http_status INTEGER CHECK(http_status BETWEEN 100 AND 599),
 error_code TEXT NOT NULL CHECK(error_code IN ('NONE','DNS','CONNECT','TIMEOUT','TLS','AUTH','RATE_LIMIT','BAD_REQUEST','NOT_FOUND','NO_ROUTE','SERVER','HTTP_OTHER','PARSE_ERROR','SCHEMA_CHANGED','UNCONFIRMED','UNKNOWN')),
 retryable INTEGER NOT NULL CHECK(retryable IN (0,1)),
 details_json TEXT NOT NULL CHECK(json_valid(details_json)),
 FOREIGN KEY(candidate_id,partition_id) REFERENCES candidates(id,partition_id)
);
CREATE TABLE candidate_discoveries (
 id TEXT PRIMARY KEY,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 source TEXT NOT NULL,
 event_key TEXT NOT NULL,
 occurred_at_us INTEGER NOT NULL CHECK(typeof(occurred_at_us)='integer'),
 ingested_at_us INTEGER NOT NULL CHECK(typeof(ingested_at_us)='integer'),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 request_sha256 TEXT NOT NULL CHECK(length(request_sha256)=64),
 UNIQUE(candidate_id,source,event_key),
 FOREIGN KEY(candidate_id,partition_id) REFERENCES candidates(id,partition_id)
);
CREATE TABLE candidates (
 id TEXT PRIMARY KEY,
 chain TEXT NOT NULL CHECK(chain='solana'),
 mint TEXT NOT NULL COLLATE BINARY,
 partition_id TEXT NOT NULL REFERENCES partitions(id),
 created_at_us INTEGER NOT NULL CHECK(typeof(created_at_us)='integer'),
 UNIQUE(chain,mint), UNIQUE(id,partition_id)
);
CREATE TABLE config_versions (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL, version TEXT NOT NULL,
 content_json TEXT NOT NULL CHECK(json_valid(content_json)),
 content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),
 created_at_us INTEGER NOT NULL,
 UNIQUE(name,version)
);
CREATE TABLE decisions (
 id TEXT PRIMARY KEY,
 filter_result_id TEXT NOT NULL,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 outcome TEXT NOT NULL CHECK(outcome IN ('PASS','SKIP')),
 kind TEXT NOT NULL CHECK(kind='RESEARCH_SHADOW'),
 research_tracking TEXT NOT NULL CHECK(research_tracking='CONTINUE'),
 created_at_us INTEGER NOT NULL,
 UNIQUE(filter_result_id), UNIQUE(id,candidate_id,partition_id),
 FOREIGN KEY(filter_result_id,candidate_id,partition_id) REFERENCES filter_results(id,candidate_id,partition_id)
);
CREATE TABLE filter_results (
 id TEXT PRIMARY KEY,
 replay_run_id TEXT NOT NULL,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 outcome TEXT NOT NULL CHECK(outcome IN ('PASS','FAIL','SKIP','UNCONFIRMED')),
 mode TEXT NOT NULL CHECK(mode='SHADOW'),
 research_tracking TEXT NOT NULL CHECK(research_tracking='CONTINUE'),
 details_json TEXT NOT NULL CHECK(json_valid(details_json)),
 created_at_us INTEGER NOT NULL,
 UNIQUE(replay_run_id), UNIQUE(id,candidate_id,partition_id),
 FOREIGN KEY(replay_run_id,candidate_id,partition_id) REFERENCES replay_runs(id,candidate_id,partition_id)
);
CREATE TABLE forward_observations (
 id TEXT PRIMARY KEY,
 decision_id TEXT NOT NULL,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 horizon_seconds INTEGER NOT NULL CHECK(horizon_seconds IN (600,1800,3600,10800,21600,43200,86400)),
 due_at_us INTEGER NOT NULL,
 recorded_at_us INTEGER,
 state TEXT NOT NULL CHECK(state IN ('PLANNED','RECORDED','MISSING')),
 snapshot_id TEXT,
 data_json TEXT NOT NULL CHECK(json_valid(data_json)),
 event_key TEXT NOT NULL,
 request_sha256 TEXT NOT NULL,
 UNIQUE(decision_id,horizon_seconds,event_key),
 CHECK((state='PLANNED' AND recorded_at_us IS NULL AND snapshot_id IS NULL) OR
       (state='RECORDED' AND recorded_at_us IS NOT NULL AND snapshot_id IS NOT NULL) OR
       (state='MISSING' AND recorded_at_us IS NOT NULL AND snapshot_id IS NULL)),
 FOREIGN KEY(decision_id,candidate_id,partition_id) REFERENCES decisions(id,candidate_id,partition_id),
 FOREIGN KEY(snapshot_id,candidate_id,partition_id) REFERENCES raw_api_snapshots(id,candidate_id,partition_id)
);
CREATE TABLE idempotency_keys (
 scope TEXT NOT NULL,
 key TEXT NOT NULL,
 request_sha256 TEXT NOT NULL CHECK(length(request_sha256)=64),
 result_id TEXT NOT NULL,
 created_at_us INTEGER NOT NULL,
 PRIMARY KEY(scope,key)
);
CREATE TABLE market_observations (
 id TEXT PRIMARY KEY,
 replay_run_id TEXT NOT NULL,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 observed_at_us INTEGER NOT NULL,
 mapping_status TEXT NOT NULL CHECK(mapping_status IN ('CONFIRMED','SYNTHETIC')),
 data_json TEXT NOT NULL CHECK(json_valid(data_json)),
 UNIQUE(replay_run_id),
 FOREIGN KEY(replay_run_id,candidate_id,partition_id) REFERENCES replay_runs(id,candidate_id,partition_id)
);
CREATE TABLE parser_versions (
 id TEXT PRIMARY KEY,
 provider TEXT NOT NULL CHECK(provider IN ('rugcheck','dexscreener','jupiter','xai','synthetic')),
 name TEXT NOT NULL, version TEXT NOT NULL,
 code_sha256 TEXT NOT NULL CHECK(length(code_sha256)=64),
 schema_status TEXT NOT NULL CHECK(schema_status IN ('UNCONFIRMED','CONFIRMED','SYNTHETIC')),
 created_at_us INTEGER NOT NULL,
 UNIQUE(provider,name,version)
);
CREATE TABLE partitions (
 id TEXT PRIMARY KEY CHECK(id IN ('RESEARCH','VALIDATION','FINAL_OOS')),
 description TEXT NOT NULL
);
CREATE TABLE pipeline_versions (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL, version TEXT NOT NULL,
 parser_version_id TEXT NOT NULL REFERENCES parser_versions(id),
 manifest_json TEXT NOT NULL CHECK(json_valid(manifest_json)),
 content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),
 created_at_us INTEGER NOT NULL,
 UNIQUE(name,version), UNIQUE(id,parser_version_id)
);
CREATE TABLE raw_api_snapshots (
 id TEXT PRIMARY KEY,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 provider TEXT NOT NULL CHECK(provider IN ('rugcheck','dexscreener','jupiter','xai','synthetic')),
 endpoint TEXT NOT NULL,
 captured_at_us INTEGER NOT NULL CHECK(typeof(captured_at_us)='integer'),
 ingested_at_us INTEGER NOT NULL CHECK(typeof(ingested_at_us)='integer'),
 http_status INTEGER CHECK(http_status BETWEEN 100 AND 599),
 provenance TEXT NOT NULL CHECK(provenance IN ('live_capture','imported_unverified','synthetic')),
 content_type TEXT NOT NULL,
 payload BLOB NOT NULL CHECK(typeof(payload)='blob'),
 payload_sha256 TEXT NOT NULL CHECK(length(payload_sha256)=64),
 byte_length INTEGER NOT NULL CHECK(byte_length=length(payload)),
 metadata_json TEXT NOT NULL CHECK(json_valid(metadata_json)),
 FOREIGN KEY(candidate_id,partition_id) REFERENCES candidates(id,partition_id),
 UNIQUE(id,candidate_id,partition_id)
);
CREATE TABLE replay_runs (
 id TEXT PRIMARY KEY,
 snapshot_id TEXT NOT NULL,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 parser_version_id TEXT NOT NULL REFERENCES parser_versions(id),
 config_version_id TEXT NOT NULL REFERENCES config_versions(id),
 pipeline_version_id TEXT NOT NULL,
 started_at_us INTEGER NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('UNCONFIRMED','PARSED','PARSE_ERROR')),
 details_json TEXT NOT NULL CHECK(json_valid(details_json)),
 UNIQUE(snapshot_id,parser_version_id,config_version_id,pipeline_version_id),
 UNIQUE(id,candidate_id,partition_id),
 FOREIGN KEY(snapshot_id,candidate_id,partition_id) REFERENCES raw_api_snapshots(id,candidate_id,partition_id),
 FOREIGN KEY(pipeline_version_id,parser_version_id) REFERENCES pipeline_versions(id,parser_version_id)
);
CREATE TABLE schema_migrations (version INTEGER PRIMARY KEY, filename TEXT NOT NULL, sha256 TEXT NOT NULL, applied_at_us INTEGER NOT NULL);
CREATE TABLE social_observations (
 id TEXT PRIMARY KEY,
 replay_run_id TEXT NOT NULL,
 candidate_id TEXT NOT NULL,
 partition_id TEXT NOT NULL,
 observed_at_us INTEGER NOT NULL,
 mapping_status TEXT NOT NULL CHECK(mapping_status IN ('CONFIRMED','SYNTHETIC')),
 data_json TEXT NOT NULL CHECK(json_valid(data_json)),
 UNIQUE(replay_run_id),
 FOREIGN KEY(replay_run_id,candidate_id,partition_id) REFERENCES replay_runs(id,candidate_id,partition_id)
);
CREATE TRIGGER api_snapshot_scope BEFORE INSERT ON api_events
 WHEN NEW.snapshot_id IS NOT NULL AND NOT EXISTS (
 SELECT 1 FROM raw_api_snapshots s WHERE s.id=NEW.snapshot_id AND
 s.partition_id=NEW.partition_id AND s.candidate_id IS NEW.candidate_id AND s.provider=NEW.provider)
 BEGIN SELECT RAISE(ABORT,'API event snapshot scope mismatch'); END;
CREATE TRIGGER forward_due_guard BEFORE INSERT ON forward_observations
 WHEN NEW.due_at_us != (SELECT created_at_us FROM decisions WHERE id=NEW.decision_id)+NEW.horizon_seconds*1000000
 BEGIN SELECT RAISE(ABORT,'forward due time must use decision anchor'); END;
CREATE TRIGGER forward_snapshot_time_guard BEFORE INSERT ON forward_observations
 WHEN NEW.snapshot_id IS NOT NULL AND NOT EXISTS (
 SELECT 1 FROM raw_api_snapshots s WHERE s.id=NEW.snapshot_id AND
 s.captured_at_us >= NEW.due_at_us AND s.captured_at_us <= NEW.recorded_at_us)
 BEGIN SELECT RAISE(ABORT,'forward snapshot outside due-to-recorded interval'); END;
CREATE TRIGGER forward_time_guard BEFORE INSERT ON forward_observations
 WHEN NEW.recorded_at_us IS NOT NULL AND NEW.recorded_at_us < NEW.due_at_us
 BEGIN SELECT RAISE(ABORT,'forward event cannot precede horizon'); END;
CREATE TRIGGER immutable_api_events_delete BEFORE DELETE ON api_events
 BEGIN SELECT RAISE(ABORT,'append-only table: api_events'); END;
CREATE TRIGGER immutable_api_events_update BEFORE UPDATE ON api_events
 BEGIN SELECT RAISE(ABORT,'append-only table: api_events'); END;
CREATE TRIGGER immutable_candidate_discoveries_delete BEFORE DELETE ON candidate_discoveries
 BEGIN SELECT RAISE(ABORT,'append-only table: candidate_discoveries'); END;
CREATE TRIGGER immutable_candidate_discoveries_update BEFORE UPDATE ON candidate_discoveries
 BEGIN SELECT RAISE(ABORT,'append-only table: candidate_discoveries'); END;
CREATE TRIGGER immutable_candidates_delete BEFORE DELETE ON candidates
 BEGIN SELECT RAISE(ABORT,'append-only table: candidates'); END;
CREATE TRIGGER immutable_candidates_update BEFORE UPDATE ON candidates
 BEGIN SELECT RAISE(ABORT,'append-only table: candidates'); END;
CREATE TRIGGER immutable_config_versions_delete BEFORE DELETE ON config_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: config_versions'); END;
CREATE TRIGGER immutable_config_versions_update BEFORE UPDATE ON config_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: config_versions'); END;
CREATE TRIGGER immutable_decisions_delete BEFORE DELETE ON decisions
 BEGIN SELECT RAISE(ABORT,'append-only table: decisions'); END;
CREATE TRIGGER immutable_decisions_update BEFORE UPDATE ON decisions
 BEGIN SELECT RAISE(ABORT,'append-only table: decisions'); END;
CREATE TRIGGER immutable_filter_results_delete BEFORE DELETE ON filter_results
 BEGIN SELECT RAISE(ABORT,'append-only table: filter_results'); END;
CREATE TRIGGER immutable_filter_results_update BEFORE UPDATE ON filter_results
 BEGIN SELECT RAISE(ABORT,'append-only table: filter_results'); END;
CREATE TRIGGER immutable_forward_observations_delete BEFORE DELETE ON forward_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: forward_observations'); END;
CREATE TRIGGER immutable_forward_observations_update BEFORE UPDATE ON forward_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: forward_observations'); END;
CREATE TRIGGER immutable_idempotency_keys_delete BEFORE DELETE ON idempotency_keys
 BEGIN SELECT RAISE(ABORT,'append-only table: idempotency_keys'); END;
CREATE TRIGGER immutable_idempotency_keys_update BEFORE UPDATE ON idempotency_keys
 BEGIN SELECT RAISE(ABORT,'append-only table: idempotency_keys'); END;
CREATE TRIGGER immutable_market_observations_delete BEFORE DELETE ON market_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: market_observations'); END;
CREATE TRIGGER immutable_market_observations_update BEFORE UPDATE ON market_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: market_observations'); END;
CREATE TRIGGER immutable_parser_versions_delete BEFORE DELETE ON parser_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: parser_versions'); END;
CREATE TRIGGER immutable_parser_versions_update BEFORE UPDATE ON parser_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: parser_versions'); END;
CREATE TRIGGER immutable_partitions_delete BEFORE DELETE ON partitions
 BEGIN SELECT RAISE(ABORT,'append-only table: partitions'); END;
CREATE TRIGGER immutable_partitions_update BEFORE UPDATE ON partitions
 BEGIN SELECT RAISE(ABORT,'append-only table: partitions'); END;
CREATE TRIGGER immutable_pipeline_versions_delete BEFORE DELETE ON pipeline_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: pipeline_versions'); END;
CREATE TRIGGER immutable_pipeline_versions_update BEFORE UPDATE ON pipeline_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: pipeline_versions'); END;
CREATE TRIGGER immutable_raw_api_snapshots_delete BEFORE DELETE ON raw_api_snapshots
 BEGIN SELECT RAISE(ABORT,'append-only table: raw_api_snapshots'); END;
CREATE TRIGGER immutable_raw_api_snapshots_update BEFORE UPDATE ON raw_api_snapshots
 BEGIN SELECT RAISE(ABORT,'append-only table: raw_api_snapshots'); END;
CREATE TRIGGER immutable_replay_runs_delete BEFORE DELETE ON replay_runs
 BEGIN SELECT RAISE(ABORT,'append-only table: replay_runs'); END;
CREATE TRIGGER immutable_replay_runs_update BEFORE UPDATE ON replay_runs
 BEGIN SELECT RAISE(ABORT,'append-only table: replay_runs'); END;
CREATE TRIGGER immutable_schema_migrations_delete BEFORE DELETE ON schema_migrations
 BEGIN SELECT RAISE(ABORT,'append-only table: schema_migrations'); END;
CREATE TRIGGER immutable_schema_migrations_update BEFORE UPDATE ON schema_migrations
 BEGIN SELECT RAISE(ABORT,'append-only table: schema_migrations'); END;
CREATE TRIGGER immutable_social_observations_delete BEFORE DELETE ON social_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: social_observations'); END;
CREATE TRIGGER immutable_social_observations_update BEFORE UPDATE ON social_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: social_observations'); END;
CREATE VIEW candidate_discovery_summary AS
 SELECT c.id,c.chain,c.mint,c.partition_id,
 COUNT(d.id) AS discovery_count,MIN(d.occurred_at_us) AS first_seen_at_us,
 MAX(d.occurred_at_us) AS last_seen_at_us
 FROM candidates c LEFT JOIN candidate_discoveries d ON d.candidate_id=c.id GROUP BY c.id;
