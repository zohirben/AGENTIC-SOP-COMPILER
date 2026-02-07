"""
runtime.py
Sprint 4 — The Runtime Pipeline.
Loads mock_data.csv, executes verified_filter.py dynamically,
calculates summary stats, saves violations.csv + summary_stats.json.
"""

import os
import sys
import json
import importlib.util
import pandas as pd

# Paths (relative to project root)
DATA_CSV = "data/mock_data.csv"
VERIFIED_FILTER = "outputs/verified_filter.py"
VIOLATIONS_CSV = "outputs/violations.csv"
SUMMARY_JSON = "outputs/summary_stats.json"
FILTERED_CSV = "outputs/filtered_results.csv"


def load_verified_filter(filter_path: str = VERIFIED_FILTER):
    """
    Dynamically import apply_filters() from verified_filter.py.
    
    Returns:
        The apply_filters function callable.
    """
    abs_path = os.path.abspath(filter_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(
            f"verified_filter.py not found at {abs_path}. "
            "Run the engine loop first (Sprint 3) to generate it."
        )
    
    spec = importlib.util.spec_from_file_location("verified_filter", abs_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, "apply_filters"):
        raise AttributeError("verified_filter.py has no apply_filters() function")
    
    return module.apply_filters


def run_pipeline(
    csv_path: str = DATA_CSV,
    filter_path: str = VERIFIED_FILTER,
    violations_path: str = VIOLATIONS_CSV,
    summary_path: str = SUMMARY_JSON,
    filtered_path: str = FILTERED_CSV,
) -> dict:
    """
    Full runtime pipeline:
    1. Load CSV
    2. Apply verified filter
    3. Calculate summary stats
    4. Save violations.csv + summary_stats.json
    
    Returns:
        Summary stats dict
    """
    print("=" * 60)
    print("🏛️  TITAN RUNTIME PIPELINE")
    print("=" * 60)
    
    # Step 1: Load data
    print(f"\n📂 Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    total_rows = len(df)
    print(f"   Loaded {total_rows} rows, {len(df.columns)} columns")
    
    # Step 2: Dynamically import and apply filter
    print(f"\n⚡ Loading filter from {filter_path}...")
    apply_filters = load_verified_filter(filter_path)
    df_filtered = apply_filters(df.copy())
    print(f"   ✅ Filters applied. Status distribution:")
    
    status_counts = df_filtered["Status"].value_counts().to_dict()
    for status, count in sorted(status_counts.items()):
        print(f"      {status}: {count}")
    
    # Step 3: Save full filtered results
    df_filtered.to_csv(filtered_path, index=False)
    print(f"\n💾 Full results saved to {filtered_path}")
    
    # Step 4: Extract violations (anything NOT 'Normal')
    violations = df_filtered[df_filtered["Status"] != "Normal"].copy()
    violations.to_csv(violations_path, index=False)
    print(f"💾 Violations saved to {violations_path} ({len(violations)} rows)")
    
    # Step 5: Calculate summary stats
    liquidation_items = df_filtered[df_filtered["Status"] == "Liquidation"]
    review_items = df_filtered[df_filtered["Status"] == "Review"]
    vip_items = df_filtered[df_filtered["Status"] == "VIP_Keep"]
    normal_items = df_filtered[df_filtered["Status"] == "Normal"]
    
    # Trapped Capital = total Price of Liquidation items
    trapped_capital = float(liquidation_items["Price"].sum()) if len(liquidation_items) > 0 else 0.0
    
    # Lost margin = total Profit_Per_Item of Review items (low-margin items)
    lost_margin = float(review_items["Profit_Per_Item"].sum()) if len(review_items) > 0 else 0.0
    
    # VIP saved value = total Price of VIP_Keep items
    vip_saved_value = float(vip_items["Price"].sum()) if len(vip_items) > 0 else 0.0
    
    summary = {
        "total_items": total_rows,
        "normal_items": int(status_counts.get("Normal", 0)),
        "liquidation": {
            "count": int(status_counts.get("Liquidation", 0)),
            "trapped_capital": round(trapped_capital, 2),
            "avg_days_in_warehouse": round(float(liquidation_items["Days_in_Warehouse"].mean()), 1) if len(liquidation_items) > 0 else 0,
        },
        "review": {
            "count": int(status_counts.get("Review", 0)),
            "total_lost_margin": round(lost_margin, 2),
            "avg_profit": round(float(review_items["Profit_Per_Item"].mean()), 2) if len(review_items) > 0 else 0,
        },
        "vip_keep": {
            "count": int(status_counts.get("VIP_Keep", 0)),
            "saved_value": round(vip_saved_value, 2),
            "avg_profit": round(float(vip_items["Profit_Per_Item"].mean()), 2) if len(vip_items) > 0 else 0,
        },
        "total_violations": len(violations),
        "violation_rate": round(len(violations) / total_rows * 100, 1),
    }
    
    # Save summary
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"💾 Summary stats saved to {summary_path}")
    
    # Print summary
    print(f"\n{'=' * 60}")
    print("📊 SUMMARY STATS")
    print(f"{'=' * 60}")
    print(f"   Total Items:        {summary['total_items']}")
    print(f"   Normal:             {summary['normal_items']}")
    print(f"   🚨 Liquidation:     {summary['liquidation']['count']} items (${summary['liquidation']['trapped_capital']:,.2f} trapped)")
    print(f"   ⚠️  Review:          {summary['review']['count']} items (${summary['review']['total_lost_margin']:,.2f} margin at risk)")
    print(f"   ✅ VIP Saved:        {summary['vip_keep']['count']} items (${summary['vip_keep']['saved_value']:,.2f} preserved)")
    print(f"   Violation Rate:     {summary['violation_rate']}%")
    print(f"{'=' * 60}")
    
    return summary


if __name__ == "__main__":
    summary = run_pipeline()
