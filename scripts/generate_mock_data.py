"""
generate_mock_data.py
Generates mock_data.csv with 100 rows for the Titan SOP Compiler test environment.

Rigged Data Strategy:
- Rows 0-80: Normal data (Age < 100, Profit > $10)
- Rows 81-90: Trigger Liquidation (Age = 200, Profit = $4)
- Rows 91-95: Trigger Review (Age = 50, Profit = $2)
- Rows 96-100: Trigger VIP Exception (Age = 250, Profit = $25)
"""

import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Initialize data
data = []

# Rows 0-79: Normal data (Age < 100, Profit > $10)
for i in range(80):
    item_name = f"Widget_{i+1:03d}"
    price = np.random.uniform(20, 100)
    days_in_warehouse = np.random.randint(10, 100)
    profit_per_item = np.random.uniform(10, 50)
    data.append({
        "Item_Name": item_name,
        "Price": round(price, 2),
        "Days_in_Warehouse": days_in_warehouse,
        "Profit_Per_Item": round(profit_per_item, 2)
    })

# Rows 80-89: Trigger Liquidation (Age = 200, Profit = $4)
for i in range(10):
    item_name = f"Widget_{81+i:03d}"
    price = 50
    days_in_warehouse = 200
    profit_per_item = 4.00
    data.append({
        "Item_Name": item_name,
        "Price": price,
        "Days_in_Warehouse": days_in_warehouse,
        "Profit_Per_Item": profit_per_item
    })

# Rows 90-94: Trigger Review (Age = 50, Profit = $2)
for i in range(5):
    item_name = f"Widget_{91+i:03d}"
    price = 30
    days_in_warehouse = 50
    profit_per_item = 2.00
    data.append({
        "Item_Name": item_name,
        "Price": price,
        "Days_in_Warehouse": days_in_warehouse,
        "Profit_Per_Item": profit_per_item
    })

# Rows 95-99: Trigger VIP Exception (Age = 250, Profit = $25)
for i in range(5):
    item_name = f"Widget_{96+i:03d}"
    price = 75
    days_in_warehouse = 250
    profit_per_item = 25.00
    data.append({
        "Item_Name": item_name,
        "Price": price,
        "Days_in_Warehouse": days_in_warehouse,
        "Profit_Per_Item": profit_per_item
    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("data/mock_data.csv", index=False)

print("✅ data/mock_data.csv generated successfully!")
print(f"Total rows: {len(df)}")
print("\nData Summary:")
print(df.describe())
print("\nFirst 5 rows:")
print(df.head())
print("\nLast 5 rows (VIP Exception):")
print(df.tail(5))
print("\nData schema:")
print(df.dtypes)
