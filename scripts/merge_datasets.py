import pandas as pd
from pathlib import Path

# ============================
# Paths
# ============================
udemy_cleaned_path = Path("data/processed/udemy_cleaned.csv")
coursera_cleaned_path = Path("data/processed/coursera_cleaned.csv")
output_path = Path("data/processed/unified_courses.csv")

# ============================
# 📥 Load Cleaned Datasets
# ============================
udemy_df = pd.read_csv(udemy_cleaned_path)
coursera_df = pd.read_csv(coursera_cleaned_path)

print(f"📊 Udemy Cleaned Shape: {udemy_df.shape}")
print(f"📊 Coursera Cleaned Shape: {coursera_df.shape}")

# ============================
# Validation Checks (Safety)
# ============================
# These are duplicates of cleaning-stage checks, kept here for extra safety
for name, df in [("Udemy", udemy_df), ("Coursera", coursera_df)]:
    if df["title"].isna().any():
        raise ValueError(f"❌ {name} dataset contains NaN titles!")
    if df["text_for_tfidf"].isna().any():
        raise ValueError(f"❌ {name} dataset contains NaN values in text_for_tfidf!")
    if df.duplicated().any():
        print(f"⚠️ Warning: {name} dataset still has duplicates.")

# ============================
# Merge Datasets
# ============================
merged_df = pd.concat([udemy_df, coursera_df], ignore_index=True)
merged_df.drop_duplicates(inplace=True)

# ============================
# Save Unified Dataset
# ============================
output_path.parent.mkdir(parents=True, exist_ok=True)
merged_df.to_csv(output_path, index=False)

print(f"\n✅ Datasets merged and saved → {output_path}")
print(f"📏 Final merged shape: {merged_df.shape}")

# ============================
# 🔎 Preview
# ============================
print("\n🔍 Merged Dataset Sample:")
print(merged_df.head(3))
print("\n📋 Merged Dataset Columns:")
print(list(merged_df.columns))
