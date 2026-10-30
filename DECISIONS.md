# Decisions and known risks

| ID | Decision | Reason / limit |
|---|---|---|
| D01 | SQLite, standard-library Python | Portable offline foundation, no server or dependencies required. Single writer limits future throughput. |
| D02 | Raw bytes in DB BLOB with metadata | Atomic evidence storage, easy online backup; large payloads increase DB size. No external blob store yet. |
| D03 | Append-only triggers on evidence and versions | Reject accidental updates/deletes and REPLACE using package connection. DB-owner privileges can drop triggers; not WORM storage. |
| D04 | SHA-256 over exact bytes | Detect payload changes; no authenticity signature or proof the provider actually served supplied bytes. |
| D05 | Candidate ≠ discovery | One mint identity can have many source events/times. Source event keys must be supplied consistently. |
| D06 | One immutable candidate partition | Prevent obvious candidate leakage. Dataset split boundaries, embargoes and multiple split experiments are not implemented. |
| D07 | UTC integer microseconds | Precise ordering; caller must declare timezone. Direct SQL writers can still supply wrong units, so Store is the supported ingestion API. |
| D08 | No provider field mappings yet | Phase 1 remains LIVE_VALIDATION_PENDING; observation data_json is extensible infrastructure, not a confirmed market/social schema. |
| D09 | Version-pinned deterministic replay identity | New parser/config/pipeline yields new results. Class hash alone is insufficient; foundation/runtime fingerprint is also pinned. External parser dependencies and state must be separately archived. |
| D10 | FAIL preserves CONTINUE | Filter is a research label, not termination logic. No strategy or trade execution semantics. |
| D11 | Decision-time forward anchor | Explicit stable baseline for 10m–24h infrastructure. If study protocol later chooses first discovery, introduce a new pipeline/schema version. |
| D12 | Append forward events | Corrections do not erase history. Which record is preferred and late-arrival tolerance remain future protocol decisions. |
| D13 | Two checksummed forward-only migrations | No silent edits/downgrades. Backup/restore is rollback strategy; later changes require a new migration. |
| D14 | Errors classify evidence, not inferred trading feasibility | HTTP 401/403/429/5xx take precedence over an explicit NO_ROUTE flag. Retryable is metadata only; no automatic retries. |
| D15 | Known-secret rejection instead of redacting raw | Rejected captures do not compromise byte-level truth. No headers accepted; endpoint auth/query secrets rejected. Unknown secrets inside arbitrary body/metadata cannot be reliably detected. Upstream secret-safe capture is still required. |

Technical debt / risks:

- This is a new coherent foundation based on the latest explicit requirements. Prior
  unseen HANDOFF/source files were not merged, and Phase 0 historical artifacts are
  not reconstructed. The current user instruction is the scope authority.
- JSON observations do not yet have provider-validated typed fields or domain range
  checks. No risk score, LP lock, holder, quote or social mapping is inferred.
- Synthetic test parsers deliberately use `risk_score` with 55/40 and 60 to test FAIL,
  PASS and version separation; those numbers are not recommended trading thresholds.
- Parser implementations are trusted local code, not sandboxed. The provided adapters
  and engine contain no network calls; arbitrary future plugins could add effects.
  Future integration should enforce capability isolation and archive dependencies.
- Snapshot provenance is caller-declared; `live_capture` requires HTTP status but is
  not independently authenticated. Imported evidence must retain its actual provenance.
- SQL constraints guard shape and lineage, not all market semantics. JSON optional
  metadata may contain private content if the caller supplies it; no secret is loaded
  automatically and no .env is packaged.
- Schema version row checksums protect against accidental migration drift. They do not
  defend against a privileged attacker rewriting DB history and source together.
- FINAL_OOS membership isolation is implemented, but access control, embargo windows,
  freeze protocol and prevention of human/model tuning on OOS data are not.
- Observation timestamps currently represent capture time. Market event time, token
  creation time and discovery time must not be conflated in Phase 2B.
- WAL backup must use Store.backup/SQLite backup, not copy only the main DB while
  writers are active. Included DB was closed before packaging.
- Migrations, tests and replay are verified in the current Linux/Python/SQLite runtime.
  No Windows/macOS run, long soak test, load test or production disaster-recovery test.
- Future concurrency beyond one SQLite writer may need ingestion queues or another
  database. No collectors/queues/schedulers were built under Phase 2A.

## Phase 2A.5 decisions

D16: Freeze methodology now, leave unsupported operational numbers explicitly null.
Structural freeze is complete; activation remains blocked rather than inventing dates,
TTL/tolerance, sample counts or economic cost values.

D17: Keep 2A source/migrations/DB unchanged. Documents, immutable protocol snapshots,
JSON templates and verification script provide a pre-registration artifact, not a
collector or security boundary. Proposed DB changes await approved additive migration.

D18: First known discovery is not retrospectively corrected to an older source timestamp.
Freeze cohort identity separately from source-event times and baseline availability.

D19: Fix baseline primary pool for a return series. Retain alternative pools without
switching to favorable survivors. Screen, quote-indicative and paper outcomes remain separate.

D20: OOS must be sealed outside analysts' read access before activation; current SQLite
partition checks cannot provide this protection. Event hash history is not external attestation.

D21: Future reviewer/annotator needs a versioned outage-controlled technical rug-like
label, not social/LLM ground truth. Rare or uncertain events may remain UNKNOWN.

Known remaining risks: source feed completeness, indexed-feed survival bias, MNAR
missing outcomes, provider clock/cache semantics, manipulable pool metrics, baseline
availability/immortal-time selection, correlated creator/time clusters, retrospective
bugfix leakage, and unimplemented access/ledger enforcement. Current protocol addresses
how to expose/control these risks; it does not claim to eliminate them.
