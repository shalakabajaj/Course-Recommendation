import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Stopwords (removed "server" to preserve 'sql server' phrase)
STOPWORDS = {
    "system", "course", "online", "learn",
    "developer", "development", "introduction",
    "intro", "basics", "fundamentals",
    "beginner", "advanced"
}

# Load dataset (adjust path if needed)

DATA_PATH = "data/processed/unified_courses.csv"
courses_df = pd.read_csv(DATA_PATH)

def preprocess_text(text: str) -> str:
    """
    Lowercase text and remove generic stopwords while preserving meaningful terms.
    """
    if not isinstance(text, str):
        return ""
    words = [w for w in text.lower().split() if w not in STOPWORDS]
    return " ".join(words)

# Use existing text_for_tfidf column if available

if "text_for_tfidf" in courses_df.columns:
    courses_df["processed_text"] = courses_df["text_for_tfidf"].apply(preprocess_text)
else:
    courses_df["processed_text"] = (
        courses_df["title"].fillna("") + " " +
        courses_df["description"].fillna("") + " " +
        courses_df["skills"].fillna("")
    ).apply(preprocess_text)

# Build TF-IDF vectorizer with bigrams (phrase handling)
vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(courses_df["processed_text"])

def recommend_courses(query: str, top_n: int = 30) -> pd.DataFrame:
    """
    Recommend top-N courses for the given query using TF-IDF bigrams, cosine similarity,
    and keyword/phrase boosting for exact matches.
    """
    filtered_query = preprocess_text(query)
    if not filtered_query.strip():
        filtered_query = query.lower()

    # Transform query into vector
    query_vec = vectorizer.transform([filtered_query])

    # Compute similarity scores
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Phrase boosting: exact query phrase in original text gets a boost
    phrase = query.strip().lower()
    mask = courses_df["processed_text"].str.contains(fr"\b{re.escape(phrase)}\b", case=False, regex=True)
    scores[mask] *= 1.3  # 30% boost for exact matches

    courses_df["similarity"] = scores
    ranked = courses_df.sort_values(by="similarity", ascending=False)

    return ranked.head(top_n)[[
        "course_id", "title", "url", "provider", "level", "duration",
        "rating", "is_paid", "subscribers", "reviews", "lectures",
        "subject", "similarity"
    ]].copy()

# Test Run Section

if __name__ == "__main__":
    sample_queries = ["sql server", "java", "python data analysis"]
    for q in sample_queries:
        print(f"\n🔎 Top recommendations for: '{q}'\n")
        try:
            recs = recommend_courses(q, top_n=5)
            for _, row in recs.iterrows():
                print(f"{row['title']} (Provider: {row['provider']}, Similarity: {row['similarity']:.3f})")
        except Exception as e:
            print(f"❌ Error for '{q}': {e}")
