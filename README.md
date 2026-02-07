<div align="center">

# ⚙️ Agentic SOP Compiler
### Deterministic Rule Enforcement via Code Generation

*An autonomous engine that translates natural-language Standard Operating Procedures*
*into verified, executable Python code — then runs it at scale for $0 per execution.*

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Cerebras](https://img.shields.io/badge/LLM-Cerebras%20gpt--oss--120b-purple.svg)](https://cerebras.ai)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)

</div>

---

## The Problem: The SOP Execution Gap

Every enterprise has Standard Operating Procedures. Compliance rules. Business logic documented in shared drives, wikis, and PDFs. The rules exist. **The execution doesn't.**

An operations team managing 10,000+ records cannot manually check each one against 15 overlapping rules every morning. The result:

- 💰 **Trapped Capital** — Non-compliant assets sit unactioned, silently accumulating carrying costs.
- 📉 **Margin Erosion** — Low-performing items go unnoticed until P&L impact is irreversible.
- ⚡ **Decision Lag** — By the time a human catches a violation, the window to act has closed.

The typical "AI solution" is a chatbot that reads rows one-by-one, burning tokens and hallucinating column names. That's not a solution — it's an O(n) token liability that scales with your data.

---

## The Solution: Compile, Don't Chat

The SOP Compiler doesn't *use* AI to read your data. It uses AI to **write the code that reads your data.**

**One inference to compile. Zero tokens to execute. Deterministic output.**

```
┌─────────────────────────────────────────────────────────────────────┐
│                  AGENTIC SOP COMPILER — PIPELINE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   📄 sops.txt              📊 dataset.csv                          │
│   (Plain-English Rules)     (Any Tabular Schema)                    │
│        │                         │                                  │
│        ▼                         ▼                                  │
│   ┌──────────┐          ┌────────────────┐                         │
│   │  Rule     │          │  Context       │                         │
│   │ Extractor │          │  Loader        │                         │
│   │ (LangGraph│          │  (Pure Pandas) │                         │
│   │  + LLM)  │          │                │                         │
│   └────┬─────┘          └───────┬────────┘                         │
│        │  rules.json            │  context.txt                     │
│        └──────────┬─────────────┘                                  │
│                   ▼                                                 │
│          ┌──────────────┐                                          │
│          │  Architect    │  ← Generalist Prompt                    │
│          │  Agent        │    (Domain-Agnostic)                    │
│          │  (Cerebras)   │                                         │
│          └──────┬───────┘                                          │
│                 │  generated_filter.py                              │
│                 ▼                                                   │
│     ┌─────────────────────┐                                        │
│     │  Self-Healing Loop   │  ← Execute → Validate → Retry        │
│     │  (Subprocess Sandbox)│    Max 3 attempts                     │
│     └──────────┬──────────┘                                        │
│                │  verified_filter.py ✅                             │
│                ▼                                                   │
│       ┌────────────────┐                                           │
│       │  Runtime        │  → violations.csv                        │
│       │  Pipeline       │  → summary_stats.json                    │
│       └───────┬────────┘                                           │
│               ▼                                                    │
│      ┌─────────────────┐                                           │
│      │  Reporter Agent  │  → executive_report.md                   │
│      │  (Executive      │                                          │
│      │   Compliance     │                                          │
│      │   Officer)       │                                          │
│      └───────┬─────────┘                                           │
│              ▼                                                     │
│     ┌──────────────────┐                                           │
│     │  Streamlit        │  Raw Data ⟷ Executive Action Report      │
│     │  Dashboard        │  + Live Agent Terminal                   │
│     └──────────────────┘                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Three Core Innovations

### 1. Self-Healing Sandbox Loop

The engine doesn't just generate code — it **proves the code works** before promoting it to production.

```
Architect Agent generates code
        │
        ▼
   Execute in isolated subprocess (30s timeout)
        │
   ┌────┴────┐
   │ Pass?   │
   ├─ YES ───┤──→ Validate output (schema integrity, row counts, distributions)
   │         │         │
   │         │    ┌────┴────┐
   │         │    │ Valid?  │
   │         │    ├─ YES ───┤──→ ✅ Promote to verified_filter.py
   │         │    └─ NO ────┘──→ Feed validation error → Architect → Retry
   └─ NO ────┘──→ Feed stderr → Architect → Retry (max 3)
```

**Result:** 3/3 cross-domain scenarios passed on first attempt. Zero retries needed.

### 2. Compile-Time vs. Run-Time Logic

| Phase | What Happens | Tokens Used | Cost |
|:---|:---|:---|:---|
| **Compile-Time** | LLM reads SOPs + schema, writes a Pandas script | ~2,000 (one-time) | ¢ |
| **Run-Time** | Pure Python executes on 10K+ records | **0** | **$0** |

Traditional approaches burn tokens *per row, per rule, per run.* The SOP Compiler eliminates run-time token spend entirely.

### 3. Deterministic Execution Guarantee

After compilation, the generated code is:
- **Tested** in a sandboxed subprocess before promotion.
- **Validated** against expected output distributions.
- **Frozen** — the same input always produces the same output. No temperature, no drift, no hallucinations.

The LLM is used for *judgment* (writing the code). Python handles *execution* (running it). Clean separation.

---

## Cross-Domain Validation

The engine is **domain-agnostic.** No business logic is hardcoded in the prompt. The Architect reads any rules JSON and reasons about any schema:

| Scenario | Domain | Rules | Result |
|:---|:---|:---|:---|
| Inventory Compliance | Warehouse Ops | Asset Disposition / Margin Review / Exception Override | ✅ Attempt 1 |
| Product Pricing Tiers | E-Commerce | Budget / Premium / Clearance Override | ✅ Attempt 1 |
| Order Fulfillment Priority | Logistics | Urgent / Priority / VIP Rush Override | ✅ Attempt 1 |

**100% first-attempt success rate across 3 completely unrelated industries.**

---

## Demo Results (Inventory Compliance Scenario)

Running the compiler against 100 inventory records with 3 overlapping rules:

| Metric | Value |
|:---|:---|
| 🚨 Non-Compliant Assets | 10 (flagged for disposition) |
| 💰 Trapped Capital Identified | **$500** |
| ⚠️ Margin-Risk Items | 5 (under $5 unit profit) |
| ✅ High-Value Assets Preserved | 5 ($375 in profit protected) |
| ⏱️ Execution Time | **< 100ms** (post-compilation) |
| 🔤 Run-Time Token Cost | **$0.00** |
| 📊 Violation Rate | 20% of records require action |

At 10,000 records: same execution time, same $0 token cost.

---

## Tech Stack

| Layer | Technology | Design Rationale |
|:---|:---|:---|
| **Orchestration** | LangGraph (StateGraph) | Explicit state machines per agent. No implicit chain-of-thought. Each node has typed I/O. |
| **LLM** | Cerebras `gpt-oss-120b` | 120B MoE reasoning model at ~3,000 t/s. Fast enough for real-time compile loops. |
| **Structured Extraction** | Pydantic v2 | Type-safe rule models (`Rule`, `RuleSet`) with fallback parsers for robustness. |
| **Code Sandbox** | `subprocess.run` | Isolated execution. 30s timeout. No `exec()` risks. Mimics E2B in local mode. |
| **Output Validation** | Custom validation node | Checks: column existence, NaN detection, row count preservation, distribution matching. |
| **Data Processing** | Pandas + NumPy | Vectorized operations only. Generated code uses `df.loc[mask]` — no row-level loops. |
| **Reporting** | LangGraph + Cerebras | Executive Compliance Officer persona generates structured Markdown reports. |
| **Dashboard** | Streamlit | Dark-mode UI with live agent terminal, metric cards, and simulation toggle. |

---

## Project Structure

```
agentic-sop-compiler/
├── app.py                      # Streamlit dashboard (dark mode, agent terminal)
├── data/
│   ├── sops.txt                # Natural language SOP rules (configurable)
│   └── mock_data.csv           # Test dataset (100 rows, rigged with known violations)
├── scripts/
│   └── generate_mock_data.py   # Data generator with embedded compliance triggers
├── src/
│   ├── context_loader.py       # CSV schema extractor (no LLM — pure Pandas)
│   ├── rule_extractor.py       # LangGraph node → Pydantic rule models
│   ├── architect.py            # Generalist code generator (domain-agnostic prompt)
│   ├── engine_loop.py          # Self-healing compile → execute → validate loop
│   ├── runtime.py              # Runtime pipeline (violations + summary stats)
│   └── reporter.py             # Executive Action Report generator (LangGraph)
├── tests/
│   ├── test_sprint_2.py        # Context + rule extraction tests
│   └── test_sprint_3.py        # Cross-domain engine tests (3/3 ✅)
├── outputs/                    # Generated artifacts (gitignored)
│   ├── verified_filter.py      # Promoted, tested code
│   ├── violations.csv          # Non-compliant records
│   ├── summary_stats.json      # Aggregated metrics
│   └── executive_report.md     # LLM-generated action report
└── PROGRESS.md                 # Sprint tracking (35/35 ✅)
```

---

## How to Run

### Prerequisites
- Python 3.12+
- [Cerebras API key](https://cloud.cerebras.ai/) → set as `CEREBRAS_API_KEY` in `.env`

### Setup

```bash
git clone <repo-url> && cd agentic-sop-compiler

python -m venv venv && source venv/bin/activate

pip install pandas numpy langgraph pydantic requests streamlit tabulate

echo "CEREBRAS_API_KEY=your_key_here" > .env
```

### Run the Full Pipeline

```bash
source venv/bin/activate && set -a && source .env && set +a

# 1. Generate test data (rigged with known violations)
python scripts/generate_mock_data.py

# 2. Extract schema context + parse SOP rules
python src/context_loader.py
python src/rule_extractor.py

# 3. Compile SOPs → Python (self-healing loop)
python src/engine_loop.py

# 4. Execute runtime pipeline + generate report
python src/runtime.py
python src/reporter.py

# 5. Launch dashboard
streamlit run app.py
```

### One-Click (via Dashboard)

```bash
streamlit run app.py
# Click "▶ Run SOP Compiler" in the sidebar — executes the full pipeline.
```

---

## Architecture: Why "Compile" Instead of "Chat"?

| Approach | Tokens per 10K Records | Latency | Hallucination Risk | Cost per Run |
|:---|:---|:---|:---|:---|
| ❌ LLM reads each row | ~5M tokens | Minutes | High | $$$$ |
| ❌ RAG + row-by-row | ~2M tokens | 30–60s | Medium | $$ |
| ✅ **SOP Compiler** | **~2K (one-time)** | **< 100ms** | **Zero (code is tested)** | **$0** |

> *"Don't send your data to the LLM. Send your rules to the LLM, get code back, and run the code on your data."*

The SOP Compiler turns an **O(n) token problem** into an **O(1) compilation step.**

---

## Configuring for Your Domain

The engine is a blank slate. To apply it to any industry:

1. **Write your SOPs** in plain English → `data/sops.txt`
2. **Drop your dataset** (any CSV) → `data/mock_data.csv`
3. **Run the compiler** → It reads your rules, reads your schema, writes the code, tests it, and executes.

No prompt changes. No code changes. The Architect Agent reasons from whatever you give it.

---

<div align="center">

**Agentic SOP Compiler** · LangGraph · Cerebras · Pydantic · Streamlit

*"Don't read the data. Write the code that reads the data."*

</div>
