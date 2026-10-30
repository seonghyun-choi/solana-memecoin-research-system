# RESEARCH_PROTOCOL — v1.0.0

상태: **STRUCTURAL_RULES_FROZEN / ACTIVATION_BLOCKED**.
작성일: 2026-10-28 (Asia/Seoul). 정확한 등록 UTC 시각과 파일 SHA-256은
`protocol/REGISTRY.jsonl`에 기록한다. 이 문서의 동일 bytes를
`protocol/versions/v1.0.0/RESEARCH_PROTOCOL.md`에 보존한다.

목적은 전략 탐색이 아니라 연구·수집 절차의 사전 고정이다. Phase 1은
LIVE_VALIDATION_PENDING, Phase 2B는 NOT STARTED다. 실제 token outcome 분석이나
API 호출은 이번 작업에서 하지 않는다. 과거 Phase 1에서 일부 응답 형태를 본 사실은
숨기지 않는다. 이번 설계는 그 가격·순위·수익 결과를 사용해 선택하지 않았다.
완전한 사전 미노출을 주장하지 않으며 과거 관찰은 confirmatory cohort에서 제외한다.

## 0. Freeze 의미, 상태와 활성화 gate

CONFIRMED는 이번 프로젝트의 방법론상 확정된 규칙이다. provider의 API 구현이나
전체 시장 coverage를 검증했다는 뜻이 아니다. PROVISIONAL은 운영 manifest에서
확정할 설계 선택이고, UNCONFIRMED는 실제 schema/coverage/clock 확인이 필요한 항목이다.

v1.0.0은 아래 구조·금지 규칙을 지금 고정한다. 숫자 근거가 없는 tolerance, stale TTL,
rug magnitude/persistence, cadence, size/notional, split date와 표본 수는 만들어내지
않는다. 이들은 `activation_manifest.template.json`의 null 상태이며 **수집/확증 분석에
사용 가능한 완결된 운영 protocol이 아니다**. 값이 없으면 permissive default를 쓰지 않고
BLOCKED다. outcome을 보지 않는 운영 준비 단계와 명시적 승인을 거쳐 별도의 activation
revision을 추가해야 한다. 현재 단계 완료는 연구수집 개시 승인이 아니다.

필수 사전 gate: source registry/실제 scope 확정, clock/availability 정의 검증, Phase 1
schema 승인, 관측 budget/cadence/TTL/tolerance/재시도 스케줄 확정, objective label
매개변수 확정, split freeze 및 sample/analysis plan 등록. 운영 준비에 token이 필요해지면
별도 승인된 calibration cohort로 격리하고 RESEARCH/VALIDATION/OOS에 재사용하지 않는다.
이번 단계에서는 calibration도 실행하지 않는다.

## 1. Candidate universe와 source bias

추정 대상은 **사전 등록된 감시 source와 감시 시간·범위에서 prospectively 포착된 Solana
mint들의 cohort**다. 전체 Solana memecoin universe를 완전 관측했다고 주장하지 않는다.
memecoin 판별은 불명확할 수 있으므로 기본 registry는 모든 범위 내 token 발견을 보존하고,
memecoin-tagged subset은 outcome 독립적인 사전 token-type classifier의 별도 분석층으로 둔다.
상장 지속, 향후 수익, rug 여부, quote 성공, social 인기, 검증 통과를 inclusion 조건으로 쓰지 않는다.

| Source family | 예상 selection bias / blind spot | 상태와 처리 |
|---|---|---|
| Pump.fun 계열 | 해당 발행 플랫폼 편향; migration/graduation된 token만 보면 생존/성공 편향 | family 포함 CONFIRMED; 최초 발행/전체 event feed 접근 UNCONFIRMED. 졸업/인기 목록만으로 primary universe 구성 금지 |
| Raydium 계열 | pool 생성·유동성 공급된 token 편향; pool 미생성·타 venue·즉시 소멸 누락 | family 포함 CONFIRMED; launch/pool 이벤트 coverage·지연 UNCONFIRMED |
| DexScreener | 인덱싱되는 venue와 활동 있는 pool 편향; trending/ranking/검색은 인기 편향 | family 포함 CONFIRMED; 전수형 이벤트/등록 범위 UNCONFIRMED. trending 발견은 secondary ascertainment stratum |
| X/social | 언어·시간대·검색 순위·봇·홍보·삭제·계정 sampling 편향 | secondary cohort CONFIRMED; 계정/키워드/검색 cadence PROVISIONAL; 결과 완전성 UNCONFIRMED |
| manual/external | 추천자의 선택·성과 인지·추천 시점·출처 누락 편향 | append-only supplementary cohort CONFIRMED; primary 성과 추정에서 제외 |

Primary cohort는 사전 scope의 **event-driven non-performance-ranked feed**로 실제 검증된
source의 합집합이다. 최소 두 독립적인 source family가 확인되기 전 primary 활성화를 막는다.
동일 upstream을 재판매하는 두 provider는 독립 source family로 세지 않는다. 특정 family를
제공하는 구현이 아직 확정되지 않았으면 이름·API를 임의 지정하지 않는다.

Social-only/manual-only/ranked-feed-only token도 candidate로 보존하되 별도 stratum이다.
후일 event feed에 나타나도 최초 cohort membership을 outcome을 본 뒤 변경하지 않는다.
새 event와 membership-history를 추가하며 사전 정의한 sensitivity 분석에서만 다룬다.
raw source event id, query/page/cursor, 검색 범위·정렬·언어, 관측 창, 반환 개수·제한,
수집 성공/실패·gap·rate limit을 보존한다. 전체 결과 pagination이 불가하면 truncated 표시한다.
알 수 없는 모집단 포착 확률을 임의 weighting하거나 social 결과 수로 전수 coverage를 주장하지 않는다.

감시 창 안에서 유효 32-byte mint가 최초 관측되고 사전 chain/scope 규칙에 맞으면 등록한다.
잘못된 주소는 rejected-event log에 이유와 원문을 남긴다. 사전 denylist는 테스트/중복/비대상
자산 같은 outcome 독립적 근거만 허용한다. metadata 미확인은 UNKNOWN으로 남긴다.
capacity 초과 시 고정 queue 순서 또는 사전 salt를 가진 mint hash sampling을 **활성화 전에
하나만 선택**한다. popularity/가격 변동으로 우선순위를 바꾸지 않는다. drop도 로그에 남긴다.

## 2. T0 / availability 정의

모든 시간은 timezone-aware 입력에서 변환한 UTC microseconds다. event time과 우리 시스템의
knowledge time을 분리한다. 요청 시작, 응답 수신, durable commit도 별도 저장한다.

| 시간 | 정의 | 주의 |
|---|---|---|
| T_CREATION | 검증된 chain token creation event 시각 | 확인 안 되면 UNKNOWN; 최초 조회시각으로 대체 금지 |
| T_POOL_CREATION(pool) | 해당 pool 생성 event 시각 | token 생성과 다름 |
| T_FIRST_LIQUIDITY(pool) | 검증된 첫 유효 유동성 event 시각 | pool 생성과 다름; provider 조회 범위 밖이면 미확인 |
| T_DISCOVERY(candidate) | 우리 시스템에 최초 유효 발견이 durable commit된 knowledge time | source가 나중에 보고한 과거 event time으로 backdate 금지 |
| T_PRIMARY_DISCOVERY | 사전 primary source scope 안에서 처음 commit된 발견 | primary source가 없으면 UNKNOWN; 전체 최초 발견과 구분 |
| T_SNAPSHOT(provider,channel) | 요청이 성공하고 요구 데이터의 schema 검증이 끝나 durable 저장된 첫 시각 | HTTP 200만으로 성공 아님; failure 원문도 먼저 보존 |
| T_BASELINE_MARKET | T_DISCOVERY 이후 승인된 market baseline이 처음 유효하게 commit된 시각 | baseline 지연 제한 내여야 함; denominator 시각 |
| T_ELIGIBLE(strategy_version) | 그 시점에 이미 available했던 필수 input이 모두 충족되어 첫 평가 가능해진 시각 | 버전별 사건; feature/score threshold PASS와는 다름 |
| T_DECISION(run) | research decision 생성 시각 | 기존 2A forward anchor; discovery 시각이라고 이름 바꾸지 않음 |

Primary universe/risk follow-up의 시간 원점은 T_DISCOVERY다. 시장 return primary panel의 원점은
T_BASELINE_MARKET이며 `baseline_delay = T_BASELINE_MARKET - T_DISCOVERY`를 반드시 함께 보고한다.
Discovery 시각의 실제 가격이 없는데 그 시각의 return을 구성하지 않는다. Primary baseline은
고정된 최대 지연 안에서만 허용하고 실패한 candidate는 baseline missing으로 cohort에 남긴다.
T_ELIGIBLE-anchored strategy panel과 decision-anchored execution panel은 별도 secondary estimand다.
각 return은 anchor_type/id, target time, denominator snapshot/가격/knowledge time을 저장한다.

T_ELIGIBLE까지 살아남은 표본만으로 discovery universe의 성과라고 말하지 않는다. 그 이전
사망/관측불가/미평가 token을 분모에 유지하고 eligibility delay·미도달 비율을 별도 보고한다.

## 3. Multiple discovery events

candidate identity는 chain+case-sensitive mint 하나다. 발견은 모두 append한다.
14:01 Pump.fun, 14:07 X, 14:23 DexScreener가 실제 commit 순서이면 T_DISCOVERY=14:01이며
이후 두 event를 삭제하지 않는다. 단, 14:23에 받은 event가 source time 13:59라고 주장해도
이미 frozen한 T_DISCOVERY는 변경하지 않는다. reported event time과 lateness를 별도 기록한다.
동시 commit은 durable ingestion sequence, 그 다음 event_id의 고정 byte-order로 tie-break한다.
Primary source 안의 최초 event도 같은 규칙으로 결정한다. 모든 retrospective backfill은
별도 backfill cohort이며 과거에 알았던 것으로 편입하지 않는다. source overlap/first-source
cohort와 중복 제거 전후 count를 보고해 ascertainment 차이를 보존한다.

## 4. Pool selection

발견된 relevant pool은 모두 raw 및 관측 lineage로 보존한다. relevant은 target mint가
base 또는 quote인, 사전 chain/venue scope 내 pool이다. 가격 역산·USD 변환·quote 방향과
pool liquidity 필드 의미는 Phase 1 승인 전 UNCONFIRMED다. pair count cap/gap도 저장한다.

**시장 baseline primary rule은 승인된 비교 가능 USD liquidity 최댓값**으로 사전 고정한다.
숫자가 유효하고 동일 as-of cutoff에서 stale이 아닌 snapshot만 비교한다. 동일 liquidity면
(chain,dex_id,pair_address)의 case-sensitive byte lexicographic 순으로 선택한다. 이 규칙은
성과가 더 좋다는 주장도, spoof-resistant하다는 주장도 아니다. 최댓값 선택 시점에 존재한
pool 목록·값·제외 이유·rule hash·knowledge cutoff를 보존한다. 최신 volume/미래 liquidity를
과거 선택에 쓰지 않는다. 동시 요청 자료를 합칠 때 cutoff는 필요한 결과들의 마지막 commit이며
baseline 지연/staleness gate를 다시 확인한다.

선택한 primary pool을 해당 baseline-return series 전체에서 고정한다. 이후 disappearance나
illiquidity 시 더 유리한 pool로 자동 교체하지 않는다. 같은 pool 가격을 못 얻으면 missing이다.
동적 deepest-pool, highest-volume, most-active, earliest-pool은 사전 등록된 secondary 분석만
허용하며 별도 series id와 denominator를 갖는다. Secondary 결과를 본 뒤 primary로 승격 금지.
Migration successor pool은 별도 continuity evidence와 사전 bridge 정책 없이는 splice하지 않는다.
모든 pool 가격이 unavailable이면 token은 cohort에 남고 baseline은 UNKNOWN이다.

## 5. Forward capture, tolerance, retry

Horizons = 600/1800/3600/10800/21600/43200/86400초. 각 panel의 anchor에 더한 target_timestamp와
실제 requested_at/response_received_at/committed_at 및 provider event timestamp를 보존한다.
`actual_timestamp`는 승인된 시장 event timestamp가 있으면 그것, 없으면 응답수신 timestamp를
proxy로 표시한다. proxy를 진짜 체결시각이라고 부르지 않는다.

Primary capture는 target 이후에 요청한다. 허용 창은 `[target, target+tolerance[h,channel]]`이며
수치와 scheduler retry offsets는 activation manifest에 미리 확정해야 한다. 동일 창 안에서
**가장 먼저 유효한 관측**을 선택한다. 더 높은 가격/더 가까운 결과를 나중에 골라 교체하지 않는다.
원본 attempt를 모두 저장한다. retry는 API/transport 실패나 불완전 payload에만 고정 스케줄로
허용한다. 낮은 수익·zero·NO_ROUTE를 원하는 값이 나올 때까지 재시도하지 않는다.

창 만료는 MISSING_WINDOW. 늦게 도착한 값은 LATE_SECONDARY로 별도 보존하고 primary 빈칸을
채우지 않는다. target 이전 nearest observation, 미래의 값으로 과거값 대체, 가격 interpolation,
last observation carried forward는 primary에서 금지한다. 실제 horizon deviation을 보고한다.
기간 종료 직전 token에도 마지막 등록시각+24h+최대 허용 window까지 follow-up을 제공한다.
중간 중단은 administrative censoring으로 표시하며 survivor-only 삭제를 하지 않는다.

## 6. Return 정의와 분모

기본 quote/시장 기준 통화는 activation manifest에서 한 가지로 고정하고 토큰별로 바꾸지 않는다.
통화/decimals/변환은 확정 parser를 쓴다. 각 metric은 분석 단위(candidate/pool/lot), anchor,
baseline value, denominator currency, amount, costs 포함 범위를 명시한다.

- Screen/market return: 같은 고정 pool, 같은 가격 기준 통화의 `P_h/P_0 - 1`.
  P_0는 T_BASELINE_MARKET의 관측값이다. 투자 가능성·체결 보장·순이익이라고 부르지 않는다.
- Quote-based indicative executable return: baseline의 고정 input notional B로 받은 token
  수량 Q를 고정하고, horizon의 Q 매도 quote net base output S_h에 대해 `S_h/B - 1`.
  매 시점 Q를 새로 늘리지 않는다. Jupiter aggregator route와 fixed market pool은 다른 대상이다.
  quote 성공은 그 순간의 indicative feasibility일 뿐 실제 체결 보장이 아니다. NO_ROUTE/expired
  quote/API 실패 시 executable return은 해당 상태로 결측이며 0 수익이나 -100%로 자동 치환하지 않는다.
- Paper execution return: 사전 latency/fill/expiry/cost/failure 규칙을 적용한 가상 cashflow의
  `net terminal liquidation value / initial total committed capital - 1`.
  실제 fill을 주장하지 않는다. initial cost를 분모에 포함했다면 분자에서 재차 빼지 않는다.
  failed entry/exit, 남은 inventory, unresolved liquidation도 보존한다.

SOL input/output이면 SOL return, USD valuation이면 별도 as-of FX evidence를 갖는 USD return이다.
두 통화를 혼합하지 않는다. Network fee에 필요한 별도 native reserve도 비용 manifest에 포함한다.
전체 cohort, baseline-available, quote-evaluable, paper-entered 각각의 분모/coverage를 보고한다.
관측 가능 subset 평균을 전체 기대수익으로 일반화하지 않는다. 미관측 outcome의 임의 imputation은
금지하고 coverage 및 사전 등록된 식별구간/시나리오만 보고한다. terminal write-off=-100%는 검증된
terminal-loss 정의와 별도 accounting 정책이 확정된 경우만 허용한다.

## 7. MFE / MAE

7개 horizon만으로는 실제 경로의 최대/최소를 복원할 수 없다. 기본 출력은
`snapshot_sampled_MFE=max(observed return)`와 `snapshot_sampled_MAE=min(observed return)`이며
baseline 0을 포함하고 grid coverage를 같이 보고한다. 정상적인 동일 가격 경로라는 조건에서
sampled max는 실제 max의 하한, sampled min은 실제 min의 상한이다. noisy/stale/다른 pool 혼합이면
이 해석도 보장하지 않는다. 가격이 사라진 구간은 극값이 없었다는 뜻이 아니다.

정밀 분석에는 별도 고정 finer grid 또는 검증된 pool trade stream이 필요하다. grid cadence,
clock 기준, OHLC 사용 조건, gap 허용치, event aggregation, 최대 지연 및 budget을 결과를 보기 전에
확정한다. 좋은 token만 더 자주 관측하지 않는다. 모든 cohort에 동일 grid 또는 사전 hash-sampled
subcohort를 적용한다. cadence 미확정 상태에서는 true MFE/MAE라는 명칭과 결과를 발표하지 않는다.

## 8. Rug 및 사건 label

`RUG_TAXONOMY.md`가 규범 문서다. Observed technical event, provider claim, social claim과
intent/fraud judgement를 분리한다. 단일 Grok/X 의견은 ground truth가 아니다. Parameterized
liquidity/price/route/pool/authority 사건을 각기 저장하고 중첩 발생을 허용한다. magnitude,
persistence, scope와 outage controls가 확정되기 전 binary rug label은 UNRESOLVED다.
향후 binary measured-rug-like label은 등록된 composite definition version으로만 산출하고
범죄/고의 확정이나 sell 불가능의 보편적 증명이라고 해석하지 않는다.

## 9. Missing state

| state | 뜻 | 수치 처리 |
|---|---|---|
| OBSERVED_VALUE | 유효 값 | 승인된 단위로 보존 |
| TRUE_ZERO | field가 의미상 관측된 실제 0 | 0 보존; validity evidence 필요 |
| UNKNOWN | 값/의미를 알 수 없음 | null+reason |
| API_FAILURE | timeout/auth/rate limit/server/transport 오류 | null+error event; 위험 판정 금지 |
| NOT_APPLICABLE | 사전 규칙상 적용 불가 | null+applicability rule |
| NOT_YET_AVAILABLE | 늦게 생길 수 있는 미완성 정보 | null; 과거 decision 소급 사용 금지 |
| STALE | age gate 미충족 | 값은 raw에 보존, primary feature 사용 금지 |
| NO_ROUTE | 승인된 성공 응답의 특정 pair/size route 부재 | 수치 0 아님; route event |
| MISSING_WINDOW / CENSORED | 창내 capture 실패 / 연구 종료 등 follow-up 제한 | 이유·분모 유지 |
| SCHEMA_UNCONFIRMED / SCHEMA_CHANGED | parser 의미 미확정/계약 변경 | normalized 값 생성 중단 |

missing/null과 zero는 서로 변환하지 않는다. RugCheck unavailable은 risky가 아니고,
Jupiter API_TIMEOUT은 NO_ROUTE가 아니다. Token별 missingness pattern, source별 API downtime,
수집 gap, baseline/각 horizon eligibility를 보고한다. Failure/rug/delisting 이후에도 관측 시도
일정은 유지하되 중단 원인은 명시한다. MNAR 가능성 때문에 complete-case 성과만 보고하지 않는다.

## 10. Stale / as-of policy

각 provider+channel+field-family별 TTL을 별도로 정한다. 가격/quote, security report, social
post, profile은 동일 TTL을 공유하지 않는다. TTL 숫자는 아직 UNCONFIRMED다. provider source
clock의 의미·cache 갱신 정책·quote expireAt을 검증한 뒤 outcome-blind latency/freshness
calibration과 연구 필요성을 근거로 activation revision에 고정한다.

Decision cutoff d에 사용할 값은 `available_at=durable_commit_at <= d`여야 한다. source event
시각도 d 이후일 수 없다. 확인된 source event age가 TTL 내인지 검사한다. source time이 없으면
cache-age UNKNOWN이며 요청/응답 시각은 acquisition recency proxy일 뿐 underlying freshness의
증명이 아니다. 해당 feature가 verified event age를 요구하면 UNKNOWN으로 fail-closed한다.
proxy 허용 feature는 사전에 명시한 별도 flag/TTL을 쓰고 분석에서 구분한다.

Provider timestamp만 과거라는 이유로 나중 수신된 응답을 과거 decision에 붙이지 않는다.
Social feature는 그때 수신된 당시 post 내용/metrics만 사용하며 후일 likes·수정·삭제·retweet
수치를 과거로 소급하지 않는다. 이후 RugCheck flag는 outcome label일 수 있지만 baseline feature가 아니다.
Replay는 당시 available snapshot 집합만 재현한다. 사후 parser 수정 결과는 revised-data analysis로
구분하고 원래 decision을 대체하지 않는다.

## 11. Time-based partition과 봉인

Random split을 primary로 쓰지 않는다. 사전 확정한 activation 시각부터 순차 chronological
RESEARCH → VALIDATION → FINAL_OOS block을 배치한다. 날짜는 현재 만들지 않는다. source scope,
수집 cadence, data quality 및 표본/precision plan으로 필요한 block length를 정하고 최초 confirmatory
수집 전에 calendar boundary/manifest hash를 freeze한다. 수익이 좋거나 event가 많아진 때를 보고
경계를 이동하지 않는다.

같은 candidate는 전체 cycle에서 처음 배정된 partition 하나만 가진다. 기준은 T_DISCOVERY
knowledge time이고 후속 discovery는 partition을 이동시키지 않는다. primary membership은
별도 필드다. 기존 Stage 2A의 자동 RESEARCH default는 미래 collector에서 사용 금지; approved
partition assignment service가 명시적 partition을 넘겨야 한다.

Training token의 label window/feature window가 다음 partition에 침범하지 않게 boundary buffer를
둔다. Buffer 최소 길이는 frozen maximum follow-up(24h)+최대 tolerance+label look-forward+
필요한 feature dependency span 중 시간 누출을 막는 보수적 합성 규칙으로 산정해 manifest에 고정한다.
경계 buffer token은 삭제하지 않고 BOUNDARY_EXCLUDED stratum으로 유지하며 확증 점수에서 제외한다.
동일 creator/campaign 연결이 보이면 사전 정의한 group contamination audit를 실시한다. 그룹 정의가
후일 확장돼도 partition을 편의상 재배정하지 않고 사전 정책대로 contaminated sensitivity panel을 표시한다.

FINAL_OOS는 별도 암호화 저장소/권한·접근 로그·key custodian으로 analyst에게 봉인할 계획이다.
현재 SQLite partition FK는 access seal이 아니다. 이 봉인과 접근감사 구현·검증 전 OOS 활성화 금지.
전략/분석/비용/표본 gate가 확정된 후 한 번의 승인된 unseal 평가를 수행한다. 열람 사실은 되돌릴 수
없다. 한번 본 OOS를 수정 전략의 새 OOS로 재사용하지 않는다.

## 12. Strategy freeze와 수정

향후 RESEARCH 후보는 feature 정의·as-of join·missing/stale handling·threshold·entry/exit·position
size·holding/latency·pool rule·quote size·slippage·fees·failure/expiry·parser/filter/pipeline/config·
social model/prompt/schema/tool parameters·dataset manifest/split·primary hypothesis/endpoint·
analysis code·seed·multiple-testing family·승인된 stopping rule을 모두 content hash로 고정한다.

VALIDATION은 사전 통과 기준에 대한 고정 후보 검증이다. 이를 본 뒤 결과에 영향을 줄 수 있는
feature/threshold/exit/cost/denominator/pool rule/누락 처리/label을 수정하면 새 research cycle이다.
이미 본 VALIDATION은 더 이상 그 수정의 untouched validation이 아니다. 추가 tuning은 RESEARCH로
명시하고 새 미래 holdout을 요구한다. 결과와 무관한 오탈자만 비분석 amendment로 허용한다.
Bug fix도 과거 출력에 영향을 주면 새 버전/전체 affected set 재처리와 오염 표시가 필요하다.
FINAL_OOS 공개 후 유리한 재분석을 primary로 바꾸지 않는다.

## 13. Multiple testing

모든 hypothesis/전략/feature family/threshold 조합/seed/cost scenario/endpoint/window 시도를
실행 전에 ledger에 예약한다. 실패·중단·결측·수동 시도도 남긴다. 한 grid job도 개별 조합 수를
숨기지 않는다. `number_of_tests_before`는 append-only registry에서 산출한 순번이며 직접 수정하지 않는다.
Independent strategy count와 actual evaluation count를 모두 기록한다.

Family와 primary endpoint를 결과 전에 정의한다. Confirmatory family는 family-wise error를
통제하는 Holm 절차를 기본 방법으로 설계하되 alpha와 유효한 p-value 생성법을 analysis plan에
먼저 확정한다. token/creator/time-cluster 의존성에 맞는 inference가 필요하며 단순 iid t-test를
자동 적용하지 않는다. Exploratory FDR 분석은 별도 등록하고 primary 확증과 구분한다.
최고 PNL 한 개 대신 모든 시도·불확실성·coverage·cost sensitivity·실패 사례를 보고한다.
수집 중 PNL을 반복 열람해 조기 종료하지 않는다. 순차 분석이 필요하면 별도 사전 alpha spending/
stopping plan을 고정한다.

## 14. Sample-size decision framework

7일/임의 token 수로 충분성을 선언하지 않는다. 사전 primary estimand, effect/precision 목표,
confidence/power 수준, event base-rate 불확실성, source overlap, 시간/creator cluster의 effective
sample size, missingness, 평가할 family 수를 근거로 precision/power 또는 simulation 계획을 세운다.
현재 숫자는 확정하지 않는다. 샘플 수 산정은 별도 승인된 연구 cycle의 protocol 업무이며 전략 탐색이 아니다.

전체 N 외에 independent creator/time clusters, source family별 수와 outage, rug-like taxonomy
사건 수, 비사건 follow-up, positive-return/negative-return 대표성, market regime 범위를 점검한다.
'successful token'은 primary horizon/return 정의와 경제적 성공 cutoff가 사전 고정된 뒤에만 사용하며
사후 상위 winner로 정의하지 않는다. Representative 여부는 관측 coverage에 한정하고 전체 시장으로
외삽하지 않는다. Regime은 사전 외생지표/달력 규칙으로 정의하고 성과를 보고 유리하게 나누지 않는다.

운영상 counts를 보는 담당자와 PNL 분석자를 분리할 계획이며 event별 adequacy check가 필요하면
독립 담당자가 outcome-blinded pass/fail만 전달한다. Rare event가 부족하면 INSUFFICIENT라고
보고하고 기준을 낮추지 않는다. 연장은 미리 정한 contingency가 있는 경우만 미래 block에 적용하며
기존 holdout boundary를 소급 변경하지 않는다.

## 15. Cost model

고정 notional/lot, input-output 통화, token transfer fee, AMM/aggregator fee, price impact,
slippage, network base fee, priority fee, 별도 명시된 tip, account/rent expense와 회수, quote expiry,
latency/requote, failed entry/exit/재시도 비용을 항목별로 저장한다. Quote의 net outAmount에 이미
포함된 비용과 외부 현금비용을 구분해 중복 차감하지 않는다. price impact와 slippage도 동일 비용의
두 이름으로 두 번 빼지 않는다. Fee 포함 semantics는 Phase 1 schema 확인까지 UNCONFIRMED다.
값을 모르면 0으로 쓰지 않고 cost-adjusted estimand를 BLOCKED로 둔다.

실행을 하지 않는 이번 단계에서는 실측 fill 비용이나 실패 확률을 만들지 않는다. 미래 paper 모델은
고정된 cost assumptions/sensitivity grid를 사전 등록하고 모든 시나리오를 보고한다. 최적의 비용
가정만 택하지 않는다. expired quote는 fill로 인정하지 않는다.

## 16. Ledger / pre-registration / amendments

`EXPERIMENT_LEDGER_SCHEMA.md`와 JSON template들이 규범 계약이다. 프로토콜, activation,
전략 freeze, dataset freeze, hypothesis 예약, run result, failure, decision, OOS access,
amendment를 append-only event로 보존한다. Result는 원래 예약을 수정하지 않고 참조한다.
Version, UTC registration timestamp, reason, previous hash, new content hash, affected future
cohort/window, retrospective impact, 승인 상태를 기록한다. 기존 snapshot/ledger event를 지우지 않는다.

현재 v1.0.0의 변경은 새로운 immutable version directory와 registry 행을 추가한다. Root의 읽기용
RESEARCH_PROTOCOL.md는 새 버전의 사본으로 바뀔 수 있지만 이전 version 파일과 registry line은
불변이다. Hash는 위변조 검출 보조이지 외부 공증·접근통제 자체는 아니다. 모든 retrospective 적용은
별도 revised/exploratory run으로 등록하고 원래 확증 결과를 대체하지 않는다.

## 17. Phase 2A 호환성과 Phase 2B gate

기존 2A DB/API/두 migration을 바꾸지 않는다. 기존 forward_observations는 **T_DECISION anchor**만
지원한다. discovery/baseline/eligible anchor는 설계만 완료했고 현재 테이블에 이름을 바꾸어 넣지 않는다.
다음 승인된 구현 단계에서 explicit anchor registry와 temporal availability provenance, source cohort,
quality state, pool selection lineage, append-only protocol/experiment ledger를 additive migration으로
구현해야 한다. 현재 documentation/JSON templates는 DB enforcement가 아니다.

Phase 2B prerequisites: 명시적 승인, 필요한 Phase 1 schema 검증, activation 필수 null 해소,
source coverage audit, 별도 calibration/confirmatory cohort 분리, split freeze, OOS seal,
사전등록·변경방지·시간정렬·누락·pool rule·forward-window 통합 테스트. 금지된 전략/threshold/PNL
최적화·Grok BUY/SELL·wallet/transaction·실거래로 범위를 확장하지 않는다.

STOP. PHASE 2A.5는 protocol 구조 freeze 단계이며 Phase 2B를 실행하지 않는다.
