import pandas as pd
import os

# ---------------------------
# Paths
# ---------------------------
udemy_input = "data/raw/udemy_courses.csv"
coursera_input = "data/raw/coursera_courses.csv"

udemy_output = "data/processed/udemy_cleaned.csv"
coursera_output = "data/processed/coursera_cleaned.csv"

os.makedirs("data/processed", exist_ok=True)

# =====================================================
# 🟢  UDEMY CLEANING
# =====================================================
udemy_df = pd.read_csv(udemy_input)

udemy_cleaned = udemy_df[[
    "course_id", "course_title", "url", "is_paid", "price",
    "num_subscribers", "num_reviews", "num_lectures",
    "level", "content_duration", "published_timestamp", "subject"
]].copy()

# Rename to common names
udemy_cleaned.rename(columns={
    "course_title": "title",
    "content_duration": "duration",
    "num_subscribers": "subscribers",
    "num_reviews": "reviews",
    "num_lectures": "lectures",
}, inplace=True)

# Add missing columns for consistency
udemy_cleaned["provider"] = "Udemy"
udemy_cleaned["rating"] = None
udemy_cleaned["description"] = None
udemy_cleaned["skills"] = udemy_cleaned["subject"]

# Combined text for TF-IDF (lowercase)
udemy_cleaned["text_for_tfidf"] = (
    udemy_cleaned["title"].fillna("") + " " +
    udemy_cleaned["subject"].fillna("")
).str.lower()

udemy_cleaned.drop_duplicates(inplace=True)

# ✅ Validation checks
assert udemy_cleaned["title"].notna().all(), "❌ Udemy: Missing values found in 'title'."
assert udemy_cleaned["text_for_tfidf"].notna().all(), "❌ Udemy: Missing values found in 'text_for_tfidf'."

# Save cleaned Udemy data
udemy_cleaned.to_csv(udemy_output, index=False)
print(f"✅ Cleaned Udemy dataset saved → {udemy_output}")
print(f"Udemy Shape: {udemy_cleaned.shape}")
print("Udemy Sample:")
print(udemy_cleaned.head(2))  # Preview first 2 rows

# =====================================================
# 🟢  COURSERA CLEANING
# =====================================================
coursera_df = pd.read_csv(coursera_input)

coursera_cleaned = pd.DataFrame({
    "title": coursera_df["Course Name"],
    "provider": coursera_df["University"],
    "level": coursera_df["Difficulty Level"],
    "rating": coursera_df["Course Rating"],
    "url": coursera_df["Course URL"],
    "description": coursera_df["Course Description"],
    "skills": coursera_df["Skills"],
})

# Add placeholders for missing columns
for col in ["price", "is_paid", "subscribers", "reviews",
            "lectures", "duration", "published_timestamp", "subject"]:
    if col == "subject":
        coursera_cleaned[col] = coursera_cleaned["skills"].apply(
            lambda x: str(x).split(",")[0] if pd.notna(x) else None
        )
    else:
        coursera_cleaned[col] = None

# Combined text for TF-IDF (lowercase)
coursera_cleaned["text_for_tfidf"] = (
    coursera_cleaned["title"].fillna("") + " " +
    coursera_cleaned["description"].fillna("") + " " +
    coursera_cleaned["skills"].fillna("") + " " +
    coursera_cleaned["subject"].fillna("")
).str.lower()

coursera_cleaned.drop_duplicates(inplace=True)

# ✅ Validation checks
assert coursera_cleaned["title"].notna().all(), "❌ Coursera: Missing values found in 'title'."
assert coursera_cleaned["text_for_tfidf"].notna().all(), "❌ Coursera: Missing values found in 'text_for_tfidf'."

# Save cleaned Coursera data
coursera_cleaned.to_csv(coursera_output, index=False)
print(f"\n✅ Cleaned Coursera dataset saved → {coursera_output}")
print(f"Coursera Shape: {coursera_cleaned.shape}")
print("Coursera Sample:")
print(coursera_cleaned.head(2))  # Preview first 2 rows

# =====================================================
# ✅ Summary
# =====================================================
print("\n📝 Cleaning complete: Both datasets validated and ready for TF-IDF.")
