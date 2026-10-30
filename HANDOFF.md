# Handoff — Phase 2A.5 research protocol freeze

PHASE 0 = COMPLETE
PHASE 1 = LIVE_VALIDATION_PENDING
PHASE 2A = COMPLETE
PHASE 2A.5 = COMPLETE
PHASE 2B = NOT STARTED

Current authority: latest user approved Phase 2A and requested only Phase 2A.5.
Do not retry Phase 1, request current PC execution, collect data, search strategies,
optimize thresholds/PNL, build Grok BUY/SELL or begin Phase 2B.

Read RESEARCH_PROTOCOL.md, RUG_TAXONOMY.md, EXPERIMENT_LEDGER_SCHEMA.md and the immutable
v1.0.0 copies. protocol/REGISTRY.jsonl records registration timestamp and hashes.
protocol/templates contains blank schemas, not actual experiment registrations or results.

Status distinction: STRUCTURAL_RULES_FROZEN / ACTIVATION_BLOCKED. TTL/tolerance/dates/
costs/notional/cadence/statistical planning values are not guessed. Resolving a pending
value requires a new timestamped activation/amendment revision before relevant data
is seen. Preserve old files and registry lines; never rewrite v1.0.0 after results.

## Phase 2B prerequisites — none executed here

1. Explicit user approval for Phase 2B and precise authorized implementation scope.
2. Phase 1 live contracts/clock/cache/fee semantics verified when the user later resumes.
3. Outcome-independent source registry and scope; independent non-ranked source-family
   coverage audited; social/manual/ranked strata separated; capacity/gap policy frozen.
4. Activation manifest required values complete, justified and approved before collection.
5. Freeze chronological partitions/buffers, immutable dataset protocol and OOS access seal.
6. Add backward-compatible anchor/availability/quality/pool/ledger storage and checks;
   keep existing decision-anchored forward records semantically unchanged.
7. Validate as-of joins, no retrospective T0/backfill, fixed pool selection, retry/window,
   missingness, protocol-history integrity and experiment counts with synthetic tests.
8. Separate operational calibration data from confirmatory cohort; no prospective data
   collection or calibration is authorized by this handoff itself.

Phase 1 dependencies: actual provider field paths/nullability, token/pool creation vs
cache timestamp semantics, complete pool enumeration/direction/units, quote size/fees/
expiry/route errors, xAI usage/output stability and social availability provenance.
Independent chain-event schemas for rug labels need separate validation too; do not
pretend the four Phase 1 APIs establish all causal/chain facts.

The old Phase 2A code/DB/migrations remain unchanged and archived documentation is in
archive/phase2a_documentation. The Stage 2A historical completion report stays historical.
Run protocol/verify_freeze.py later to check artifact hashes; it never activates collection.
Future pipeline fingerprints must be newly registered if runtime code is changed.

STOP. PHASE 2A.5 complete; Phase 2B not started and not authorized.
