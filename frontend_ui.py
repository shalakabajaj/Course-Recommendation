import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from recommendation import recommend_courses as get_recommendations  # ✅ Backend

# Page Configuration

st.set_page_config(page_title="Online Course Recommender", layout="wide")

# Feedback File Setup

FEEDBACK_FILE = "course_feedback.csv"
if not os.path.exists(FEEDBACK_FILE):
    pd.DataFrame(columns=["timestamp", "course_title", "rating", "comments"]).to_csv(FEEDBACK_FILE, index=False)

# Custom CSS

st.markdown("""
<style>
    .main-title {font-size: 36px; font-weight: 700; margin-bottom: 0.5rem;}
    .description {font-size: 18px; color: #666;}
    .course-card {
        border: 1px solid #e6e6e6; padding: 1rem; border-radius: 10px;
        background-color: white; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .feedback-section {margin-top: 10px; padding: 0.5rem; background: #f8f9fa; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

# Header

st.markdown('<div class="main-title">🎓 Online Course Recommender System</div>', unsafe_allow_html=True)
st.markdown('<div class="description">Enter your preferences and get the best course recommendations tailored to you.</div>', unsafe_allow_html=True)

# Sidebar Filters (Simplified)

st.sidebar.header("📌 Filter Courses")
keyword = st.sidebar.text_input("🔍 Enter keywords", placeholder="e.g. SQL Server, Data Analysis")
level = st.sidebar.selectbox("📘 Select Level", options=["Any", "Beginner", "Intermediate", "Advanced"])

# Recommendations Section

if st.sidebar.button("🎯 Get Recommendations"):
    st.subheader("📄 Recommended Courses")
    st.success(f"Showing results for: {keyword or 'All'} | Level: {level}")

    try:
        # Fetch recommendations
        results = get_recommendations(keyword or "all", top_n=30)
        if results is None or results.empty:
            st.warning("⚠ No recommendations found.")
            results = pd.DataFrame()

        results = results.copy()
        results.columns = results.columns.str.lower().str.strip()

        # Coerce numeric columns
        for col in ["rating", "subscribers", "reviews", "lectures"]:
            if col in results.columns:
                results[col] = pd.to_numeric(results[col], errors="coerce")

        # Level filter
        if level != "Any" and "level" in results.columns:
            results = results[results["level"].astype(str).str.lower() == level.lower()]

        # Limit to top 10
        results = results.head(10)

        if results.empty:
            st.warning("⚠ No matching courses found. Try adjusting filters.")
        else:
            cols = st.columns(2)
            for i, row in results.iterrows():
                course_title = row.get("title") or row.get("course_title") or "Untitled"
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="course-card">
                        <h4>{course_title}</h4>
                        <p><b>Provider:</b> {row.get('provider','N/A')}<br>
                           <b>Level:</b> {row.get('level','N/A')}<br>
                           <b>Duration:</b> {row.get('duration','N/A')} hrs<br>
                           <b>Rating:</b> ⭐ {row.get('rating','N/A')}<br>
                           <b>Price:</b> {'Paid' if str(row.get('is_paid','')).lower() in ['true','1','yes'] else 'Free'}<br>
                           <b>Subscribers:</b> {row.get('subscribers','N/A')}<br>
                           <b>Reviews:</b> {row.get('reviews','N/A')}<br>
                           <b>Lectures:</b> {row.get('lectures','N/A')}<br>
                           <b>Subject:</b> {row.get('subject','N/A')}</p>
                        <a href="{row.get('url','#')}" target="_blank">🔗 Visit Course</a>
                    </div>
                    """, unsafe_allow_html=True)

                    
    except Exception as e:
        st.error(f"❌ Error fetching recommendations: {e}")

else:
    st.info("Enter your preferences and click the button to get recommendations.")

# Footer

st.markdown("---")
st.caption("✅ Developed as part of MCA Project — Online Course Recommender System")
