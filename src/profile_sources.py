from pathlib import Path
import json
import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'

def profile_csv(path):
    print(f"\nCSV: {path.name}")
    if not path.exists():
        print(f"Error: {path} not found.")
        return

    print(f"File size: {path.stat().st_size} bytes")
    df = pd.read_csv(path)
    
    print(f"Row count: {len(df)}")
    print(f"Column count: {len(df.columns)}")
    print("\nColumns and Inferred Types:\n", df.dtypes)
    print("\nMissing values by column:\n", df.isnull().sum())
    
    exact_duplicates = df.duplicated().sum()
    print(f"\nExact duplicate rows: {exact_duplicates}")

    if 'customer_id' in df.columns:
        print(f"customer_id unique: {df['customer_id'].is_unique}")

def profile_json(path):
    print(f"\nJSON: {path.name}")
    if not path.exists():
        print(f"Error: {path} not found.")
        return

    with open(path, 'r') as f:
        data = json.load(f)

    is_list = isinstance(data, list)
    print(f"Root structure is a list of records: {is_list}")

    if is_list and len(data) > 0:
        print(f"Total records: {len(data)}")
        
        first_record = data[0]
        print(f"\nTop-level keys: {list(first_record.keys())}")
        
        nested_fields = [k for k, v in first_record.items() if isinstance(v, (dict, list))]
        print(f"Nested fields identified: {nested_fields}")

        timestamp_fields = [k for k, v in first_record.items() if isinstance(v, str) and any(x in k.lower() for x in ['date', 'time', 'at'])]
        numeric_fields = [k for k, v in first_record.items() if isinstance(v, (int, float))]
        
        print(f"Potential timestamp fields: {timestamp_fields}")
        print(f"Potential numeric fields: {numeric_fields}")

        all_keys = set().union(*(d.keys() for d in data))
        missing_counts = {k: 0 for k in all_keys}
        for record in data:
            for k in all_keys:
                if k not in record or record[k] is None:
                    missing_counts[k] += 1
                    
        print("\nMissing keys/nulls per field:\n", missing_counts)

def profile_parquet(path):
    print(f"\nParquet: {path.name}")
    if not path.exists():
        print(f"Error: {path} not found.")
        return

    print(f"File size: {path.stat().st_size} bytes")
    df = pd.read_parquet(path)
    
    print(f"Shape: {df.shape} (Rows: {df.shape[0]}, Columns: {df.shape[1]})")
    print("\nData Types:\n", df.dtypes)
    print("\nMissing Values:\n", df.isnull().sum())

if __name__ == '__main__':
    profile_csv(DATA_DIR / 'customers.csv')
    profile_json(DATA_DIR / 'orders.json')
    profile_parquet(DATA_DIR / 'products.parquet')