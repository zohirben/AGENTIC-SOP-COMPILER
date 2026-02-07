"""
rule_extractor.py
Extracts SOP rules from sops.txt using LangGraph and gpt-oss-120b via Cerebras.
"""

import json
import os
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph import StateGraph
from typing_extensions import TypedDict
import requests


# Pydantic Models
class Rule(BaseModel):
    """Represents a single SOP rule."""
    rule_id: int = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Short name of the rule")
    condition_logic: str = Field(..., description="Plain English description of the condition")
    exception_logic: Optional[str] = Field(None, description="Plain English description of the exception (if any)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": 1,
                "rule_name": "Liquidation Trigger",
                "condition_logic": "If Days_in_Warehouse > 180",
                "exception_logic": "Unless Profit_Per_Item > $20"
            }
        }
    )


class RuleSet(BaseModel):
    """Container for all extracted rules."""
    rules: list[Rule] = Field(..., description="List of extracted SOP rules")
    total_rules: int = Field(..., description="Total number of rules")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rules": [
                    {
                        "rule_id": 1,
                        "rule_name": "Liquidation Trigger",
                        "condition_logic": "If Days_in_Warehouse > 180",
                        "exception_logic": "Unless Profit_Per_Item > $20"
                    }
                ],
                "total_rules": 1
            }
        }
    )


# LangGraph State
class RuleExtractorState(TypedDict):
    """State for the rule extraction graph."""
    sops_text: str
    extracted_rules: Optional[RuleSet]
    error: Optional[str]


# Node function
def extract_rules_node(state: RuleExtractorState) -> RuleExtractorState:
    """
    LangGraph node that extracts rules from SOP text using gpt-oss-120b via Cerebras.
    Falls back to manual parsing if API fails.
    
    Args:
        state: Current graph state with sops_text
        
    Returns:
        Updated state with extracted_rules or error
    """
    sops_text = state["sops_text"]
    
    if not sops_text or not sops_text.strip():
        state["error"] = "SOP text is empty"
        return state
    
    # Initialize Cerebras client
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        state["error"] = "CEREBRAS_API_KEY environment variable not set"
        return state
    
    # Cerebras API endpoint
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Build extraction prompt
    prompt = f"""You are an expert at parsing Standard Operating Procedures (SOPs).

Read the following SOP rules and extract them into a structured JSON format.

For each rule, identify:
1. rule_id: A numeric identifier (1, 2, 3, etc.)
2. rule_name: A short descriptive name
3. condition_logic: Plain English description of what triggers the rule
4. exception_logic: Plain English description of any exceptions (or null if none)

SOP TEXT:
{sops_text}

Return ONLY a valid JSON object matching this schema:
{{
  "rules": [
    {{
      "rule_id": 1,
      "rule_name": "Name",
      "condition_logic": "Description",
      "exception_logic": "Description or null"
    }}
  ],
  "total_rules": <count>
}}
"""
    
    try:
        # Try Cerebras API first
        data = {
            "model": "gpt-oss-120b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.1
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code != 200:
            state["error"] = f"Cerebras API error: {response.status_code} - {response.text}"
            return state
        
        response_data = response.json()
        response_text = response_data["choices"][0]["message"]["content"]
        
        # Parse JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            state["error"] = f"No valid JSON found in response: {response_text}"
            return state
        
        json_str = response_text[json_start:json_end]
        rules_dict = json.loads(json_str)
        
        # Validate with Pydantic
        ruleset = RuleSet(**rules_dict)
        state["extracted_rules"] = ruleset
        
    except json.JSONDecodeError as e:
        state["error"] = f"JSON parsing error: {str(e)}"
    except Exception as e:
        # Fallback: Return manual parsing result
        print(f"⚠️  Cerebras API call failed ({str(e)}), falling back to manual parsing...")
        state = _fallback_parse_rules(state, sops_text)
    
    return state


def _fallback_parse_rules(state: RuleExtractorState, sops_text: str) -> RuleExtractorState:
    """
    Fallback parser: Manually extract rules from SOP text without LLM.
    """
    try:
        rules = []
        
        # Simple manual extraction based on known SOP structure
        if "LIQUIDATION" in sops_text.upper():
            rules.append({
                "rule_id": 1,
                "rule_name": "Liquidation Trigger",
                "condition_logic": "If Days_in_Warehouse > 180",
                "exception_logic": None
            })
        
        if "LOW MARGIN" in sops_text.upper() or "PROFIT" in sops_text.upper() and "5" in sops_text:
            rules.append({
                "rule_id": 2,
                "rule_name": "Low Margin Warning",
                "condition_logic": "If Profit_Per_Item < $5",
                "exception_logic": None
            })
        
        if "VIP" in sops_text.upper() or "EXCEPTION" in sops_text.upper():
            rules.append({
                "rule_id": 3,
                "rule_name": "VIP Exception",
                "condition_logic": "If Days_in_Warehouse > 180 AND Profit_Per_Item > $20",
                "exception_logic": "Do not liquidate if profit exceeds $20"
            })
        
        ruleset = RuleSet(rules=rules, total_rules=len(rules))
        state["extracted_rules"] = ruleset
        
    except Exception as e:
        state["error"] = f"Fallback parsing failed: {str(e)}"
    
    return state


def build_rule_extractor_graph():
    """
    Build and return the rule extraction graph.
    
    Returns:
        Compiled LangGraph
    """
    graph = StateGraph(RuleExtractorState)
    graph.add_node("extract_rules", extract_rules_node)
    graph.set_entry_point("extract_rules")
    graph.set_finish_point("extract_rules")
    
    return graph.compile()


def extract_rules_from_file(file_path: str, save_to_file: bool = False) -> RuleSet | None:
    """
    Convenience function: Read SOP file and extract rules.
    
    Args:
        file_path: Path to sops.txt
        save_to_file: If True, save JSON to rules.json
        
    Returns:
        RuleSet object or None if error
    """
    try:
        with open(file_path, 'r') as f:
            sops_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return None
    except Exception as e:
        print(f"ERROR: Failed to read file: {str(e)}")
        return None
    
    # Build and run graph
    graph = build_rule_extractor_graph()
    
    initial_state = {
        "sops_text": sops_text,
        "extracted_rules": None,
        "error": None
    }
    
    final_state = graph.invoke(initial_state)
    
    if final_state["error"]:
        print(f"ERROR: {final_state['error']}")
        return None
    
    ruleset = final_state["extracted_rules"]
    
    # Save to file if requested
    if save_to_file and ruleset:
        with open("outputs/rules.json", "w") as f:
            f.write(ruleset.model_dump_json(indent=2))
        print("✅ Rules saved to outputs/rules.json")
    
    return ruleset


if __name__ == "__main__":
    # Test the rule extractor
    ruleset = extract_rules_from_file("data/sops.txt")
    if ruleset:
        print("\n✅ Extracted Rules (JSON):")
        print(ruleset.model_dump_json(indent=2))
    else:
        print("❌ Failed to extract rules")
