# EXPERIMENT_LEDGER_SCHEMA — v1.0.0

현재 단계: **설계 및 빈 template만 제공**. 실제 hypothesis/strategy 검색·결과 실행은 없다.
DB migration은 이번에 추가하지 않는다. 다음 승인된 구현에서 append-only DB 제약, server sequence,
원자적 등록, 권한·export 검증을 구현한다. 파일 JSONL만으로 동시성/변조 방지가 해결됐다고 주장하지 않는다.

## 공통 immutable event envelope

| field | 의미 |
|---|---|
| ledger_event_id | globally unique append event id |
| sequence | registry에서 원자적으로 부여하는 단조 증가 순번 |
| event_type | PROTOCOL_REGISTERED / ACTIVATION_FROZEN / DATASET_FROZEN / STRATEGY_FROZEN / EXPERIMENT_REGISTERED / RUN_STARTED / RUN_RESULT / RUN_FAILED / RUN_ABORTED / REVIEW_DECISION / AMENDMENT / PARTITION_ACCESS |
| created_at_us / available_at_us | canonical UTC 시간; backdate 금지 |
| actor / reason | 생성 주체와 이유 |
| research_cycle_id / experiment_id / run_id | cycle/hypothesis/evaluation 단위 연결 |
| protocol_version / protocol_sha256 | 승인된 protocol에 대한 참조 |
| payload | event-type별 구조 |
| previous_event_sha256 / event_sha256 | canonical JSON(q-json-v1) hash chain; hash 계산 시 자신의 event_sha256 제외 |
| supersedes_event_id | correction이면 원래 event를 참조; 원문 삭제 아님 |

Hash chain은 secret signature·외부 timestamp 공증·불변 보관소의 대체가 아니다. 정기 signed manifest,
독립 백업과 접근 감사는 운영 전에 별도 구현한다. 결측 필드는 null+reason이며 빈 문자열/0으로 채우지 않는다.

## EXPERIMENT_REGISTERED payload

experiment_id, research_cycle_id, created_at, hypothesis, rationale, confirmatory_or_exploratory,
family_id, family_definition, primary_endpoint, secondary_endpoints, estimand, null_hypothesis,
dataset_partition, dataset_manifest_hash, split_manifest_hash, source_strata, features,
filter_config_hash, config_version, parser_versions, pipeline_version, strategy_version/hash,
execution_model_version, cost_model_version, social_model/prompt/schema/tool versions,
planned_threshold_grid, planned_seed_list, planned_evaluation_count, multiplicity_method/alpha,
inference_method/cluster_unit, sample_size_plan, stopping_rule, missing/stale/coverage rules,
number_of_tests_before, number_of_strategies_before, registration_status, notes.

number_of_tests_before는 등록 당시의 actual evaluation count를 server ledger에서 산출한 audit 값이다.
계획 grid count와 completed/failed/aborted evaluation count를 각각 유지한다. 결과가 없다는 이유로
count를 줄이지 않는다. evaluation_id는 `(cycle, strategy version, dataset manifest, parameter tuple,
seed, endpoint family, cost scenario)`를 구분하고 사전 family 정책으로 시도 수를 센다. 한 call에서
여러 조합을 평가하면 모든 조합의 child evaluation registration이 필요하다. 같은 확정 artifact의
재현 실행은 reproduction_of를 붙이고 독립 가설 수와 compute-run 수를 별도 표시한다.

## 결과 / 실패 / 결정

RUN_RESULT는 등록 event와 run_id를 참조하고 executed_config_hash, start/end, code/environment hash,
실제 데이터 manifest, partition exposure, result artifact hash/path, 모든 사전 endpoint 값과 uncertainty,
coverage/denominator, cost sensitivity, multiplicity-adjusted 결과, deviations를 저장한다.
미관측 result는 null+reason이다. 최고 결과만 덮어쓰는 `result` 컬럼 하나를 사용하지 않는다.
RUN_FAILED / RUN_ABORTED는 reason/error type/partial artifacts/노출한 partition/소비한 evaluation count를
보존한다. REVIEW_DECISION은 RETAIN / REJECT / INSUFFICIENT / NEW_CYCLE_REQUIRED와 이유를 별도로 append한다.
등록되지 않은 수동 분석을 발견하면 UNREGISTERED_EXPLORATORY event로 기록하고 확증 결과에서 제외한다.

## Protocol/strategy/dataset freeze와 access

Freeze event는 문서/설정/코드/모델/prompt/데이터 목록 hash, 승인 주체, 시각, 미래 적용 cohort,
required prereqs 및 null blocker 목록을 보존한다. PARTITION_ACCESS는 partition, 범위, 목적,
요청/승인/열람 시각과 actor를 남긴다. 실패한 접근도 기록한다. OOS 열람을 취소하여 미노출로
되돌릴 수 없다. VALIDATION을 본 뒤 수정한 전략은 새 cycle과 fresh holdout을 요구한다.

## 예상 additive DB 설계 (DDL 적용하지 않음)

protocol_versions + protocol_amendments; source_registry_versions; cohort_membership_events;
candidate_time_anchors; observation_availability; pool_selection_events; forward_capture_attempts;
quality_annotations; outcome_events; partition_manifests + partition_access_events;
strategy_freezes; experiment_registrations + experiment_events + evaluation_registrations.

기존 candidate/raw/version/replay id를 FK로 참조한다. version/hash와 정합성 제약을 추가하고 기존
테이블/immutable migration은 수정하지 않는다. Candidate partition 한 개 규칙을 유지한다.
현재 `idempotency_keys`/`config_versions`를 새 ledger로 가장해 의미를 바꾸지 않는다.
