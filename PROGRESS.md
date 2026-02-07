# 🏛️ PROJECT TITAN - PROGRESS TRACKER
## SOP Compiler Architecture Implementation

---

## 📅 SPRINT 1: THE FOUNDATION (Data & Rules)
Goal: Create a "Rigged" environment to prove the logic works.

### 1.1 The "Law" (sops.txt)
- [x] Create sops.txt with three conflict-prone rules
- [x] Rule A: Liquidation (Days > 180)
- [x] Rule B: Low Margin Warning (Profit < $5)
- [x] Rule C: VIP Exception (Days > 180 AND Profit > $20)

### 1.2 The "Test Subject" (mock_data.csv)
- [x] Generate mock_data.csv with 100 rows
- [x] Schema: Item_Name, Price, Days_in_Warehouse, Profit_Per_Item
- [x] Rows 0-80: Normal data (Age < 100, Profit > $10)
- [x] Rows 81-90: Trigger Liquidation (Age = 200, Profit = $4)
- [x] Rows 91-95: Trigger Review (Age = 50, Profit = $2)
- [x] Rows 96-100: Trigger VIP Exception (Age = 250, Profit = $25)

---

## 📅 SPRINT 2: THE COMPILER SETUP (Inputs)
Goal: Prepare the context so the Coder Agent cannot fail.

### 2.1 The "Context Stuffer" (Script)
- [x] Create src/context_loader.py
- [x] Load CSV with Pandas and format schema
- [x] Return formatted context with headers + first 3 rows
- [x] Function: get_csv_context(file_path: str) -> str

### 2.2 The "Rule Extractor" (Agent)
- [x] Create src/rule_extractor.py
- [x] Build Pydantic models: Rule, RuleSet
- [x] Create LangGraph node for rule extraction
- [x] Parse sops.txt using gpt-oss-120b (with fallback to manual parsing)
- [x] Validate output format with Pydantic
- [x] Extracted 3 rules: Liquidation, Low Margin Warning, VIP Exception

---

## 📅 SPRINT 3: THE ENGINE (Code Generation Loop)
Goal: Build the "Self-Healing" Python Generator.

### 3.1 The "Architect" (Agent)
- [x] Build Architect agent (src/architect.py) with Cerebras gpt-oss-120b
- [x] Define system prompt: Senior Python Data Engineer
- [x] Implement constraints: Pandas/Numpy only, vectorized ops
- [x] Generate `apply_filters(df)` function
- [x] Fix code function for self-healing retries
- [x] **REFACTORED: Generalist prompt** (no hardcoded rules — LLM reasons from any rules JSON)

### 3.2 The "Sandbox Loop" (The Magic)
- [x] Build engine loop (src/engine_loop.py) with subprocess execution
- [x] Implement code execution with subprocess.run
- [x] Add error handling + retry logic (max 3 attempts)
- [x] Validation: Check for PROCESS_COMPLETE marker
- [x] **Added post-execution validation node** (checks Status column, row counts, expected distributions)
- [x] Save verified code to verified_filter.py

### 3.3 Multi-Scenario Testing (Hybrid Approach)
- [x] Scenario 1: Titan Warehouse SOP — ✅ PASSED (attempt 1)
- [x] Scenario 2: Electronics Pricing Tiers — ✅ PASSED (attempt 1)
- [x] Scenario 3: Order Fulfillment Priority — ✅ PASSED (attempt 1)
- [x] **Overall: 3/3 scenarios, 100% success rate, all first-attempt**

---

## 📅 SPRINT 4: THE VOICE (Runtime & Reporting)
Goal: The "Morning Brief" Dashboard.

### 4.1 The Runtime (src/runtime.py)
- [x] Load mock_data.csv (full 100 rows)
- [x] Execute verified_filter.py (dynamic import via importlib)
- [x] Calculate violations count by status + trapped capital + margin risk
- [x] Generate violations.csv output (20 violations)
- [x] Generate summary_stats.json

### 4.2 The "Reporter" Agent (src/reporter.py)
- [x] Build Reporter agent (LangGraph node + Cerebras gpt-oss-120b)
- [x] Define "Vigilant CFO" persona
- [x] Input: summary_stats.json + top 5 violations
- [x] Output: Markdown War Room Brief (war_room_brief.md)
- [x] Format: 🚨 CRITICAL ACTIONS / ⚠️ MARGIN WATCH / ✅ WINS

### 4.3 The Dashboard (app.py)
- [x] Create app.py (Streamlit)
- [x] Sidebar: Config panel + "Run SOP Compiler" button + live metrics
- [x] Toggle: Raw Data view with status filter + bar chart
- [x] Toggle: War Room Brief (Markdown) + color-coded violations table
- [x] Action buttons: Approve Liquidation / Send to Slack / Download Report

---

## 🔧 TECH STACK
- **Orchestration**: LangGraph (State Machine)
- **LLM**: Cerebras gpt-oss-120b (120B MoE, ~3,000 t/s)
- **Code Execution**: E2B Sandbox
- **Data Validation**: Pydantic
- **UI**: Streamlit
- **Data Processing**: Pandas + NumPy

---

## 📊 COMPLETION METRICS
- **Sprint 1**: 6/6 ✅ (100%)
- **Sprint 2**: 4/4 ✅ (100%)
- **Sprint 3**: 10/10 ✅ (100%) — generalist prompt + validation + 3/3 multi-domain scenarios
- **Sprint 4**: 15/15 ✅ (100%) — runtime + reporter agent + Streamlit dashboard
- **Overall**: 35/35 (100%) 🎉

---

## 📝 NOTES
- Virtual env: `/home/zohir/learning-langraph/venv/`
- Dependencies: pandas, numpy, langgraph, pydantic, requests

### Project Structure
```
learning-langraph/
├── app.py                  # Streamlit dashboard (Sprint 4)
├── data/                   # Input data & rules
│   ├── sops.txt            # Natural language SOP rules
│   └── mock_data.csv       # Generated test dataset (100 rows)
├── scripts/                # Standalone utility scripts
│   └── generate_mock_data.py
├── src/                    # Core engine modules
│   ├── context_loader.py   # CSV schema extractor (no LLM)
│   ├── rule_extractor.py   # LangGraph + Cerebras rule parser
│   ├── architect.py        # Generalist code generator (Cerebras)
│   ├── engine_loop.py      # Self-healing execution + validation loop
│   ├── runtime.py          # Runtime pipeline (violations + stats)
│   └── reporter.py         # War Room Brief generator (LangGraph + Cerebras)
├── tests/                  # Test harnesses
│   ├── test_sprint_2.py    # Context loader + rule extractor tests
│   └── test_sprint_3.py    # Multi-scenario engine tests (3 domains)
├── outputs/                # All generated artifacts (gitignored)
│   ├── context.txt, rules.json, filtered_results.csv
│   ├── generated_filter.py, verified_filter.py
│   ├── violations.csv, summary_stats.json
│   ├── war_room_brief.md
│   └── test scenario artifacts
├── archive/                # Legacy/experimental code
├── project_spec.txt        # Master architecture spec
├── PROGRESS.md             # This file
└── config.yaml
```
