import re

import pandas as pd
from pathlib import Path

# =========================
# Config
# =========================
INPUT_DIR = "./data/wiki_5y"
OUTPUT_CSV = "./data/wiki_5y/merged_2.csv"

# =========================
# Main
# =========================
def main():
    input_path = Path(INPUT_DIR)

    if not input_path.exists():
        raise FileNotFoundError(f"Folder not found: {INPUT_DIR}")

    csv_files = sorted(input_path.glob("*.csv"))

    if not csv_files:
        raise ValueError("No CSV files found in the folder")

    print(f"Found {len(csv_files)} CSV files")

    dfs = []
    for csv_file in csv_files:
        genre = re.match(r"^wiki_(.+)_5y\.csv$", csv_file.name).group(1)
        print(f"Reading {csv_file.name}")
        df = pd.read_csv(csv_file)
        df["genre"] = genre
        dfs.append(df)

    merged_df = pd.concat(dfs, ignore_index=True)

    print(f"Total rows after merge: {len(merged_df)}")

    merged_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved merged CSV to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
