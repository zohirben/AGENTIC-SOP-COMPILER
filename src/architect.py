"""
architect.py
The "Architect Agent" - Generates Python filter scripts using Cerebras gpt-oss-120b.
Takes CSV schema + extracted rules and produces vectorized Pandas code.
GENERALIST: Works with ANY schema and ANY set of SOP rules.
"""

import os
import json
import requests


def _call_cerebras(prompt: str, temperature: float = 0.1) -> str:
    """
    Call Cerebras gpt-oss-120b API.
    
    Args:
        prompt: The prompt to send
        temperature: Sampling temperature (low = deterministic)
        
    Returns:
        Response text from the model
        
    Raises:
        RuntimeError: If API call fails
    """
    api_key = os.getenv("CEREBRAS_API_KEY")
    if not api_key:
        raise RuntimeError("CEREBRAS_API_KEY environment variable not set")
    
    url = "https://api.cerebras.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-oss-120b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a Senior Python Data Engineer. "
                    "You write clean, production-grade Pandas code. "
                    "You ONLY return raw Python code. No markdown, no ```python blocks, no explanations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2048,
        "temperature": temperature
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        raise RuntimeError(f"Cerebras API error: {response.status_code} - {response.text}")
    
    response_data = response.json()
    return response_data["choices"][0]["message"]["content"]


def _strip_markdown_fences(code: str) -> str:
    """Remove markdown code fences if LLM includes them."""
    code = code.strip()
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    if code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    return code


def generate_filter_script(schema_str: str, rules_json: str, csv_path: str = "mock_data.csv", output_path: str = "filtered_results.csv") -> str:
    """
    Generate a Python filter script using LLM based on schema and rules.
    GENERALIST: No hardcoded business logic — the LLM reasons from the rules JSON.
    
    Args:
        schema_str: Formatted CSV schema string (from context_loader)
        rules_json: JSON string of extracted rules (from rule_extractor)
        csv_path: Path to input CSV file
        output_path: Path to output CSV file
        
    Returns:
        Python code string for the filter script
    """
    prompt = f"""Write a complete Python script that classifies rows in a dataset based on business rules.

## DATA SCHEMA
{schema_str}

## BUSINESS RULES (as JSON)
{rules_json}

## INSTRUCTIONS
1. Import pandas (and numpy if needed) at the top.
2. Define a function `apply_filters(df)` that:
   - Creates a new column called 'Status' with default value 'Normal'.
   - Reads EACH rule from the BUSINESS RULES JSON above.
   - For each rule, translate `condition_logic` into a vectorized Pandas mask (using df.loc[mask, 'Status'] = ...).
   - CRITICAL — EXCEPTION HANDLING:
     * If a rule has an `exception_logic` field (non-null), it means that exception OVERRIDES the parent rule.
     * Exceptions are higher priority than their parent conditions.
     * Apply rules in order from LOWEST priority to HIGHEST priority, so that higher-priority statuses overwrite lower-priority ones.
     * General principle: specific rules (exceptions) override general rules.
   - Do NOT use for loops over rows. Use only vectorized Pandas operations.
   - Returns the modified DataFrame.
3. The script's `if __name__ == "__main__"` block must:
   - Load `{csv_path}` using pandas.
   - Call `apply_filters(df)`.
   - Save the result to `{output_path}` (with index=False).
   - Print "PROCESS_COMPLETE" as the LAST line of stdout.
4. Use ONLY pandas and numpy. No for loops over rows. No input(). No external libraries.
5. Return ONLY raw Python code. No markdown fences, no explanations, no comments about what you're doing."""

    response = _call_cerebras(prompt)
    return _strip_markdown_fences(response)


def fix_filter_script(broken_code: str, error_msg: str, schema_str: str, csv_path: str = "mock_data.csv", output_path: str = "filtered_results.csv") -> str:
    """
    Ask the LLM to fix broken code based on the error message.
    
    Args:
        broken_code: The code that failed
        error_msg: The stderr output from running the code
        schema_str: The data schema for context
        csv_path: Path to input CSV
        output_path: Path to output CSV
        
    Returns:
        Fixed Python code string
    """
    prompt = f"""Your previous code FAILED with this error:

## ERROR
{error_msg}

## BROKEN CODE
{broken_code}

## DATA SCHEMA (for reference)
{schema_str}

## TASK
Fix the code. Return ONLY the corrected Python code.
- Keep the same structure: `apply_filters(df)` function + `if __name__ == "__main__"` block.
- Must load `{csv_path}`, apply filters, save to `{output_path}`.
- Must print "PROCESS_COMPLETE" as the last line on success.
- Use ONLY pandas/numpy. No for loops over rows. No markdown fences."""

    response = _call_cerebras(prompt)
    return _strip_markdown_fences(response)


if __name__ == "__main__":
    # Quick test
    with open("outputs/context.txt", "r") as f:
        schema = f.read()
    with open("outputs/rules.json", "r") as f:
        rules = f.read()
    
    code = generate_filter_script(schema, rules, csv_path="data/mock_data.csv", output_path="outputs/filtered_results.csv")
    print("=== GENERATED CODE ===")
    print(code)
