"""
test_sprint_3.py
Multi-scenario test harness for the generalist Architect + Validation engine.
Tests 3 completely different SOP+Dataset combinations.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.context_loader import get_csv_context
from src.engine_loop import run_engine, MAX_RETRIES


# ============================================================================
# SCENARIO 1: Original Titan SOP (warehouse liquidation)
# ============================================================================
def setup_scenario_1():
    """Original Titan SOP — already exists from Sprint 1."""
    name = "Titan Warehouse SOP"
    csv_path = "data/mock_data.csv"
    context_path = "outputs/context.txt"
    rules_path = "outputs/rules.json"
    output_path = "outputs/test_output_s1.csv"
    expected = {"Normal": 80, "Liquidation": 10, "Review": 5, "VIP_Keep": 5}
    return name, csv_path, context_path, rules_path, output_path, expected


# ============================================================================
# SCENARIO 2: Pricing Tier Classification (completely different domain)
# ============================================================================
def setup_scenario_2():
    """Pricing tiers for an online electronics store."""
    name = "Electronics Pricing Tiers"
    csv_path = "outputs/test_electronics.csv"
    context_path = "outputs/test_electronics_context.txt"
    rules_path = "outputs/test_electronics_rules.json"
    output_path = "outputs/test_output_s2.csv"
    
    np.random.seed(99)
    data = []
    
    # 60 normal products (Price 50-200, Rating 3-5)
    for i in range(60):
        data.append({
            "Product_Name": f"Gadget_{i+1:03d}",
            "Price": round(np.random.uniform(50, 200), 2),
            "Customer_Rating": round(np.random.uniform(3.0, 5.0), 1),
            "Units_Sold": np.random.randint(100, 1000)
        })
    
    # 15 Budget products (Price < 30) -> should be 'Budget'
    for i in range(15):
        data.append({
            "Product_Name": f"Gadget_{60+i+1:03d}",
            "Price": round(np.random.uniform(10, 29), 2),
            "Customer_Rating": round(np.random.uniform(2.0, 4.0), 1),
            "Units_Sold": np.random.randint(50, 300)
        })
    
    # 15 Premium products (Price > 500) -> should be 'Premium'
    for i in range(15):
        data.append({
            "Product_Name": f"Gadget_{75+i+1:03d}",
            "Price": round(np.random.uniform(501, 1000), 2),
            "Customer_Rating": round(np.random.uniform(4.0, 5.0), 1),
            "Units_Sold": np.random.randint(10, 100)
        })
    
    # 10 Clearance products (Price > 500 BUT Rating < 2.5) -> should be 'Clearance' (exception!)
    for i in range(10):
        data.append({
            "Product_Name": f"Gadget_{90+i+1:03d}",
            "Price": round(np.random.uniform(501, 800), 2),
            "Customer_Rating": round(np.random.uniform(1.0, 2.4), 1),
            "Units_Sold": np.random.randint(1, 20)
        })
    
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    
    # Generate context
    context = get_csv_context(csv_path)
    with open(context_path, "w") as f:
        f.write(context)
    
    # Rules
    rules = {
        "rules": [
            {
                "rule_id": 1,
                "rule_name": "Budget Tier",
                "condition_logic": "If Price is less than 30, status should be 'Budget'.",
                "exception_logic": None
            },
            {
                "rule_id": 2,
                "rule_name": "Premium Tier",
                "condition_logic": "If Price is greater than 500, status should be 'Premium'.",
                "exception_logic": "If Price is greater than 500 BUT Customer_Rating is below 2.5, status should be 'Clearance' instead of 'Premium'."
            },
            {
                "rule_id": 3,
                "rule_name": "Clearance Exception",
                "condition_logic": "If Price is greater than 500 and Customer_Rating is less than 2.5, status should be 'Clearance' (override Premium).",
                "exception_logic": None
            }
        ],
        "total_rules": 3
    }
    with open(rules_path, "w") as f:
        json.dump(rules, f, indent=2)
    
    expected = {"Normal": 60, "Budget": 15, "Premium": 15, "Clearance": 10}
    return name, csv_path, context_path, rules_path, output_path, expected


# ============================================================================
# SCENARIO 3: Order Fulfillment Priority (logistics domain)
# ============================================================================
def setup_scenario_3():
    """Order priority rules for a logistics/fulfillment center."""
    name = "Order Fulfillment Priority"
    csv_path = "outputs/test_orders.csv"
    context_path = "outputs/test_orders_context.txt"
    rules_path = "outputs/test_orders_rules.json"
    output_path = "outputs/test_output_s3.csv"
    
    np.random.seed(77)
    data = []
    
    # 50 standard orders (Value 20-200, Delay 0-3 days)
    for i in range(50):
        data.append({
            "Order_ID": f"ORD_{i+1:04d}",
            "Order_Value": round(np.random.uniform(20, 200), 2),
            "Days_Since_Order": np.random.randint(0, 4),
            "Is_Prime_Member": np.random.choice([True, False])
        })
    
    # 20 delayed orders (Delay > 7) -> should be 'Urgent'
    for i in range(20):
        data.append({
            "Order_ID": f"ORD_{50+i+1:04d}",
            "Order_Value": round(np.random.uniform(20, 200), 2),
            "Days_Since_Order": np.random.randint(8, 15),
            "Is_Prime_Member": False
        })
    
    # 15 high-value orders (Value > 500) -> should be 'Priority'
    for i in range(15):
        data.append({
            "Order_ID": f"ORD_{70+i+1:04d}",
            "Order_Value": round(np.random.uniform(501, 2000), 2),
            "Days_Since_Order": np.random.randint(0, 3),
            "Is_Prime_Member": np.random.choice([True, False])
        })
    
    # 15 VIP rush (Delay > 7 AND Value > 500) -> should be 'VIP_Rush'
    for i in range(15):
        data.append({
            "Order_ID": f"ORD_{85+i+1:04d}",
            "Order_Value": round(np.random.uniform(501, 2000), 2),
            "Days_Since_Order": np.random.randint(8, 20),
            "Is_Prime_Member": True
        })
    
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    
    # Generate context
    context = get_csv_context(csv_path)
    with open(context_path, "w") as f:
        f.write(context)
    
    # Rules
    rules = {
        "rules": [
            {
                "rule_id": 1,
                "rule_name": "Delayed Order",
                "condition_logic": "If Days_Since_Order is greater than 7, status should be 'Urgent'.",
                "exception_logic": "If Days_Since_Order > 7 AND Order_Value > 500, status should be 'VIP_Rush' instead of 'Urgent'."
            },
            {
                "rule_id": 2,
                "rule_name": "High Value Order",
                "condition_logic": "If Order_Value is greater than 500, status should be 'Priority'.",
                "exception_logic": None
            },
            {
                "rule_id": 3,
                "rule_name": "VIP Rush Exception",
                "condition_logic": "If Days_Since_Order > 7 AND Order_Value > 500, status should be 'VIP_Rush'. This overrides both 'Urgent' and 'Priority'.",
                "exception_logic": None
            }
        ],
        "total_rules": 3
    }
    with open(rules_path, "w") as f:
        json.dump(rules, f, indent=2)
    
    expected = {"Normal": 50, "Urgent": 20, "Priority": 15, "VIP_Rush": 15}
    return name, csv_path, context_path, rules_path, output_path, expected


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def main():
    print("=" * 70)
    print("🏛️  SPRINT 3 MULTI-SCENARIO TEST SUITE")
    print("    Testing generalist Architect prompt across 3 domains")
    print("=" * 70)
    
    scenarios = [
        setup_scenario_1,
        setup_scenario_2,
        setup_scenario_3,
    ]
    
    results = []
    
    for setup_fn in scenarios:
        name, csv_path, context_path, rules_path, output_path, expected = setup_fn()
        
        result = run_engine(
            csv_path=csv_path,
            context_path=context_path,
            rules_path=rules_path,
            output_path=output_path,
            expected=expected,
            scenario_name=name
        )
        results.append(result)
    
    # ========================================================================
    # FINAL REPORT
    # ========================================================================
    print("\n\n" + "=" * 70)
    print("📋 SPRINT 3 FINAL REPORT")
    print("=" * 70)
    
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    
    for r in results:
        icon = "✅" if r["success"] else "❌"
        val_icon = "✅" if r["validation_passed"] else "❌"
        print(f"\n{icon} {r['scenario']}")
        print(f"   Attempts: {r['attempts']}/{MAX_RETRIES}")
        print(f"   Execution: {'PASS' if r['success'] else 'FAIL'}")
        print(f"   Validation: {val_icon}")
        if r["validation_report"]:
            for line in r["validation_report"].split("\n"):
                print(f"   {line}")
    
    print(f"\n{'=' * 70}")
    print(f"OVERALL: {passed}/{total} scenarios passed")
    rate = (passed / total * 100) if total > 0 else 0
    print(f"SUCCESS RATE: {rate:.0f}%")
    print(f"{'=' * 70}")
    
    # Cleanup test files
    # (keep them for inspection, just note it)
    print("\nTest artifacts left for inspection:")
    for r in results:
        print(f"  - generated_filter.py (last scenario's code)")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
