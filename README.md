# 🪙 Solana Memecoin Research System

A research infrastructure project for building a **reproducible and bias-aware Solana memecoin analysis pipeline**.

The system is designed to capture what was known about a token at the time of discovery, preserve raw observations, and support reproducible offline analysis before any trading strategy is developed.

> **Project Status:** Research Infrastructure / Active Development  
> **Phase 0:** COMPLETE  
> **Phase 1:** LIVE VALIDATION PENDING  
> **Phase 2A:** COMPLETE  
> **Phase 2A.5:** COMPLETE  
> **Phase 2B:** NOT STARTED

---

## 🎯 Project Goal

Memecoin research is particularly vulnerable to retrospective bias.

If a researcher first looks at tokens that became successful or failed dramatically and then reconstructs their history, the resulting strategy can suffer from:

- Look-ahead bias
- Survivorship bias
- Selection bias
- Data leakage
- Post-hoc rule modification

This project takes a different approach:

> **Define the research protocol first, preserve what was observable at each point in time, and only then begin strategy research.**

The current repository therefore focuses on **data infrastructure, reproducibility, and research protocol design**, not trading.

---

## 🏗️ Current Architecture

```text
Candidate Discovery
        ↓
Discovery Event
        ↓
Raw Snapshot Capture
        ↓
Immutable Storage
        ↓
Versioned Parser
        ↓
Normalized Observations
        ↓
Offline Replay
        ↓
Research Decision
        ↓
Experiment Ledger
```

The architecture separates raw observations from later interpretation so that historical data can be replayed under known parser and configuration versions.

---

## 🔬 Research Protocol

Before analyzing token performance, Phase 2A.5 freezes the structural research protocol.

The protocol defines rules for:

- Candidate universe construction
- Discovery-source handling
- Observation timing
- Data provenance
- Snapshot preservation
- Missing-data treatment
- Experiment registration
- Forward outcome measurement
- Rug-risk taxonomy
- Protocol amendments
- Leakage prevention

Operational parameters without sufficient evidence remain unresolved rather than being assigned arbitrary defaults.

See:

- `RESEARCH_PROTOCOL.md`
- `PHASE2A5_COMPLETION_REPORT.md`
- `protocol/`

for the full protocol and amendment history.

---

## 🗄️ Data Foundation

Phase 2A implements the storage and replay infrastructure needed for later research.

Key components include:

### Immutable observations

Raw source responses can be stored before normalization so future parser changes do not silently rewrite historical observations.

### Versioned parsing

Parser versions are explicitly bound to implementations.

```text
Stored Raw Bytes
       ↓
Parser Version
       ↓
Normalized Observation
```

This makes it possible to reproduce how a historical observation was interpreted.

### Offline replay

The replay system is designed around:

```text
stored bytes
    ↓
registered parser
    ↓
immutable configuration
    ↓
research filters
    ↓
research decision
```

Replay does not silently fall back to live APIs.

### Experiment ledger

The project defines an experiment-ledger structure for recording future research decisions and preserving the history of experiments.

---

## 🧩 Core Components

The Python package is located in:

```text
qfoundation/
```

Important components include:

```text
qfoundation/
├── adapters.py
├── codec.py
├── db.py
├── errors.py
├── replay.py
├── store.py
├── time_model.py
└── migrations/
```

### `Store`

Handles research data such as:

- Candidate identity
- Discovery events
- Raw snapshot capture
- Immutable versions
- API error events
- Forward plans and events
- Database backup

### `ReplayEngine`

Reconstructs research decisions from previously stored observations rather than querying live providers during replay.

### Provider adapters

The project contains adapter boundaries for sources including:

- RugCheck
- DexScreener
- Jupiter
- XAI

Mappings that have not yet been validated against live API fixtures remain explicitly **UNCONFIRMED**.

This prevents guessed API schemas from becoming production assumptions.

---

## 🧪 Testing

The repository includes automated tests under:

```text
tests/
```

Example test command:

```bash
python -m unittest discover -s tests -v
```

Verification and regression artifacts are preserved under:

```text
reports/
```

---

## 🛠️ Technology

- Python 3.10+
- SQLite
- SQLite JSON1
- Python `unittest`
- Versioned database migrations
- Offline replay architecture

The current foundation intentionally has no external runtime dependency for provider fetching or trading execution.

---

## 📚 Documentation

This repository includes detailed engineering and research documentation.

| Document | Purpose |
|---|---|
| `ARCHITECTURE.md` | System architecture and invariants |
| `DATA_SCHEMA.md` | Database tables and fields |
| `DECISIONS.md` | Design decisions and known risks |
| `EXPERIMENT_LEDGER_SCHEMA.md` | Experiment tracking structure |
| `RESEARCH_PROTOCOL.md` | Frozen research methodology |
| `RUG_TAXONOMY.md` | Rug-risk classification framework |
| `PHASE2A_COMPLETION_REPORT.md` | Data-foundation completion report |
| `PHASE2A5_COMPLETION_REPORT.md` | Protocol-freeze completion report |
| `PROJECT_STATUS.md` | Current development status |
| `HANDOFF.md` | Continuation notes |

---

## 📍 Development Progress

### Phase 0 — COMPLETE

Initial project definition and research boundaries.

### Phase 1 — LIVE VALIDATION PENDING

Live provider fixtures and field mappings still require validation.

Unverified field locations are deliberately **not hard-coded as confirmed production mappings**.

### Phase 2A — COMPLETE

Data-foundation infrastructure implemented, including storage, migrations, replay, versioning, and tests.

### Phase 2A.5 — COMPLETE

Research protocol frozen before strategy exploration.

### Phase 2B — NOT STARTED

Strategy research and subsequent analysis have intentionally not started yet.

---

## 🤖 AI-Assisted Development

This project was developed using an AI-assisted engineering workflow for:

- Architecture design
- Research-protocol development
- Python implementation
- Database design
- Test generation and review
- Bias and leakage analysis
- Documentation
- Iterative validation

AI-generated proposals are treated as engineering inputs rather than automatically accepted results. Unverified assumptions are explicitly tracked instead of silently promoted to confirmed facts.

---

## ⚠️ Scope

This repository is currently a **research infrastructure project**, not a production trading bot.

It does not currently implement:

- Wallet management
- Transaction signing
- Automated token purchases
- Automated trading
- Production token scanning
- Live trading signals

The purpose of the current phases is to establish a reproducible research foundation before attempting to discover profitable strategies.

---

## 🔮 Next Steps

The next major milestone is **Phase 1 live validation**.

Once live provider schemas are validated, future work can proceed toward:

1. Confirmed provider mappings
2. Prospective candidate collection
3. Forward outcome tracking
4. Rug-risk analysis
5. Feature research
6. Strategy evaluation

Strategy rules will not be retroactively optimized using future information.
