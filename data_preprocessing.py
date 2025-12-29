#%%
import pandas as pd
import numpy as np


# =========================
# Configurations
# =========================
INPUT_CSV = "./data/wiki_db_2.csv"
OUTPUT_CSV = "./data/wiki_db_cleaned_2.csv"
COVERAGE_CSV = "./data/wiki_db_column_coverage.csv"

#%%
# =========================
# Load data
# =========================
df = pd.read_csv(INPUT_CSV)

print("Original shape:", df.shape)

#%%
# =========================
# Drop unnecessary columns
# =========================
DROP_COLS = [
    "movie",
    "qid"
]

df = df.drop(columns=DROP_COLS, errors="ignore")

print("After dropping columns:", df.shape)

#%%
# =========================
# Unit normalization
# runtime_minutes -> hours
# =========================
#%% 找出 'runtime_dbpedia' 欄位有值的列
non_null_runtime_rows = df[df['runtime_dbpedia'].notna()]
print(non_null_runtime_rows[['runtime', 'runtime_dbpedia']])

#%%
df["runtime_dbpedia"] = df["runtime_dbpedia"] / 60

#%%
# =========================
# Column coverage statistics
# =========================
coverage_df = pd.DataFrame({
    "non_null_count": df.notnull().sum(),
    "coverage_ratio": df.notnull().mean(),
    "total_rows": len(df)
}).sort_values("coverage_ratio", ascending=False)

print("\nColumn coverage:")
print(coverage_df)

#%%
# =========================
# Check data format issues
# =========================
#%% 找出欄位有值的列
columns_to_check = df.columns

for col in columns_to_check:
    non_null_rows = df[df[col].notna()]
    print(f"\nNon-null rows for column '{col}':")
    print(non_null_rows[[col]].head(10))

#%% transform year_dbpedia to integer
df['year_dbpedia'] = df['year_dbpedia'].astype('Int64')

#%% transform runtime_dbpedia to absolute values
df['runtime_dbpedia'] = df['runtime_dbpedia'].abs()

#%% 找出兩個欄位值不相等的列
column_1 = 'actors'
column_2 = 'actors_dbpedia'
not_null_df = df[df[column_1].notna() & df[column_2].notna()]
different_values_df = not_null_df[not_null_df[column_1] != not_null_df[column_2]]
pd.set_option('display.max_rows', None)
print(different_values_df[[column_1, column_2]])

#%% Drop title_dbpedia, year_dbpedia columns due to redundancy
DROP_COLS = [
    "title_dbpedia",
    "year_dbpedia"
]

df = df.drop(columns=DROP_COLS, errors="ignore")

#%% 取 'runtime' 和 'runtime_dbpedia' 兩個欄位值的平均值，並更新回這兩個欄位
condition1 = df['runtime'] != df['runtime_dbpedia']
condition2 = df['runtime'].notna()
condition3 = df['runtime_dbpedia'].notna()
rows_to_update_mask = condition1 & condition2 & condition3
average_runtime = (df.loc[rows_to_update_mask, 'runtime'] + df.loc[rows_to_update_mask, 'runtime_dbpedia']) / 2
df.loc[rows_to_update_mask, 'runtime'] = average_runtime

#%% Conditional completeness: A has value, B is missing
def count_A_notnull_B_null(df, col_A, col_B):
    if col_A not in df.columns or col_B not in df.columns:
        return None
    return df[df[col_A].notnull() & df[col_B].isnull()].shape[0]

conditional_stats = {
    "dbpedia_notnull_wikidata_null_runtime":
        count_A_notnull_B_null(df, "runtime_dbpedia", "runtime"),
    "dbpedia_notnull_wikidata_null_directors":
        count_A_notnull_B_null(df, "directors_dbpedia", "directors"),
    "dbpedia_notnull_wikidata_null_actors":
        count_A_notnull_B_null(df, "actors_dbpedia", "actors")
}

print("\nConditional completeness:")
for k, v in conditional_stats.items():
    print(f"{k}: {v}")

#%% Drop redundant dbpedia columns after merging
print("Before dropping columns:", df.shape)
DROP_COLS = [
    "runtime_dbpedia",
    "directors_dbpedia",
    "actors_dbpedia"
]
df = df.drop(columns=DROP_COLS, errors="ignore")
print("After dropping columns:", df.shape)



#%%
# =========================
# Save results
# =========================
df.to_csv(OUTPUT_CSV, index=False)
# coverage_df.to_csv(COVERAGE_CSV)

print("\nSaved cleaned data to:", OUTPUT_CSV)
print("Saved coverage stats to:", COVERAGE_CSV)