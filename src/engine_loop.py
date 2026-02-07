"""
engine_loop.py
The "Self-Healing" Engine Loop.
Generates filter code via the Architect, executes it, validates output, retries on failure.
Supports parameterized paths for multi-scenario testing.
"""

import os
import sys
import subprocess
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.architect import generate_filter_script, fix_filter_script
from src.context_loader import get_csv_context

MAX_RETRIES = 3
GENERATED_FILE = "outputs/generated_filter.py"


def load_inputs(context_path: str = "outputs/context.txt", rules_path: str = "outputs/rules.json") -> tuple[str, str]:
    """Load schema and rules from Sprint 2 output files."""
    with open(context_path, "r") as f:
        schema_str = f.read()
    with open(rules_path, "r") as f:
        rules_json = f.read()
    return schema_str, rules_json


def save_code(code: str, file_path: str) -> None:
    """Save generated code to a file."""
    with open(file_path, "w") as f:
        f.write(code)


def execute_code(file_path: str) -> tuple[bool, str, str]:
    """
    Execute the generated Python script in a subprocess.
    
    Returns:
        (success: bool, stdout: str, stderr: str)
    """
    python_exe = sys.executable
    
    result = subprocess.run(
        [python_exe, file_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    success = result.returncode == 0 and "PROCESS_COMPLETE" in result.stdout
    return success, result.stdout, result.stderr


def validate_output(output_path: str, expected: dict | None = None) -> tuple[bool, str]:
    """
    Post-execution validation of the generated CSV.
    
    Args:
        output_path: Path to the filtered_results.csv
        expected: Optional dict with expected status counts, e.g.
                  {"Normal": 80, "Liquidation": 10, "Review": 5, "VIP_Keep": 5}
    
    Returns:
        (valid: bool, report: str)
    """
    import pandas as pd
    
    if not os.path.exists(output_path):
        return False, f"Output file {output_path} not found"
    
    df = pd.read_csv(output_path)
    
    # Check 1: Status column exists
    if "Status" not in df.columns:
        return False, "VALIDATION FAIL: 'Status' column missing from output"
    
    # Check 2: No NaN in Status
    nan_count = df["Status"].isna().sum()
    if nan_count > 0:
        return False, f"VALIDATION FAIL: {nan_count} rows have NaN Status"
    
    # Check 3: Row count preserved
    actual_counts = df["Status"].value_counts().to_dict()
    
    report_lines = ["📊 Validation Report:"]
    report_lines.append(f"   Total rows: {len(df)}")
    report_lines.append(f"   Status distribution:")
    for status, count in sorted(actual_counts.items()):
        report_lines.append(f"     {status}: {count}")
    
    # Check 4: Expected counts (if provided)
    if expected:
        mismatches = []
        for status, exp_count in expected.items():
            actual = actual_counts.get(status, 0)
            match = "✅" if actual == exp_count else "❌"
            if actual != exp_count:
                mismatches.append(f"{status}: expected {exp_count}, got {actual}")
            report_lines.append(f"   {match} {status}: expected={exp_count}, actual={actual}")
        
        if mismatches:
            report = "\n".join(report_lines)
            return False, f"VALIDATION FAIL: Mismatched counts\n{report}"
    
    report = "\n".join(report_lines)
    return True, report


def run_engine(
    csv_path: str = "data/mock_data.csv",
    context_path: str = "outputs/context.txt",
    rules_path: str = "outputs/rules.json",
    output_path: str = "outputs/filtered_results.csv",
    expected: dict | None = None,
    scenario_name: str = "Default"
) -> dict:
    """
    Main engine loop with validation.
    
    Args:
        csv_path: Path to input CSV
        context_path: Path to schema context file
        rules_path: Path to rules JSON file
        output_path: Path to output CSV
        expected: Expected status counts for validation
        scenario_name: Name for logging
    
    Returns:
        Result dict with keys: success, attempts, validation, code
    """
    print(f"\n🚀 ENGINE LOOP: Scenario '{scenario_name}'")
    print("=" * 70)
    
    result = {
        "scenario": scenario_name,
        "success": False,
        "attempts": 0,
        "validation_passed": False,
        "validation_report": "",
        "code": ""
    }
    
    # Step 1: Load or generate context
    if os.path.exists(context_path):
        schema_str = open(context_path).read()
    else:
        schema_str = get_csv_context(csv_path)
    
    with open(rules_path, "r") as f:
        rules_json = f.read()
    
    print(f"✅ Loaded schema from {context_path}")
    print(f"✅ Loaded rules from {rules_path}")
    
    # Step 2: Generate initial code
    print(f"\n📝 Generating filter script via Architect (gpt-oss-120b)...")
    current_code = generate_filter_script(schema_str, rules_json, csv_path, output_path)
    
    # Step 3: Execute and retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        result["attempts"] = attempt
        print(f"\n--- Attempt {attempt}/{MAX_RETRIES} ---")
        
        # Save code
        save_code(current_code, GENERATED_FILE)
        print(f"💾 Saved code to {GENERATED_FILE} ({len(current_code)} chars)")
        
        # Execute
        print(f"⚡ Executing {GENERATED_FILE}...")
        try:
            exec_success, stdout, stderr = execute_code(GENERATED_FILE)
        except subprocess.TimeoutExpired:
            print("⏰ Execution timed out (30s limit)")
            stderr = "TimeoutError: Script execution exceeded 30 seconds."
            exec_success = False
            stdout = ""
        
        if exec_success:
            print(f"✅ Code executed successfully (PROCESS_COMPLETE found)")
            
            # Step 4: VALIDATION
            print(f"\n🔍 Running validation...")
            valid, val_report = validate_output(output_path, expected)
            result["validation_report"] = val_report
            print(val_report)
            
            if valid:
                result["success"] = True
                result["validation_passed"] = True
                result["code"] = current_code
                
                # Save verified version
                save_code(current_code, "outputs/verified_filter.py")
                print(f"\n💾 Verified code saved to outputs/verified_filter.py")
                
                print(f"\n{'=' * 70}")
                print(f"✅ SCENARIO '{scenario_name}': PASSED on attempt {attempt}")
                print(f"{'=' * 70}")
                return result
            else:
                # Validation failed — treat as error and retry
                error_msg = f"Code ran but output validation failed:\n{val_report}"
                print(f"❌ Validation failed")
                
                if attempt < MAX_RETRIES:
                    print(f"🔧 Feeding validation error back to Architect...")
                    current_code = fix_filter_script(current_code, error_msg, schema_str, csv_path, output_path)
        else:
            # Execution failed
            error_msg = stderr.strip() if stderr.strip() else f"No stderr. stdout: {stdout.strip()}"
            print(f"❌ Execution failed:\n{error_msg[:500]}")
            
            if attempt < MAX_RETRIES:
                print(f"🔧 Feeding error back to Architect for retry...")
                current_code = fix_filter_script(current_code, error_msg, schema_str, csv_path, output_path)
    
    print(f"\n{'=' * 70}")
    print(f"❌ SCENARIO '{scenario_name}': FAILED after {MAX_RETRIES} attempts")
    print(f"{'=' * 70}")
    return result


if __name__ == "__main__":
    result = run_engine(
        csv_path="data/mock_data.csv",
        context_path="outputs/context.txt",
        rules_path="outputs/rules.json",
        output_path="outputs/filtered_results.csv",
        expected={"Normal": 80, "Liquidation": 10, "Review": 5, "VIP_Keep": 5},
        scenario_name="Titan SOP (Original)"
    )
