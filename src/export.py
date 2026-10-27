"""Export data to CSV, JSON, SQL."""
import csv
import json
import os
from typing import List, Dict, Any
from pathlib import Path

from config.settings import DATA_DIR, GROUND_TRUTH_DIR


class Exporter:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        GROUND_TRUTH_DIR.mkdir(parents=True, exist_ok=True)
    
    def to_csv(self, data: List[Dict[str, Any]], filename: str, subdir: str = ""):
        if not data:
            return
        outdir = DATA_DIR if subdir == "" else GROUND_TRUTH_DIR
        filepath = outdir / filename
        keys = data[0].keys()
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        print(f"  Wrote {filepath} ({len(data)} rows)")
    
    def to_json(self, data: List[Dict[str, Any]], filename: str, subdir: str = ""):
        outdir = DATA_DIR if subdir == "" else GROUND_TRUTH_DIR
        filepath = outdir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"  Wrote {filepath} ({len(data)} rows)")
    
    def to_sql(self, all_data: Dict[str, List[Dict[str, Any]]], filename: str = "seed_data.sql"):
        filepath = DATA_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("-- YottaFlex Synthetic Data Seed\n")
            f.write("-- Generated with seed 20261022\n\n")
            f.write("BEGIN;\n\n")
            
            for table_name, rows in all_data.items():
                if not rows or table_name == "ground_truth":
                    continue
                f.write(f"-- Table: {table_name}\n")
                keys = list(rows[0].keys())
                for row in rows[:1000]:  # Limit for SQL file size, still shows structure
                    cols = ', '.join([f'"{k}"' for k in keys])
                    vals = []
                    for k in keys:
                        v = row[k]
                        if v is None:
                            vals.append('NULL')
                        elif isinstance(v, bool):
                            vals.append('TRUE' if v else 'FALSE')
                        elif isinstance(v, (int, float)):
                            vals.append(str(v))
                        else:
                            # Escape quotes
                            v_str = str(v).replace("'", "''")
                            vals.append(f"'{v_str}'")
                    vals_str = ', '.join(vals)
                    f.write(f"INSERT INTO {table_name} ({cols}) VALUES ({vals_str});\n")
                if len(rows) > 1000:
                    f.write(f"-- ... ({len(rows) - 1000} more rows)\n")
                f.write("\n")
            
            f.write("COMMIT;\n")
        print(f"  Wrote {filepath} (schema + sample inserts)")
