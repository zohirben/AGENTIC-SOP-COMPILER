"""
context_loader.py
Extracts CSV schema and sample data for prompt injection into the Architect agent.
"""

import pandas as pd
from typing import Optional


def get_csv_context(file_path: str, save_to_file: bool = False) -> str:
    """
    Load a CSV file and return formatted context: schema + first 3 rows.
    
    Args:
        file_path: Path to the CSV file
        save_to_file: If True, save output to context.txt
        
    Returns:
        Formatted string with DATA SCHEMA and sample rows
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return f"ERROR: File not found: {file_path}"
    except Exception as e:
        return f"ERROR: Failed to read CSV: {str(e)}"
    
    if df.empty:
        return "ERROR: CSV file is empty"
    
    # Get column names
    columns = list(df.columns)
    column_str = ", ".join(columns)
    
    # Get data types
    dtypes_str = ", ".join([f"{col}: {str(df[col].dtype)}" for col in columns])
    
    # Get first 3 rows
    sample_rows = df.head(3)
    
    # Build markdown table header
    header_row = "| " + " | ".join(columns) + " |"
    separator_row = "| " + " | ".join(["---"] * len(columns)) + " |"
    
    # Build data rows
    data_rows = []
    for _, row in sample_rows.iterrows():
        row_str = "| " + " | ".join([str(val) for val in row]) + " |"
        data_rows.append(row_str)
    
    # Construct final output
    context = f"""DATA SCHEMA:
- Columns: [{column_str}]
- Data Types: [{dtypes_str}]
- Total Rows: {len(df)}

Sample Data (First 3 Rows):
{header_row}
{separator_row}
{chr(10).join(data_rows)}
"""
    
    # Save to file if requested
    if save_to_file:
        with open("outputs/context.txt", "w") as f:
            f.write(context)
        print("✅ Context saved to outputs/context.txt")
    
    return context


def get_csv_head(file_path: str, n: int = 5) -> pd.DataFrame:
    """
    Convenience function to get first n rows as a DataFrame.
    
    Args:
        file_path: Path to the CSV file
        n: Number of rows to return (default 5)
        
    Returns:
        DataFrame with first n rows
    """
    return pd.read_csv(file_path).head(n)


if __name__ == "__main__":
    # Test the context loader
    context = get_csv_context("data/mock_data.csv")
    print(context)
