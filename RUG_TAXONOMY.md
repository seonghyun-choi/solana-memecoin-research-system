# RUG_TAXONOMY — v1.0.0

목적: 사후 outcome annotation을 재현 가능한 측정 사건으로 분리한다.
사건의 의도/불법성/사기 여부를 판단하는 ground truth 분류기가 아니다.
모든 label은 taxonomy version, parser version, original snapshot ids, event interval,
first_available_at, computed_at, evaluator, scope, missingness와 uncertainty를 보존한다.
Threshold/persistence/baseline window가 null이면 label 상태는 UNRESOLVED다.

| event code | 측정 정의(사전 매개변수 필요) | 제외/혼동 방지 |
|---|---|---|
| LIQUIDITY_DEPLETION | 고정 pool의 비교 가능한 유동성이 등록 baseline 대비 alpha_L 이하로 감소하고 duration_L 동안 지속 | USD 가격 하락만으로 USD liquidity 감소 가능. reserve/token 수량과 인출 evidence 없이 liquidity removal이라 단정 금지 |
| VERIFIED_LIQUIDITY_REMOVAL | 승인된 chain event로 pool reserve/LP withdrawal 측정 | underlying event schema/chain coverage 아직 UNCONFIRMED |
| POOL_NOT_OBSERVED | 같은 pool의 유효 provider 조회에서 존재 확인 불가 | 검색 목록/인덱스 누락은 chain상 pool 소멸 아님; timeout은 API_FAILURE |
| POOL_CLOSURE_VERIFIED | 승인된 chain evidence로 실제 pool 폐쇄/비활성 확인 | provider 404 단독으로 확정 금지 |
| SELL_ROUTE_UNAVAILABLE | 고정 input mint/output mint/amount에서 승인된 성공 응답의 명시적 NO_ROUTE가 사전 persistence 조건 충족 | 특정 venue/router/size 범위만 의미. timeout/auth/rate-limit은 아님 |
| PRICE_COLLAPSE | 동일 pool·통화·유효 가격이 baseline 대비 alpha_P 이하이고 duration_P 지속 | stale, wrong quote direction, decimals, sparse trades, migrated pool로 인한 단절 구분 |
| PROVIDER_RUG_FLAG | RugCheck 등 provider가 나중에 명시적 flag를 반환 | provider claim이며 독립 ground truth 아님; 과거 feature로 역주입 금지 |
| AUTHORITY_CHANGE | mint/freeze/update authority의 검증된 상태 transition | authority 보유/변경 자체가 rug 증거 아님 |
| TOKEN_RESTRICTION_EVENT | 승인된 on-chain freeze/mint/transfer restriction 등 상태 사건 | event별 기술 효과만 기록; 악의 추론 금지 |
| SOCIAL_RUG_CLAIM | X/Grok/외부 작성자가 rug라고 주장 | 텍스트/모델/프롬프트·검색 timestamp와 출처 보존, objective label과 분리 |
| MIGRATION_OR_RECONFIGURATION | 유동성/거래가 successor venue로 이동한 검증 evidence | 기존 pool 결측을 피해 label로 오인하지 않도록 별도 상태 |
| DATA_OUTAGE | provider/수집 시스템 장애 또는 truncated coverage | token outcome이 아니며 threshold evidence로 사용 금지 |

사건 상태는 OBSERVED / NOT_OBSERVED_WITH_COVERAGE / UNKNOWN / CONFLICTED / UNRESOLVED.
NOT_OBSERVED_WITH_COVERAGE도 감시 밖 사건의 부재를 보장하지 않는다. 여러 code가 동시에 존재할 수 있다.
첫 event 시각을 정확히 알 수 없으면 last-known-normal ~ first-known-event의 interval-censored
onset으로 기록한다. 나중 조회시각을 정확한 발생시각으로 꾸미지 않는다.

## Composite binary outcome 제안과 활성화 gate

v1의 frozen 논리 구조는 `MEASURED_RUG_LIKE_EVENT`다. 다음 두 branch 중 하나가 확인될 때만
positive로 분류하도록 설계한다:

1. VERIFIED_LIQUIDITY_REMOVAL 또는 POOL_CLOSURE_VERIFIED **그리고** 동일 자산/등록 scope의
   persistent SELL_ROUTE_UNAVAILABLE.
2. 검증된 TOKEN_RESTRICTION_EVENT **그리고** 같은 자산/시간 창의 persistent SELL_ROUTE_UNAVAILABLE.

branch별 coincidence window, persistent failure 횟수/시간, quote size, coverage와 독립적인 provider
outage control, migration 예외가 activation manifest에서 먼저 확정되어야 한다. Chain 의미와 route
semantics는 Phase 1 및 별도 schema 검증이 필요하다. 그 전 binary label은 계산하지 않는다.
이 정의가 못 잡는 rug 유형은 있을 수 있다. Price collapse/US-dollar liquidity 감소/provider flag/social
claim만으로 이 composite를 positive로 만들지 않는다. 이러한 사건은 별도 outcome으로 보고한다.

Binary negative는 전체 label horizon의 필수 coverage를 충족하고 positive branch가 없을 때만
NOT_DETECTED_UNDER_PROTOCOL로 기록한다. 그렇지 않으면 UNKNOWN/CENSORED이며 false로 채우지 않는다.
Binary measured label과 '진짜 rug'를 동일시하지 않는다. 고의·법적 판단은 범위 밖이다.

## annotation 운영

- Outcome annotator는 baseline strategy PASS/SKIP/PNL·social verdict를 보지 않고 evidence를 검토한다.
- Rule 변경/분쟁 adjudication은 version과 reason을 남긴다. 원래 label은 지우지 않는다.
- Case-by-case로 예외 threshold를 바꾸지 않는다. UNKNOWN/CONFLICTED를 허용한다.
- Terminal economic loss는 별도 accounting label이다. NO_ROUTE나 rug-like label 하나로 원금 전액손실을 확정하지 않는다.
- Label feature leakage 금지: 미래 사건은 outcome 평가에만 사용하고 과거 decision feature에는 사용하지 않는다.
