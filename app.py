import streamlit as st
from utils import extract_video_id, get_video_details, get_comments
from transformers import pipeline
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

def preprocess_comments(comments):
    cleaned = []
    for comment in comments:
        # Remove emojis, URLs, and non-alphabetic characters
        comment = re.sub(r"http\S+|[^a-zA-Z\s]", "", comment)
        comment = comment.lower().strip()
        if comment:
            cleaned.append(comment)
    return cleaned


st.set_page_config(page_title="YouTube Engagement Analyzer", layout="wide")
st.title("📊 YouTube Engagement Analyzer")

api_key = st.secrets["YOUTUBE_API_KEY"]  # Store securely in Streamlit secrets

url = st.text_input("Paste a YouTube video URL")

if url:
    video_id = extract_video_id(url)
    if video_id:
        details = get_video_details(video_id, api_key)
        st.subheader(details['snippet']['title'])
        st.write(f"📅 Published: {details['snippet']['publishedAt']}")
        st.write(f"👍 Likes: {details['statistics'].get('likeCount', 'N/A')}")
        st.write(f"💬 Comments: {details['statistics'].get('commentCount', 'N/A')}")

        comments = get_comments(video_id, api_key)
        st.write(f"Fetched {len(comments)} comments")

        # Sentiment Analysis
        sentiment_model = pipeline("sentiment-analysis", truncation=True)
        sentiments = sentiment_model(comments)

        pos = sum(1 for s in sentiments if s['label'] == 'POSITIVE')
        neg = sum(1 for s in sentiments if s['label'] == 'NEGATIVE')
        st.write(f"😊 Positive: {pos}, 😠 Negative: {neg}")

        filtered_comments = preprocess_comments(comments)
        cleaned_text = " ".join(filtered_comments).strip()

        # Word Cloud
        if cleaned_text:
            wc = WordCloud(width=800, height=400).generate(cleaned_text)
            st.subheader("🗣️ Comment Word Cloud")
            fig, ax = plt.subplots()
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("No valid words found in comments to generate a word cloud.")