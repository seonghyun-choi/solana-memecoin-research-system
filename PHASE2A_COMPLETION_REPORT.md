# PHASE 2A — DATA FOUNDATION 완료 보고

기준일: 2026-10-28 (Asia/Seoul).

```text
PHASE 0 = COMPLETE
PHASE 1 = LIVE_VALIDATION_PENDING
PHASE 2A = COMPLETE
PHASE 2B = NOT STARTED
```

Phase 2A 구현과 테스트를 실제로 완료했다. Phase 1 live validation을 재시도하지
않았으며, 사용자에게 PC 실행을 요구하지 않는다. 모든 테스트는 임시 DB와 합성
payload를 사용했다. 실제 token 수집·tracking·최적화·거래·multi-agent 구현은 없다.

## 1. 생성된 directory tree

```text
q_data_foundation/
  README.md
  PROJECT_STATUS.md
  ARCHITECTURE.md
  DATA_SCHEMA.md
  DECISIONS.md
  HANDOFF.md
  PHASE2A_COMPLETION_REPORT.md
  pyproject.toml
  requirements.txt
  PACKAGE_MANIFEST.json
  qfoundation/
    __init__.py
    __main__.py
    adapters.py
    codec.py
    db.py
    errors.py
    replay.py
    store.py
    time_model.py
    migrations/
      001_foundation.sql
      002_integrity.sql
  tests/
    test_foundation.py
  data/
    foundation.sqlite3
  reports/
    test_results.txt
    db_schema.json
    schema.sql
    verification.json
  archive/
    README.md
    phase1_live_validator.zip
```

## 2. 생성·수정한 파일

위 소스·테스트·DB·문서는 이번 Phase 2A에서 신규 생성했다. PROJECT_STATUS.md는
시작 시 IN_PROGRESS로 기록하고 테스트 통과 후 COMPLETE로 수정했다.
이전 Phase 1 ZIP은 archive에 원본 그대로 복사했으며 실행하거나 수정하지 않았다.
현재 프로젝트의 상태/HANDOFF가 archive 안의 오래된 Phase 2 중단 문구에 우선한다.
이전에 보이지 않는 HANDOFF/소스를 검색했다고 주장하지 않으며, 이번 사용자 지시에
명시된 요구사항을 구현 기준으로 삼았다.

## 3. DB schema 및 migration

SQLite 16개 테이블, migration 2개, 인덱스·조회 view·무결성 trigger를 생성했다.
001은 테이블과 partition seed, 002는 인덱스·append-only·관계/시간 guard를 적용한다.
Migration은 파일 SHA-256을 기록하고 트랜잭션 안에서 적용한다. 재실행은 no-op,
기존 파일 변조·미등록 target·downgrade는 거부한다. 실패한 DDL은 rollback된다.

실제 생성된 DB: `data/foundation.sqlite3`. `PRAGMA integrity_check = ok`,
`PRAGMA foreign_key_check` 위반 0건. 전체 DDL은 `reports/schema.sql`, column/FK/index
메타데이터는 `reports/db_schema.json`, 읽기용 설명은 `DATA_SCHEMA.md`에 있다.

## 4. table별 역할

| Table | 역할 |
|---|---|
| candidates | chain+mint별 단일 identity와 불변 partition |
| candidate_discoveries | 출처·시각·event key별 반복 발견 이력 |
| raw_api_snapshots | 원문 bytes·HTTP metadata·provenance·SHA-256 |
| market_observations | replay에서 파생된 버전별 market JSON |
| filter_results | shadow 결과와 CONTINUE tracking |
| social_observations | replay에서 파생된 버전별 social JSON |
| decisions | 연구용 PASS/SKIP, 실제 거래 판단 아님 |
| forward_observations | 7개 horizon의 계획·관찰·누락 append 이력 |
| api_events | API/transport 오류와 HTTP 상태 이력 |
| config_versions | 이름/버전별 canonical config·hash |
| pipeline_versions | parser/filter/source/runtime manifest·hash |
| parser_versions | provider/parser/version/code hash/schema 상태 |
| partitions | RESEARCH / VALIDATION / FINAL_OOS |
| replay_runs | raw→parser/config/pipeline 처리 lineage |
| idempotency_keys | scope+key와 입력 fingerprint/결과 id |
| schema_migrations | 적용 migration과 checksum 이력 |

## 5. candidate deduplication

UNIQUE(chain,mint), mint는 대소문자를 보존한다. Solana base58 32-byte 주소 문법만
검사하며 on-chain 존재 여부는 추측하지 않는다. SQLite BEGIN IMMEDIATE와 unique
제약으로 동시 발견도 한 candidate로 귀결된다. 8개의 동시 제출 테스트도 통과했다.

## 6. discovery event 구조

candidate_id, partition_id, source, event_key, occurred_at_us, ingested_at_us,
metadata_json, request_sha256을 저장한다. 같은 mint가 Pump.fun 14:01, X 14:05,
DexScreener 14:11에 발견되면 candidate=1, discoveries=3인 테스트를 통과했다.
동일 출처의 서로 다른 이벤트와 순서가 뒤바뀐 입력도 보존한다. first/last seen은
전체 event를 집계하는 view에서 계산하고 candidate 생성시각과 구분한다.

## 7. immutable snapshot 구조

원문 bytes를 SQLite BLOB으로 metadata와 같은 트랜잭션에 저장한다. Raw 및 관련
evidence/version 테이블의 UPDATE/DELETE를 trigger로 거부한다. package connection의
recursive_triggers 설정에서 INSERT OR REPLACE 우회도 차단했다. Admin이 trigger를
제거할 수 있으므로 하드웨어/WORM 수준 보존이라고 주장하지 않는다.

## 8. hashing

payload의 원래 bytes에 SHA-256을 적용한다. JSON 공백/개행도 원문의 일부이므로
그대로 보존하며 reserialization하지 않는다. byte length와 hash를 읽기/replay 시
검사한다. Config/manifest는 별도 q-json-v1 canonical JSON hash를 사용한다.
같은 내용의 다른 실제 capture는 별도 snapshot으로 보존한다.

## 9. adapter architecture

ProviderAdapter 추상 인터페이스와 RugCheckAdapter, DexScreenerAdapter,
JupiterAdapter, XAIAdapter를 구현했다. 인터페이스는 offline parse만 제공한다.
현재 네 adapter는 모두 UNCONFIRMED를 반환하고 market/social 값은 만들지 않는다.
Phase 1 전에 CONFIRMED provider parser를 등록하거나 real-provider normalized
output을 생성하려는 경로는 명시적으로 차단한다. 테스트용 SyntheticParser만 별도다.

## 10. UTC/time model

Canonical time은 UTC Unix epoch 기준 정수 microseconds다. timezone-aware 입력만
받고 naïve datetime과 단위 없는 숫자는 거부한다. `+09:00`과 동등한 `Z` 입력은
같은 정수값이 된다. occurred/captured/ingested/replay/due/recorded clock을 구분한다.
provider event time mapping은 아직 없다. 현재 observation의 observed_at_us는 raw
capture 시각이며 실제 시장 event time이라고 주장하지 않는다.

## 11. error model

NONE / DNS / CONNECT / TIMEOUT / TLS / AUTH / RATE_LIMIT / BAD_REQUEST /
NOT_FOUND / NO_ROUTE / SERVER / HTTP_OTHER / PARSE_ERROR / SCHEMA_CHANGED /
UNCONFIRMED / UNKNOWN을 정의했다. HTTP 인증·rate limit·서버 오류는 NO_ROUTE로
해석하지 않는다. retryable은 분류 metadata일 뿐 자동 재호출을 실행하지 않는다.
Parser 예외는 raw를 유지한 PARSE_ERROR replay가 되고 normalized 값은 없다.
Filter 예외는 전체 replay 트랜잭션을 rollback한다.

## 12. config/pipeline/parser versioning

이름+버전은 불변이다. 동일 버전의 다른 내용은 VersionConflict다. Parser는 provider,
class source hash, schema status를 고정한다. Pipeline은 parser id, filter hash,
foundation 전체 소스/migration hash와 Python/SQLite 버전을 고정한다. Registry는
실제 class hash를 확인한다. 구버전 replay에는 해당 source/runtime도 보존해야 한다.

## 13. partition support

세 partition이 실제 DB에 seed되어 있다. Candidate는 하나의 partition에 불변 소속된다.
후속 raw/replay/observation/filter/decision/forward에 composite FK로 같은 candidate와
partition을 강제한다. 다른 partition으로 candidate를 재등록하거나 lineage를 연결하는
시도는 실패한다. OOS 접근 제어·embargo·dataset split 정책 자체는 아직 정의하지 않았다.

## 14. replay 구조

저장된 raw snapshot → 지정된 parser version → 지정된 config version → pipeline에
고정된 shadow filter → append-only normalized observation/filter/연구 decision 순서다.
(snapshot, parser, config, pipeline) 조합은 유일하다. 같은 조합은 기존 run을 반환하고,
새 config/parser는 이전 결과와 raw를 보존한 채 새 run을 만든다. API fallback이 없다.
소켓을 차단한 상태의 provider replay 테스트도 통과했다.

## 15. idempotency와 forward infrastructure

Discovery/capture/API event/forward 기록은 scope+stable key+입력 SHA-256으로 중복을
처리한다. 같은 key에 다른 입력은 덮어쓰기 대신 오류다. Replay는 버전 tuple unique,
forward planning은 decision+horizon+plan key로 중복을 차단한다.

Filter FAIL=tracking termination이 아니다. 합성 risk_score=55 / threshold=40 테스트는
FAIL을 보존하면서 decision=SKIP, research_tracking=CONTINUE임을 검증했다. 이 수치는
테스트 입력이지 제안 threshold가 아니다.

PASS/SKIP 모두 10m/30m/1h/3h/6h/12h/24h 계획을 생성할 수 있다. 기준시각은 immutable
decision timestamp다. 실측은 계획을 수정하지 않고 별도 행으로 append한다. horizon
이전 기록과 오래된 snapshot 연결은 거부한다. 실제 tracking이나 scheduler는 없다.

## 16. 실제 실행한 test 목록

아래 41개 테스트를 `python -m unittest discover -s tests -v`로 실행했다.
각 테스트의 원본 출력은 `reports/test_results.txt`에 보존했다.

- `test_api_event_and_idempotency` — PASS
- `test_api_event_snapshot_partition_mismatch_rejected` — PASS
- `test_candidate_deduplication` — PASS
- `test_composite_fk_blocks_partition_leak` — PASS
- `test_concurrent_candidate_and_discovery` — PASS
- `test_config_versioning_canonical_and_immutable` — PASS
- `test_confirmed_provider_mapping_registration_blocked` — PASS
- `test_database_creation_and_foreign_keys` — PASS
- `test_discovery_idempotency_and_conflict` — PASS
- `test_error_taxonomy` — PASS
- `test_failed_migration_atomic_rollback` — PASS
- `test_filter_fail_never_terminates_research` — PASS
- `test_filter_failure_rolls_back` — PASS
- `test_forward_horizons_pass_and_skip_idempotent` — PASS
- `test_forward_record_append_only` — PASS
- `test_forward_rejects_early_event_and_stale_snapshot` — PASS
- `test_hash_corruption_detected` — PASS
- `test_invalid_mint_rejected_no_lowercasing` — PASS
- `test_migration_downgrade_rejected` — PASS
- `test_migration_tamper_detected` — PASS
- `test_migration_upgrade_and_rerun` — PASS
- `test_multiple_discovery_events` — PASS
- `test_naive_time_rejected` — PASS
- `test_no_secret_endpoint_or_known_payload` — PASS
- `test_online_backup_preserves_raw` — PASS
- `test_parser_error_saved_without_inventing_fields` — PASS
- `test_parser_version_mismatch_rejected` — PASS
- `test_partition_identity_cannot_move` — PASS
- `test_payload_exact_bytes_hash` — PASS
- `test_pipeline_versioning` — PASS
- `test_provider_adapters_unconfirmed_no_normalization` — PASS
- `test_raw_snapshot_immutable_sql` — PASS
- `test_real_adapter_replay_skeleton_offline` — PASS
- `test_replace_cannot_bypass_immutability` — PASS
- `test_replay_idempotency` — PASS
- `test_replay_new_config_preserves_old` — PASS
- `test_replay_new_parser_preserves_raw_and_old_result` — PASS
- `test_same_source_multiple_events_and_out_of_order` — PASS
- `test_snapshot_idempotency_and_new_capture` — PASS
- `test_unconfirmed_parse_no_live_calls_even_with_valid_looking_body` — PASS
- `test_utc_normalization` — PASS

## 17. test 결과

**41 tests passed / 0 failed / 0 skipped.** DB 생성·upgrade·재실행·migration 변조 및
rollback, 동시 dedup, 다중 discovery, raw immutability/REPLACE 차단/hash 변조 감지,
UTC/naïve 입력, config/pipeline 버전, 오류 taxonomy, provider UNCONFIRMED gate,
replay idempotency/버전별 재처리/rollback, CONTINUE tracking, 7 horizon의 PASS/SKIP
지원, partition/FK/time guard, 알려진 secret 거부, online backup을 확인했다.

배포 DB에는 partitions=3, schema_migrations=2만 존재한다. candidates/snapshots/replay/
observations/decisions 등 업무 행은 모두 0이다. 테스트 결과는 live 검증 증거가 아니다.

## 18. Phase 1 완료 후 연결할 부분

실제 HTTP capture 원문 bytes/provenance를 가져와 승인된 field schema·nullable·단위·오류
규칙을 검증한다. 이후 real-provider parser에 새 버전을 부여하고 current UNCONFIRMED
등록/replay gate를 승인에 따라 수정한다. Live contract tests와 replay 회귀 비교를 연결한다.
기존 pending Phase 1 상태는 그 작업이 실제 완료되기 전까지 바꾸지 않는다.

## 19. Phase 2B에서 해야 할 작업

아직 시작하지 않았다. 승인을 받으면 검증된 parser 연결, 제한된 ingestion orchestration,
rate/error handling, observation 품질/freshness, forward scheduling과 missing/late-data
규칙, partition freeze/embargo, 통합 contract tests를 검토할 수 있다. 이는 다음 단계의
제안 목록이며 unseen 이전 HANDOFF의 정확한 범위를 복원했다고 주장하지 않는다.
최적화·Grok trading decision·wallet·transaction·실거래 기능은 포함하지 않는다.

## 20. technical debt / known risks

DB owner의 변조 방어, 대용량 BLOB 증가와 single writer 병목, 외부 parser 의존성의
archive/sandbox, caller-declared provenance 검증, 미확정 typed observation schema,
OOS 접근 정책, future observation 선택 규칙, 실제 OS별 실행·load/soak/복구 시험이
남아 있다. 알려지지 않은 secret이 payload 안에 있을 경우 자동 완전탐지는 불가능하다.
자세한 근거와 trade-off는 DECISIONS.md에 기록했다.

**STOP. Phase 1은 LIVE_VALIDATION_PENDING으로 유지한다. Phase 2B는 사용자 승인 전까지 시작하지 않는다.**
