# PHASE 2A.5 — RESEARCH PROTOCOL FREEZE 완료 보고

기준일: 2026-10-28 (Asia/Seoul).

PHASE 0 = COMPLETE  
PHASE 1 = LIVE_VALIDATION_PENDING  
PHASE 2A = COMPLETE  
PHASE 2A.5 = COMPLETE  
PHASE 2B = NOT STARTED

**완료 범위: 연구 구조와 변경 절차의 사전 freeze. 운영 활성화는 BLOCKED.**
숫자 근거가 없는 운영 parameter는 null이며, 임의 default를 적용하지 않는다.
실제 token dataset/성과를 분석하거나 전략을 탐색하지 않았다. Phase 1 API 호출도 재시도하지 않았다.

## 1. Candidate universe protocol

등록된 source scope/time의 prospectively ascertained cohort를 연구 대상으로 정의했다.
전체 Solana universe 대표성을 주장하지 않는다. Pump.fun/Raydium/DexScreener family는 구현
coverage를 확인한 non-ranked event feed일 때 primary 합집합에 포함한다. 최소 두 독립 source
family 확인이 필요하다. X/social/manual/ranked discovery는 별도 supplementary strata다.
성과·생존·quote 성공·필터 PASS로 candidate를 포함/제외하지 않는다. Drop/reject/gap도 남긴다.
source별 예상 platform/listing/indexing/popularity/manual selection bias와 상태를 protocol 표에 기록했다.

## 2. T0 definitions

T_CREATION / T_POOL_CREATION / T_FIRST_LIQUIDITY / T_DISCOVERY /
T_PRIMARY_DISCOVERY / T_SNAPSHOT(provider,channel) / T_BASELINE_MARKET /
T_ELIGIBLE(strategy_version) / T_DECISION을 분리했다. 최초 발견은 durable knowledge time이며
source event timestamp로 소급하지 않는다. Universe/risk follow-up은 discovery 원점,
market-return panel은 유효 market baseline 원점, strategy panel은 eligibility/decision 원점을
명시적으로 분리한다. Baseline/eligibility delay와 미도달 candidate도 보고한다.

## 3. Multiple discovery handling

candidate=1, discovery events=여러 개 규칙을 유지한다. Primary timestamp는 최초 qualifying
commit, 동일 시각은 ingestion sequence/event id로 결정한다. 늦은 과거 event는 lateness로
저장하며 최초 discovery를 수정하지 않는다. Source overlap과 first-source membership을 보존한다.
Backfill은 별도 cohort이며 과거에 알았던 데이터로 편입하지 않는다.

## 4. Pool selection protocol

모든 relevant pool을 보존한다. Baseline 시점의 유효·비교 가능·as-of USD liquidity 최대 pool을
primary로 선택하고 tie는 정해진 byte lexicographic order로 처리한다. 당시 후보 목록·제외 이유·
cutoff·rule hash를 남긴다. Series 중 disappearance가 발생해도 유리한 pool로 갈아타지 않는다.
Highest-volume/most-active/earliest-pool은 별도 사전등록 secondary 분석만 허용한다.
가격 방향/유동성 의미/coverage의 실제 mapping은 Phase 1까지 UNCONFIRMED다.

## 5. Forward observation protocol

10m/30m/1h/3h/6h/12h/24h 유지. Target, requested, received, committed, provider event time과
실제 사용 timestamp를 별도로 보존한다. Target 이후 사전 tolerance 창 안의 첫 유효 관측을 선택한다.
오류 retry는 미리 고정한 offsets로만 허용하며, 결과가 나쁘다는 이유로 재시도하지 않는다.
창 밖 late value는 secondary로 남긴다. 이전 nearest 값·interpolation·LOCF는 primary 금지다.
Tolerance 숫자는 미확정이며 그 상태로 수집을 활성화하지 않는다.

## 6. Return definitions

Screen/market = 동일 fixed-pool·통화 P_h/P_0−1. Quote-based indicative executable = baseline
고정 notional B로 얻은 고정 Q의 horizon sell net output S_h/B−1. Quote는 실제 fill 보장이 아니다.
Paper = 사전 execution/cost/failure 규칙 적용 후 net terminal value/initial committed capital−1.
통화·분모·notional·fee 포함 범위와 미관측 liquidation을 구분하고 비용을 중복 차감하지 않는다.
NO_ROUTE/timeout을 0이나 −100% 수익으로 자동 치환하지 않는다. Available subset 성과를 전체
cohort 기대수익으로 일반화하지 않는다.

## 7. MFE/MAE measurement plan

현재 7 horizon 값은 snapshot-sampled MFE/MAE만 제공할 수 있다. Baseline 0과 grid coverage를
포함해 보고한다. True path extremes를 주장하지 않는다. 별도 finer grid/trade stream이 필요하며
cadence와 budget은 outcome을 보기 전 고정한다. 전 cohort 동일 grid 또는 사전 hash-sampled
subcohort를 사용하고 좋은 token만 촘촘하게 관측하지 않는다.

## 8. Rug taxonomy

Liquidity depletion/removal, pool not-observed/verified closure, sell-route unavailable, price collapse,
provider flag, authority/restriction, social claim, migration, outage를 분리했다. 사건은 다중 label과
onset interval을 갖는다. Objective composite는 검증된 removal/closure 또는 restriction과
persistent route loss의 조합으로 설계했지만 magnitude/persistence/coverage/chain schema가
미확정이므로 binary label을 아직 계산하지 않는다. Social/Grok claim은 ground truth가 아니다.

## 9. Missing-data policy

OBSERVED_VALUE / TRUE_ZERO / UNKNOWN / API_FAILURE / NOT_APPLICABLE /
NOT_YET_AVAILABLE / STALE / NO_ROUTE / MISSING_WINDOW / CENSORED /
SCHEMA_UNCONFIRMED / SCHEMA_CHANGED를 구분한다. Null=0 치환 금지.
RugCheck unavailable은 risky가 아니며 Jupiter timeout은 NO_ROUTE가 아니다.
죽거나 사라진 token도 cohort에 남기고 missingness/coverage/분모를 보고한다.

## 10. Stale-data policy

Provider/channel/field-family별 TTL과 source clock 의미를 별도 freeze하도록 설계했다.
Decision cutoff 이전에 실제 commit된 값만 사용할 수 있다. Source timestamp가 없으면 요청/응답
시각은 acquisition proxy일 뿐 underlying freshness 증명이 아니다. Verified age가 필요한 feature는
UNKNOWN으로 차단한다. 후일 likes·risk flag·수정 post를 과거 feature로 역주입하지 않는다.

## 11. Dataset partition policy

Random split 대신 chronological RESEARCH→VALIDATION→FINAL_OOS block을 사용한다.
현재 날짜 경계는 만들지 않았다. 수집 시작 전 calendar boundaries와 buffer 계산 규칙을 고정한다.
같은 candidate는 한 partition에만 속하고 후속 발견으로 이동하지 않는다. Boundary token과 group
contamination은 명시적으로 보존/분리한다. OOS는 별도 권한·암호화·custodian·access audit로 봉인할
계획이며, 현재 SQLite partition 제약을 실제 봉인이라고 주장하지 않는다.

## 12. Strategy freeze policy

Feature/as-of/missing/stale, threshold, entry/exit, sizing, pool rule, execution/cost assumptions,
parser/filter/config/pipeline, social model/prompt/tool/schema, dataset/split, endpoint/inference/
seed/multiplicity/stopping plan을 모두 hash로 고정한다. VALIDATION을 본 뒤 결과에 영향을 주는
변경은 새 research cycle과 fresh holdout을 요구한다. OOS 공개 후 수정 전략의 OOS로 재사용 금지다.

## 13. Multiple-testing controls

모든 hypothesis/grid combination/seed/cost scenario/endpoint 시도를 사전 ledger에 예약한다.
실패/중단/수동 미등록 시도도 삭제하지 않는다. Family와 endpoint를 사전 고정하고 확증 family의
Holm FWER control을 기본 설계로 두되 alpha·유효한 cluster-aware inference는 사전 확정 gate다.
최고 PNL 하나 대신 모든 시도/불확실성/coverage를 보고한다. 결과를 보며 임의 stopping하지 않는다.

## 14. Sample-size decision framework

Estimand·precision/effect/power·event rate 불확실성·creator/time dependence·missingness·family 수에
기초한 계획을 요구한다. Token N뿐 아니라 independent clusters, taxonomy 사건, 비사건 follow-up,
source와 외생적으로 정의한 regime coverage를 확인한다. 임의 숫자는 정하지 않았다. Rare event
부족은 INSUFFICIENT로 보고하고, 사후 winner를 성공 token이라고 정의하지 않는다.

## 15. Cost model framework

Slippage/price impact/network fee/priority fee/실패비용/quote expiry와 latency/requote, protocol/AMM
fee, transfer fee, rent/account 비용을 구분했다. Quote 내 포함 비용과 외부 비용을 reconciliation하고
중복 차감하지 않는다. 미확정 비용을 0으로 쓰지 않는다. Actual fill/실패확률을 이번에 만들지 않았다.

## 16. Research ledger design

Append-only registration→run→result/failure→review decision, protocol/strategy/dataset freeze,
amendment와 partition-access event를 설계했다. Experiment id, UTC, hypothesis, partition, features,
filter config, strategy version, number_of_tests_before, result/decision/notes 및 전체 provenance를
포함한다. Count는 authoritative sequence에서 산출하고 failed strategies를 삭제하지 않는다.
현재는 문서/빈 template이며 실제 concurrent DB ledger enforcement 구현은 후속 승인 업무다.

## 17. 생성/수정 파일

신규:

- RESEARCH_PROTOCOL.md, RUG_TAXONOMY.md, EXPERIMENT_LEDGER_SCHEMA.md
- PHASE2A5_COMPLETION_REPORT.md
- protocol/versions/v1.0.0/: 위 세 규범 문서와 세 template의 불변 사본
- protocol/REGISTRY.jsonl: UTC 등록시각·이유·미래 적용범위·previous hash·artifact hashes
- protocol/templates/: activation_manifest, experiment_event, amendment JSON templates
- protocol/verify_freeze.py: read-only hash/chain/mirror 검증, 활성화 기능 없음
- reports/phase2a5_freeze_verification.json, phase2a5_regression_tests.txt,
  phase2a5_preserved_foundation.json
- archive/phase2a_documentation/: 이전 2A 문서 사본

업데이트: PROJECT_STATUS.md, ARCHITECTURE.md, DATA_SCHEMA.md, DECISIONS.md, HANDOFF.md,
README.md, PACKAGE_MANIFEST.json. 이전 완료 보고서와 Phase 1 archive는 유지했다.

## 18. DB migration / 검증 결과

**새 migration 없음.** 기존 qfoundation runtime source, migration 001/002, initialized DB의
SHA-256이 Phase 2A 배포 manifest와 동일한지 확인했다. Decision-anchored forward 구조를
소급 재해석하지 않았다. Anchor/source/quality/pool/ledger 확장은 후속 additive migration 설계로만 남겼다.

검증: protocol hash/registry chain/current mirror 일치 PASS; 기존 회귀 테스트 **41/41 PASS**.
이 검사는 규칙·파일 정합성에 대한 것이며 통계적 유효성/시장 성과/live API 검증 통과를 의미하지 않는다.
Activation template의 필수 항목 25개는 아직 미해결로 명시되어 있다.

## 19. Phase 1 결과가 필요한 unresolved items

Provider 필드 경로/nullable/type/units, cache·source clock·freshness, pool enumeration과 token
방향/가격 변환, quote notional/fee/expiry/route error semantics, xAI output/tool usage와 social
availability provenance가 남아 있다. Source 전수 coverage, on-chain authority/liquidity-event
증거, OOS access control은 네 API의 Phase 1만으로 해결되지 않는 별도 검증 사항이다.
Tolerance/TTL/cadence/cost/sample plan/date boundaries는 실제 결과를 보며 유리하게 정하지 않고
outcome-blind 근거와 사전 승인으로 activation revision에 기록해야 한다.

## 20. Phase 2B 시작 전 prerequisites

사용자 명시적 승인, 필요한 live contract 확인, source registry/coverage 확정, activation null 해소와
승인, time split/buffer freeze, OOS 봉인 검증, anchor/as-of/quality/ledger additive 구현 계획 및
합성 통합 테스트가 필요하다. 별도 calibration cohort와 confirmatory cohort를 분리한다.
현재 사용자에게 PC 실행을 요청하지 않으며 어떤 prerequisite 실행도 자동 시작하지 않는다.

**PHASE 2A.5 STATUS = COMPLETE — STRUCTURAL_RULES_FROZEN / ACTIVATION_BLOCKED.**

**STOP. Phase 1 = LIVE_VALIDATION_PENDING. Phase 2B = NOT STARTED.**
