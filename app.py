"""
app.py
Agentic SOP Compiler — Enterprise Dashboard.
Dark-mode UI with live agent terminal, metric cards, and simulation toggle.
"""

import os
import sys
import json
import time
import io
import contextlib
import streamlit as st
import pandas as pd

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.runtime import run_pipeline
from src.reporter import generate_war_room_brief

# ── Paths ────────────────────────────────────────────────────────────────────

DATA_CSV = "data/mock_data.csv"
VIOLATIONS_CSV = "outputs/violations.csv"
SUMMARY_JSON = "outputs/summary_stats.json"
REPORT_MD = "outputs/executive_report.md"
FILTERED_CSV = "outputs/filtered_results.csv"


# ── Dark Mode CSS ────────────────────────────────────────────────────────────

DARK_CSS = """
<style>
    /* ── Global dark overrides ───────────────────────────────────── */
    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
    }

    /* ── Metric cards ────────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #58a6ff;
    }
    .metric-card .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 4px 0;
        font-family: 'SF Mono', 'Cascadia Code', monospace;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #8b949e;
    }
    .metric-card .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 4px;
    }
    .metric-red .metric-value { color: #f85149; }
    .metric-yellow .metric-value { color: #d29922; }
    .metric-green .metric-value { color: #3fb950; }
    .metric-blue .metric-value { color: #58a6ff; }

    /* ── Agent terminal ──────────────────────────────────────────── */
    .agent-terminal {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', monospace;
        font-size: 0.78rem;
        line-height: 1.6;
        max-height: 400px;
        overflow-y: auto;
        color: #8b949e;
    }
    .agent-terminal .log-step { color: #58a6ff; }
    .agent-terminal .log-ok { color: #3fb950; }
    .agent-terminal .log-warn { color: #d29922; }
    .agent-terminal .log-err { color: #f85149; }
    .agent-terminal .log-dim { color: #484f58; }

    /* ── Report card ─────────────────────────────────────────────── */
    .report-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 32px;
        margin: 8px 0;
    }

    /* ── Section headers ─────────────────────────────────────────── */
    .section-header {
        background: linear-gradient(90deg, #161b22 0%, transparent 100%);
        border-left: 3px solid #58a6ff;
        padding: 8px 16px;
        margin: 16px 0 8px 0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8b949e;
    }

    /* ── Status pills (for dataframe) ────────────────────────────── */
    .status-critical { background: #f8514922; color: #f85149; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
    .status-warning { background: #d2992222; color: #d29922; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
    .status-success { background: #3fb95022; color: #3fb950; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }

    /* ── Sidebar tweaks ──────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #21262d;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        border: 1px solid #238636;
        font-weight: 600;
    }

    /* ── Divider ─────────────────────────────────────────────────── */
    hr {
        border-color: #21262d;
    }
</style>
"""


# ── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Agentic SOP Compiler",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(DARK_CSS, unsafe_allow_html=True)


# ── Helper: Metric Card ─────────────────────────────────────────────────────

def metric_card(icon: str, value: str, label: str, color_class: str = "metric-blue") -> str:
    return f"""
    <div class="metric-card {color_class}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


# ── Helper: Agent Terminal Log ───────────────────────────────────────────────

def render_agent_terminal(logs: list[str]) -> str:
    """Render a list of log lines as a styled terminal block."""
    lines_html = []
    for line in logs:
        if line.startswith("[OK]"):
            cls = "log-ok"
        elif line.startswith("[WARN]"):
            cls = "log-warn"
        elif line.startswith("[ERR]"):
            cls = "log-err"
        elif line.startswith("[STEP]") or line.startswith("[>>]"):
            cls = "log-step"
        else:
            cls = "log-dim"
        lines_html.append(f'<span class="{cls}">{line}</span>')
    
    content = "<br>".join(lines_html)
    return f'<div class="agent-terminal">{content}</div>'


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Agentic SOP Compiler")
    st.caption("Deterministic Rule Enforcement · v1.0")
    st.divider()
    
    st.markdown('<div class="section-header">Pipeline Control</div>', unsafe_allow_html=True)
    
    run_clicked = st.button("▶ Run SOP Compiler", type="primary", use_container_width=True)
    
    if run_clicked:
        logs = []
        log_container = st.empty()
        
        def add_log(msg: str):
            logs.append(msg)
            log_container.markdown(render_agent_terminal(logs[-12:]), unsafe_allow_html=True)
        
        try:
            add_log("[STEP] Initializing pipeline...")
            add_log(f"[>>] Loading data from {DATA_CSV}")
            time.sleep(0.3)
            
            # Capture runtime output
            add_log("[STEP] Executing runtime pipeline...")
            add_log("[>>] Dynamically importing verified_filter.py")
            
            stdout_capture = io.StringIO()
            with contextlib.redirect_stdout(stdout_capture):
                summary = run_pipeline()
            
            runtime_output = stdout_capture.getvalue()
            for line in runtime_output.strip().split("\n"):
                stripped = line.strip()
                if stripped and not stripped.startswith("="):
                    if "✅" in stripped or "PASS" in stripped:
                        add_log(f"[OK] {stripped}")
                    elif "❌" in stripped or "FAIL" in stripped:
                        add_log(f"[ERR] {stripped}")
                    elif "💾" in stripped or "📂" in stripped or "⚡" in stripped:
                        add_log(f"[STEP] {stripped}")
                    else:
                        add_log(f"     {stripped}")
            
            st.session_state["pipeline_run"] = True
            st.session_state["summary"] = summary
            
            add_log("[STEP] Generating Executive Action Report...")
            add_log("[>>] Reporter Agent: Executive Compliance Officer persona")
            
            stdout_capture2 = io.StringIO()
            with contextlib.redirect_stdout(stdout_capture2):
                report = generate_war_room_brief()
            
            if report:
                st.session_state["report"] = report
                add_log("[OK] Report generated successfully")
                add_log(f"[OK] Pipeline complete — {summary['total_violations']} violations detected")
            else:
                add_log("[WARN] Report generation failed. Stats available.")
            
        except Exception as e:
            add_log(f"[ERR] Pipeline error: {str(e)}")
    
    st.divider()
    
    # Live metric cards in sidebar
    st.markdown('<div class="section-header">Live Metrics</div>', unsafe_allow_html=True)
    
    if os.path.exists(SUMMARY_JSON):
        with open(SUMMARY_JSON, "r") as f:
            stats = json.load(f)
        
        st.markdown(
            metric_card("📊", str(stats["total_items"]), "Records Scanned"),
            unsafe_allow_html=True,
        )
        st.markdown(
            metric_card("🚨", str(stats["liquidation"]["count"]), "Non-Compliant", "metric-red"),
            unsafe_allow_html=True,
        )
        st.markdown(
            metric_card("✅", str(stats["vip_keep"]["count"]), "Assets Preserved", "metric-green"),
            unsafe_allow_html=True,
        )
        st.markdown(
            metric_card("💰", f"${stats['liquidation']['trapped_capital']:,.0f}", "Trapped Capital", "metric-yellow"),
            unsafe_allow_html=True,
        )
    else:
        st.info("Run the compiler to see metrics.")


# ── Main Screen ──────────────────────────────────────────────────────────────

st.markdown("# ⚙️ Agentic SOP Compiler")
st.caption("Deterministic Rule Enforcement via Code Generation · Powered by LangGraph + Cerebras gpt-oss-120b")

# Top metric bar (if stats exist)
if os.path.exists(SUMMARY_JSON):
    with open(SUMMARY_JSON, "r") as f:
        stats = json.load(f)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(metric_card("📊", str(stats["total_items"]), "Total Records"), unsafe_allow_html=True)
    c2.markdown(metric_card("🚨", str(stats["liquidation"]["count"]), "Flagged", "metric-red"), unsafe_allow_html=True)
    c3.markdown(metric_card("⚠️", str(stats["review"]["count"]), "Under Review", "metric-yellow"), unsafe_allow_html=True)
    c4.markdown(metric_card("✅", str(stats["vip_keep"]["count"]), "Preserved", "metric-green"), unsafe_allow_html=True)
    c5.markdown(metric_card("📈", f"{stats['violation_rate']}%", "Violation Rate", "metric-blue"), unsafe_allow_html=True)

st.divider()

# View toggle
view_mode = st.toggle("📋 Executive Action Report", value=True)

if not view_mode:
    # ── RAW DATA VIEW ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Raw Dataset</div>', unsafe_allow_html=True)
    
    if os.path.exists(DATA_CSV):
        df_raw = pd.read_csv(DATA_CSV)
        st.dataframe(df_raw, use_container_width=True, height=350)
        st.caption(f"{len(df_raw)} records · {len(df_raw.columns)} columns")
    else:
        st.warning("No data found. Run `scripts/generate_mock_data.py` first.")
    
    if os.path.exists(FILTERED_CSV):
        st.markdown('<div class="section-header">Classified Results</div>', unsafe_allow_html=True)
        df_filtered = pd.read_csv(FILTERED_CSV)
        
        col_filter, col_chart = st.columns([2, 1])
        
        with col_filter:
            status_filter = st.multiselect(
                "Filter by Status:",
                options=sorted(df_filtered["Status"].unique()),
                default=sorted(df_filtered["Status"].unique()),
            )
            df_display = df_filtered[df_filtered["Status"].isin(status_filter)]
            
            def color_status(val):
                colors = {
                    "Liquidation": "background-color: #f8514933; color: #f85149",
                    "Review": "background-color: #d2992233; color: #d29922",
                    "VIP_Keep": "background-color: #3fb95033; color: #3fb950",
                    "Normal": "background-color: #161b22; color: #8b949e",
                }
                return colors.get(val, "")
            
            styled = df_display.style.map(color_status, subset=["Status"])
            st.dataframe(styled, use_container_width=True, height=350)
        
        with col_chart:
            st.markdown("**Distribution**")
            counts = df_filtered["Status"].value_counts()
            st.bar_chart(counts, color="#58a6ff")

else:
    # ── EXECUTIVE ACTION REPORT VIEW ─────────────────────────────────────
    
    report_text = None
    if "report" in st.session_state:
        report_text = st.session_state["report"]
    elif os.path.exists(REPORT_MD):
        with open(REPORT_MD, "r") as f:
            report_text = f.read()
    
    if report_text:
        # Report in a styled card
        st.markdown(f'<div class="report-card">', unsafe_allow_html=True)
        st.markdown(report_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Violations table
        st.markdown('<div class="section-header">Violation Details</div>', unsafe_allow_html=True)
        
        if os.path.exists(VIOLATIONS_CSV):
            df_violations = pd.read_csv(VIOLATIONS_CSV)
            
            def color_violations(val):
                colors = {
                    "Liquidation": "background-color: #f8514933; color: #f85149",
                    "Review": "background-color: #d2992233; color: #d29922",
                    "VIP_Keep": "background-color: #3fb95033; color: #3fb950",
                }
                return colors.get(val, "")
            
            styled = df_violations.style.map(color_violations, subset=["Status"])
            st.dataframe(styled, use_container_width=True, height=280)
            st.caption(f"{len(df_violations)} violations flagged across {df_violations['Status'].nunique()} categories")
        
        st.divider()
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve Actions", type="primary", use_container_width=True):
                st.balloons()
                st.success("Actions approved. Compliance directives queued for execution.")
        
        with col2:
            if st.button("📧 Send to Stakeholders", use_container_width=True):
                st.info("📨 Report dispatched to stakeholder channel (simulated)")
        
        with col3:
            st.download_button(
                label="📥 Export Report",
                data=report_text,
                file_name="executive_action_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
    else:
        st.markdown(
            """
            <div style="text-align: center; padding: 80px 0; color: #484f58;">
                <div style="font-size: 3rem; margin-bottom: 16px;">⚙️</div>
                <div style="font-size: 1.1rem; color: #8b949e;">No report generated yet.</div>
                <div style="font-size: 0.85rem; margin-top: 8px;">
                    Click <strong>▶ Run SOP Compiler</strong> in the sidebar to execute the pipeline.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Agent Terminal (always visible at bottom) ────────────────────────────────

st.divider()
with st.expander("🖥️ Agent Terminal — Pipeline Execution Log", expanded=False):
    if "pipeline_run" in st.session_state:
        # Show a reconstructed log from the summary stats
        if os.path.exists(SUMMARY_JSON):
            with open(SUMMARY_JSON, "r") as f:
                s = json.load(f)
            
            terminal_logs = [
                "[STEP] Pipeline initialized",
                f"[>>] Loaded {s['total_items']} records from {DATA_CSV}",
                "[STEP] Dynamically imported verified_filter.py",
                "[OK] apply_filters() executed successfully",
                f"[OK] Status distribution: Normal={s['normal_items']}, "
                f"Liquidation={s['liquidation']['count']}, "
                f"Review={s['review']['count']}, "
                f"VIP_Keep={s['vip_keep']['count']}",
                f"[STEP] Saved violations.csv ({s['total_violations']} rows)",
                "[STEP] Saved summary_stats.json",
                "[STEP] Reporter Agent invoked (Executive Compliance Officer)",
                "[>>] Cerebras gpt-oss-120b — generating action report...",
                "[OK] Executive Action Report generated",
                f"[OK] Pipeline complete — {s['violation_rate']}% violation rate detected",
            ]
            st.markdown(render_agent_terminal(terminal_logs), unsafe_allow_html=True)
        else:
            st.markdown(render_agent_terminal(["[OK] Pipeline completed. Stats unavailable."]), unsafe_allow_html=True)
    else:
        st.markdown(
            render_agent_terminal([
                "[STEP] Awaiting pipeline execution...",
                "[>>] Click '▶ Run SOP Compiler' in the sidebar to begin.",
            ]),
            unsafe_allow_html=True,
        )


# ── Footer ───────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "⚙️ Agentic SOP Compiler v1.0 · "
    "LangGraph + Cerebras gpt-oss-120b · "
    "Deterministic Rule Enforcement via Code Generation"
)
