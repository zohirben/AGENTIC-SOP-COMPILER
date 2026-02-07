"""
test_sprint_2.py
Test both the context loader and rule extractor.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from src.context_loader import get_csv_context
from src.rule_extractor import extract_rules_from_file


def test_context_loader():
    """Test the context loader with mock_data.csv"""
    print("\n" + "="*80)
    print("TEST 1: Context Loader")
    print("="*80)
    
    context = get_csv_context("data/mock_data.csv", save_to_file=True)
    print(context)
    
    if "DATA SCHEMA:" in context and "Widget_" in context:
        print("\n✅ Context Loader: PASSED")
        return True
    else:
        print("\n❌ Context Loader: FAILED")
        return False


def test_rule_extractor():
    """Test the rule extractor with sops.txt"""
    print("\n" + "="*80)
    print("TEST 2: Rule Extractor")
    print("="*80)
    
    ruleset = extract_rules_from_file("data/sops.txt", save_to_file=True)
    
    if ruleset:
        print("\n✅ Extracted Rules (JSON):")
        print(ruleset.model_dump_json(indent=2))
        print(f"\n✅ Rule Extractor: PASSED ({ruleset.total_rules} rules found)")
        return True
    else:
        print("\n❌ Rule Extractor: FAILED")
        return False


def main():
    print("\n🚀 SPRINT 2 TEST SUITE")
    
    test1_passed = test_context_loader()
    test2_passed = test_rule_extractor()
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Context Loader: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Rule Extractor: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if (test1_passed and test2_passed) else '❌ SOME TESTS FAILED'}")
    print("="*80)


if __name__ == "__main__":
    main()
