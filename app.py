import re
from collections import Counter

import streamlit as st
import pandas as pd
import altair as alt


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Podcast Sentiment Explorer",
    layout="wide"
)

st.title("🎧 Podcast Sentiment Explorer")
st.caption(
    "Sentiment and feedback insights from podcast comments. "
    "Upload a CSV to explore sentiment, keywords, and the underlying conversation."
)


# -----------------------------
# Sidebar: Upload + options
# -----------------------------
st.sidebar.header("📁 Dataset")
st.sidebar.caption("Tip: add an `episode_title` column to enable episode-level filtering.")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

DEFAULT_FILE = "podcast_sentiment_demo.csv"


@st.cache_data
def load_csv_from_upload(file) -> pd.DataFrame:
    return pd.read_csv(file)


@st.cache_data
def load_csv_from_path(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


# Load data
if uploaded_file is not None:
    df = load_csv_from_upload(uploaded_file)
    st.success("Loaded data from uploaded CSV ✅")
else:
    try:
        df = load_csv_from_path(DEFAULT_FILE)
        st.success(f"Loaded demo data: `{DEFAULT_FILE}` ✅")
    except FileNotFoundError:
        st.error(f"No CSV uploaded and default file `{DEFAULT_FILE}` not found.")
        st.stop()


# -----------------------------
# Basic checks / normalization
# -----------------------------
# We expect at least a text column; we try common alternatives
TEXT_COL_CANDIDATES = ["text", "comment", "comment_text", "body"]
text_col = next((c for c in TEXT_COL_CANDIDATES if c in df.columns), None)

if text_col is None:
    st.error(
        "I couldn't find a comment text column.\n\n"
        "Your CSV needs a column named one of: `text`, `comment`, `comment_text`, `body`."
    )
    st.stop()

# Normalize to 'text' internally (without overwriting original)
df["_text"] = df[text_col].astype(str)

# Sentiment label column
SENT_COL_CANDIDATES = ["bert_label_norm", "sentiment", "label"]
sent_col = next((c for c in SENT_COL_CANDIDATES if c in df.columns), None)

if sent_col is None:
    st.warning(
        "No sentiment column found (expected `bert_label_norm` or `sentiment`). "
        "This demo will still work for keyword search, but sentiment features will be limited."
    )
    df["_sentiment"] = "unknown"
else:
    df["_sentiment"] = df[sent_col].astype(str).str.lower().str.strip()

# Episode column (optional)
EPISODE_COL = "episode_title"
has_episode = EPISODE_COL in df.columns

if has_episode:
    df["_episode"] = df[EPISODE_COL].astype(str)
else:
    df["_episode"] = "All comments"


# -----------------------------
# Episode filter (if available)
# -----------------------------
episode_choice = None
if has_episode:
    episode_list = ["All episodes"] + sorted(df["_episode"].dropna().unique().tolist())
    episode_choice = st.sidebar.selectbox("🎙️ Choose episode", options=episode_list)

    if episode_choice != "All episodes":
        df = df[df["_episode"] == episode_choice].copy()
        st.sidebar.success(f"Showing: {episode_choice}")
else:
    st.sidebar.info("This dataset contains a single episode. Add `episode_title` for episode filtering.")


# -----------------------------
# Overview (KPIs + chart)
# -----------------------------
st.markdown("## Overview")

total_comments = len(df)

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total comments", total_comments)

def pct_for(label: str) -> float:
    if total_comments == 0:
        return 0.0
    return (df["_sentiment"].eq(label).sum() / total_comments) * 100

pos_pct = pct_for("positive")
neu_pct = pct_for("neutral")
neg_pct = pct_for("negative")

# Only show meaningful sentiment KPIs if we have real sentiment labels
if sent_col is not None:
    col2.metric("😊 Positive %", f"{pos_pct:.1f}%")
    col3.metric("😐 Neutral %", f"{neu_pct:.1f}%")
    col4.metric("😡 Negative %", f"{neg_pct:.1f}%")
else:
    col2.metric("😊 Positive %", "—")
    col3.metric("😐 Neutral %", "—")
    col4.metric("😡 Negative %", "—")


# Sentiment chart
st.markdown("## Sentiment distribution")

sent_counts = (
    df.groupby("_sentiment")
      .size()
      .reset_index(name="count")
      .sort_values("count", ascending=False)
)

if not sent_counts.empty:
    sent_counts["percentage"] = (sent_counts["count"] / max(total_comments, 1) * 100).round(2)

    chart = (
        alt.Chart(sent_counts)
        .mark_bar()
        .encode(
            x=alt.X("_sentiment:N", title="Sentiment", sort="-y"),
            y=alt.Y("count:Q", title="Number of comments"),
            tooltip=["_sentiment", "count", "percentage"]
        )
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No rows to chart.")


# -----------------------------
# Keyword Intelligence
# -----------------------------
st.markdown("## Keywords")
st.caption(
    "**Top N keywords** means: show the **N most frequent words/phrases** in the comments. "
    "The slider controls how many keywords you want to see (e.g., Top 10 vs Top 30)."
)

# Simple stopwords list (you can expand later)
STOPWORDS = set("""
a an and are as at be but by for from has have he her hers him his i if in into is it its
just me my no not of on or our ours she so that the their them then there these they this to
too up was we were what when where which who will with you your yours
""".split())

def tokenize(text: str):
    # remove URLs
    text = re.sub(r"http\S+|www\.\S+", " ", text.lower())
    # keep words only
    words = re.findall(r"[a-zA-Z']+", text)
    return words

@st.cache_data
def extract_top_keywords(series: pd.Series, top_n: int, min_len: int = 3):
    tokens = []
    for t in series.dropna().astype(str):
        for w in tokenize(t):
            if len(w) < min_len:
                continue
            if w in STOPWORDS:
                continue
            if w.isnumeric():
                continue
            tokens.append(w)

    counts = Counter(tokens)
    top = counts.most_common(top_n)
    return pd.DataFrame(top, columns=["keyword", "count"])

top_n = st.slider("Top N keywords", min_value=5, max_value=50, value=20, step=1)
min_len = st.slider("Minimum word length", min_value=2, max_value=6, value=3, step=1)

# Keyword tables by sentiment
if sent_col is None:
    st.info("No sentiment column detected, so keywords are shown for all comments combined.")
    kw_all = extract_top_keywords(df["_text"], top_n=top_n, min_len=min_len)
    st.dataframe(kw_all, use_container_width=True)
else:
    kw_cols = st.columns(3)
    for col, label in zip(kw_cols, ["positive", "neutral", "negative"]):
        subset = df[df["_sentiment"] == label]
        with col:
            st.subheader(label.title())
            kw = extract_top_keywords(subset["_text"], top_n=top_n, min_len=min_len)
            if kw.empty:
                st.write("No keywords found.")
            else:
                st.dataframe(kw, use_container_width=True)


# -----------------------------
# Keyword drilldown (pick a keyword -> see matching comments)
# -----------------------------
st.markdown("## Keyword drilldown")
st.caption("Pick a keyword to instantly view the comments that contain it.")

# Build a keyword list from all comments (fast enough for demo datasets)
kw_all = extract_top_keywords(df["_text"], top_n=50, min_len=min_len)
keyword_options = ["(none)"] + kw_all["keyword"].tolist()

chosen_kw = st.selectbox("Choose a keyword", options=keyword_options)

drill_df = df.copy()
if chosen_kw != "(none)":
    drill_df = drill_df[drill_df["_text"].str.contains(chosen_kw, case=False, na=False)].copy()

st.write(f"Matching comments: **{len(drill_df)}**")

# Choose columns to show (only include if they exist)
cols_to_show = []
for c in ["_episode", "author", "_text", "_sentiment", "bert_score", "vader_label", "vader_score", "published_at", "like_count"]:
    if c in drill_df.columns:
        cols_to_show.append(c)

# if author column isn't in dataset, we'll still show key columns
if "author" not in drill_df.columns:
    cols_to_show = [c for c in cols_to_show if c != "author"]

# fallback if nothing matched
if not cols_to_show:
    cols_to_show = drill_df.columns.tolist()

st.dataframe(drill_df[cols_to_show].rename(columns={"_text": "text", "_sentiment": "sentiment", "_episode": "episode_title"}), use_container_width=True)


# -----------------------------
# Explore comments (sentiment + text search)
# -----------------------------
st.markdown("## Explore comments")
left, right = st.columns([2, 3])

with left:
    if sent_col is not None:
        sentiment_choice = st.radio(
            "Filter by sentiment:",
            options=["all", "positive", "neutral", "negative"],
            horizontal=True
        )
    else:
        sentiment_choice = "all"
        st.info("Sentiment filter disabled (no sentiment column found).")

with right:
    query = st.text_input(
        "Search in comment text (optional)",
        value="",
        placeholder="Type a keyword or phrase..."
    )

filtered_df = df.copy()

if sent_col is not None and sentiment_choice != "all":
    filtered_df = filtered_df[filtered_df["_sentiment"] == sentiment_choice]

if query.strip():
    filtered_df = filtered_df[filtered_df["_text"].str.contains(query.strip(), case=False, na=False)]

st.write(f"Showing **{len(filtered_df)}** comments")

cols_to_show2 = []
for c in ["_episode", "author", "_text", "_sentiment", "bert_score", "vader_label", "vader_score", "published_at", "like_count"]:
    if c in filtered_df.columns:
        cols_to_show2.append(c)

if not cols_to_show2:
    cols_to_show2 = filtered_df.columns.tolist()

st.dataframe(
    filtered_df[cols_to_show2].rename(columns={"_text": "text", "_sentiment": "sentiment", "_episode": "episode_title"}),
    use_container_width=True
)


# -----------------------------
# Raw preview
# -----------------------------
with st.expander("Raw data preview (first 50 rows)"):
    st.dataframe(df.head(50), use_container_width=True)
