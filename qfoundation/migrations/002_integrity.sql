CREATE INDEX discoveries_candidate_time ON candidate_discoveries(candidate_id,occurred_at_us);
CREATE INDEX snapshots_candidate_time ON raw_api_snapshots(candidate_id,captured_at_us);
CREATE INDEX snapshots_payload_hash ON raw_api_snapshots(payload_sha256);
CREATE INDEX replay_partition ON replay_runs(partition_id,started_at_us);
CREATE INDEX forwards_due ON forward_observations(partition_id,state,due_at_us);
CREATE INDEX errors_provider_time ON api_events(provider,occurred_at_us);
CREATE VIEW candidate_discovery_summary AS
 SELECT c.id,c.chain,c.mint,c.partition_id,
 COUNT(d.id) AS discovery_count,MIN(d.occurred_at_us) AS first_seen_at_us,
 MAX(d.occurred_at_us) AS last_seen_at_us
 FROM candidates c LEFT JOIN candidate_discoveries d ON d.candidate_id=c.id GROUP BY c.id;
CREATE TRIGGER forward_due_guard BEFORE INSERT ON forward_observations
 WHEN NEW.due_at_us != (SELECT created_at_us FROM decisions WHERE id=NEW.decision_id)+NEW.horizon_seconds*1000000
 BEGIN SELECT RAISE(ABORT,'forward due time must use decision anchor'); END;
CREATE TRIGGER api_snapshot_scope BEFORE INSERT ON api_events
 WHEN NEW.snapshot_id IS NOT NULL AND NOT EXISTS (
 SELECT 1 FROM raw_api_snapshots s WHERE s.id=NEW.snapshot_id AND
 s.partition_id=NEW.partition_id AND s.candidate_id IS NEW.candidate_id AND s.provider=NEW.provider)
 BEGIN SELECT RAISE(ABORT,'API event snapshot scope mismatch'); END;
CREATE TRIGGER immutable_partitions_update BEFORE UPDATE ON partitions
 BEGIN SELECT RAISE(ABORT,'append-only table: partitions'); END;
CREATE TRIGGER immutable_partitions_delete BEFORE DELETE ON partitions
 BEGIN SELECT RAISE(ABORT,'append-only table: partitions'); END;
CREATE TRIGGER immutable_candidates_update BEFORE UPDATE ON candidates
 BEGIN SELECT RAISE(ABORT,'append-only table: candidates'); END;
CREATE TRIGGER immutable_candidates_delete BEFORE DELETE ON candidates
 BEGIN SELECT RAISE(ABORT,'append-only table: candidates'); END;
CREATE TRIGGER immutable_candidate_discoveries_update BEFORE UPDATE ON candidate_discoveries
 BEGIN SELECT RAISE(ABORT,'append-only table: candidate_discoveries'); END;
CREATE TRIGGER immutable_candidate_discoveries_delete BEFORE DELETE ON candidate_discoveries
 BEGIN SELECT RAISE(ABORT,'append-only table: candidate_discoveries'); END;
CREATE TRIGGER immutable_config_versions_update BEFORE UPDATE ON config_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: config_versions'); END;
CREATE TRIGGER immutable_config_versions_delete BEFORE DELETE ON config_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: config_versions'); END;
CREATE TRIGGER immutable_parser_versions_update BEFORE UPDATE ON parser_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: parser_versions'); END;
CREATE TRIGGER immutable_parser_versions_delete BEFORE DELETE ON parser_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: parser_versions'); END;
CREATE TRIGGER immutable_pipeline_versions_update BEFORE UPDATE ON pipeline_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: pipeline_versions'); END;
CREATE TRIGGER immutable_pipeline_versions_delete BEFORE DELETE ON pipeline_versions
 BEGIN SELECT RAISE(ABORT,'append-only table: pipeline_versions'); END;
CREATE TRIGGER immutable_raw_api_snapshots_update BEFORE UPDATE ON raw_api_snapshots
 BEGIN SELECT RAISE(ABORT,'append-only table: raw_api_snapshots'); END;
CREATE TRIGGER immutable_raw_api_snapshots_delete BEFORE DELETE ON raw_api_snapshots
 BEGIN SELECT RAISE(ABORT,'append-only table: raw_api_snapshots'); END;
CREATE TRIGGER immutable_replay_runs_update BEFORE UPDATE ON replay_runs
 BEGIN SELECT RAISE(ABORT,'append-only table: replay_runs'); END;
CREATE TRIGGER immutable_replay_runs_delete BEFORE DELETE ON replay_runs
 BEGIN SELECT RAISE(ABORT,'append-only table: replay_runs'); END;
CREATE TRIGGER immutable_market_observations_update BEFORE UPDATE ON market_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: market_observations'); END;
CREATE TRIGGER immutable_market_observations_delete BEFORE DELETE ON market_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: market_observations'); END;
CREATE TRIGGER immutable_social_observations_update BEFORE UPDATE ON social_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: social_observations'); END;
CREATE TRIGGER immutable_social_observations_delete BEFORE DELETE ON social_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: social_observations'); END;
CREATE TRIGGER immutable_filter_results_update BEFORE UPDATE ON filter_results
 BEGIN SELECT RAISE(ABORT,'append-only table: filter_results'); END;
CREATE TRIGGER immutable_filter_results_delete BEFORE DELETE ON filter_results
 BEGIN SELECT RAISE(ABORT,'append-only table: filter_results'); END;
CREATE TRIGGER immutable_decisions_update BEFORE UPDATE ON decisions
 BEGIN SELECT RAISE(ABORT,'append-only table: decisions'); END;
CREATE TRIGGER immutable_decisions_delete BEFORE DELETE ON decisions
 BEGIN SELECT RAISE(ABORT,'append-only table: decisions'); END;
CREATE TRIGGER immutable_forward_observations_update BEFORE UPDATE ON forward_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: forward_observations'); END;
CREATE TRIGGER immutable_forward_observations_delete BEFORE DELETE ON forward_observations
 BEGIN SELECT RAISE(ABORT,'append-only table: forward_observations'); END;
CREATE TRIGGER immutable_api_events_update BEFORE UPDATE ON api_events
 BEGIN SELECT RAISE(ABORT,'append-only table: api_events'); END;
CREATE TRIGGER immutable_api_events_delete BEFORE DELETE ON api_events
 BEGIN SELECT RAISE(ABORT,'append-only table: api_events'); END;
CREATE TRIGGER immutable_idempotency_keys_update BEFORE UPDATE ON idempotency_keys
 BEGIN SELECT RAISE(ABORT,'append-only table: idempotency_keys'); END;
CREATE TRIGGER immutable_idempotency_keys_delete BEFORE DELETE ON idempotency_keys
 BEGIN SELECT RAISE(ABORT,'append-only table: idempotency_keys'); END;
CREATE TRIGGER immutable_schema_migrations_update BEFORE UPDATE ON schema_migrations
 BEGIN SELECT RAISE(ABORT,'append-only table: schema_migrations'); END;
CREATE TRIGGER immutable_schema_migrations_delete BEFORE DELETE ON schema_migrations
 BEGIN SELECT RAISE(ABORT,'append-only table: schema_migrations'); END;
CREATE TRIGGER forward_time_guard BEFORE INSERT ON forward_observations
 WHEN NEW.recorded_at_us IS NOT NULL AND NEW.recorded_at_us < NEW.due_at_us
 BEGIN SELECT RAISE(ABORT,'forward event cannot precede horizon'); END;
CREATE TRIGGER forward_snapshot_time_guard BEFORE INSERT ON forward_observations
 WHEN NEW.snapshot_id IS NOT NULL AND NOT EXISTS (
 SELECT 1 FROM raw_api_snapshots s WHERE s.id=NEW.snapshot_id AND
 s.captured_at_us >= NEW.due_at_us AND s.captured_at_us <= NEW.recorded_at_us)
 BEGIN SELECT RAISE(ABORT,'forward snapshot outside due-to-recorded interval'); END;
