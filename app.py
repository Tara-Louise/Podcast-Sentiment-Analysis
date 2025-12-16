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
st.caption("Sentiment and feedback insights from podcast comments. Upload a CSV to explore sentiment, keywords, and the underlying conversation.")

st.sidebar.header("Dataset")


st.sidebar.caption("Tip: add an `episode_title` column to enable episode-level filtering.")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])


@st.cache_data
def load_data_from_upload(file) -> pd.DataFrame:
    return pd.read_csv(file)

@st.cache_data
def load_data_from_path(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

DEFAULT_FILE = "sentiment_with_aggregation.csv"

if uploaded_file is not None:
    df = load_data_from_upload(uploaded_file)
    st.success("Loaded data from uploaded CSV")
else:
    try:
        df = load_data_from_path(DEFAULT_FILE)
        st.success(f"Loaded {len(df)} rows from `{DEFAULT_FILE}`")
    except FileNotFoundError:
        st.error(f"No CSV uploaded and default file `{DEFAULT_FILE}` not found.")
        st.stop()

# -----------------------------
# Optional: episode dropdown
# -----------------------------
# ── Episode-level filtering (optional) ───────────────────────────

if "episode_title" in df.columns:
    episode = st.sidebar.selectbox(
        "Select episode",
        options=sorted(df["episode_title"].unique())
    )
    df = df[df["episode_title"] == episode]
else:
    st.sidebar.info(
        "This dataset contains a single episode. "
        "Add an `episode_title` column to enable episode-level filtering."
    )

# -----------------------------
# Validate sentiment column
# -----------------------------
if "bert_label_norm" not in df.columns:
    st.error("Column `bert_label_norm` not found. Your CSV needs this column for sentiment.")
    st.stop()

total_comments = len(df)

# -----------------------------
# Aggregation
# -----------------------------
sent_counts = (
    df.groupby("bert_label_norm")
      .size()
      .reset_index(name="count")
)

sent_counts["percentage"] = (sent_counts["count"] / total_comments * 100).round(2)

def get_pct(label: str) -> float:
    row = sent_counts.loc[sent_counts["bert_label_norm"] == label, "percentage"]
    return float(row.iloc[0]) if not row.empty else 0.0

pos_pct = get_pct("positive")
neu_pct = get_pct("neutral")
neg_pct = get_pct("negative")

# -----------------------------
# KPI cards
# -----------------------------
st.markdown("## Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total comments", total_comments)
col2.metric("😊 Positive %", f"{pos_pct:.1f}%")
col3.metric("😐 Neutral %", f"{neu_pct:.1f}%")
col4.metric("😡 Negative %", f"{neg_pct:.1f}%")

# -----------------------------
# Chart
# -----------------------------
st.markdown("## Sentiment distribution")

chart_data = sent_counts.rename(columns={"bert_label_norm": "label"})

chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("label:N", title="Sentiment"),
        y=alt.Y("count:Q", title="Number of comments"),
        tooltip=["label", "count", "percentage"]
    )
)

st.altair_chart(chart, use_container_width=True)

# -----------------------------
# Explore comments (filter + search + download)
# -----------------------------
st.markdown("## Explore comments")

sentiment_choice = st.radio(
    "Filter by sentiment:",
    options=["all", "positive", "neutral", "negative"],
    horizontal=True
)

keyword = st.text_input("Search in comment text (optional)").strip().lower()

filtered_df = df.copy()

if sentiment_choice != "all":
    filtered_df = filtered_df[filtered_df["bert_label_norm"] == sentiment_choice]

if keyword:
    filtered_df = filtered_df[
        filtered_df["text"].astype(str).str.lower().str.contains(keyword, na=False)
    ]

st.write(f"Showing **{len(filtered_df)}** comments")

cols_to_show = ["author", "text", "bert_label_norm"]
if "bert_score" in filtered_df.columns:
    cols_to_show.append("bert_score")
if "vader_label" in filtered_df.columns:
    cols_to_show.append("vader_label")
if "vader_score" in filtered_df.columns:
    cols_to_show.append("vader_score")
if "published_at" in filtered_df.columns:
    cols_to_show.append("published_at")
if "like_count" in filtered_df.columns:
    cols_to_show.append("like_count")

st.dataframe(filtered_df[cols_to_show], use_container_width=True)

csv_export = filtered_df[cols_to_show].to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download filtered comments as CSV",
    data=csv_export,
    file_name=f"comments_{sentiment_choice}.csv",
    mime="text/csv"
)

# -----------------------------
# Raw preview
# -----------------------------
st.markdown("## Raw data preview")
st.dataframe(df.head(50), use_container_width=True)
