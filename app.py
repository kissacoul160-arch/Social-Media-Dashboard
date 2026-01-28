import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Social Media Dashboard 🎀", layout="wide")

# --- 2. THE COQUETTE GLUE (CSS with !important for lace, cursive, and pink) ---
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&family=Playfair+Display:ital@1&display=swap" rel="stylesheet">
    
    <style>
    /* 1. BACKGROUND & LACE */
    .stApp {
        background-color: #FFF5F7 !important;
        background-image: url("https://www.transparenttextures.com/patterns/white-lace.png") !important;
        background-attachment: fixed !important;
    }

    /* 2. CURSIVE TITLES */
    h1 {
        font-family: 'Great Vibes', cursive !important;
        color: #D4778B !important;
        font-size: 5rem !important;
        text-align: center !important;
        font-weight: 400 !important;
    }
    
    h2, h3, .stSubheader {
        font-family: 'Dancing Script', cursive !important;
        color: #D4778B !important;
        font-size: 2.5rem !important;
    }

    /* 3. COQUETTE METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 2px dashed #FFC1CC !important;
        border-radius: 30px !important;
        padding: 20px !important;
        box-shadow: 0px 10px 15px rgba(212, 119, 139, 0.1) !important;
    }

    /* 4. METRIC FONT STYLING */
    div[data-testid="stMetricLabel"] > div {
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.8rem !important;
        color: #D4778B !important;
    }
    
    div[data-testid="stMetricValue"] > div {
        font-family: 'Playfair Display', serif !important;
        color: #FF85A2 !important;
    }

    /* 5. SIDEBAR STYLE */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 228, 232, 1) !important;
        border-right: 5px double #FFC1CC !important;
    }

    /* 6. PINK BUTTONS */
    .stButton > button {
        background-color: #FFC1CC !important;
        color: white !important;
        border-radius: 50px !important;
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.5rem !important;
        border: 2px solid #FFF !important;
        padding: 8px 30px !important;
    }

    /* 7. CUSTOM DIVIDER */
    hr {
        border: 0;
        height: 3px;
        background-image: linear-gradient(to right, transparent, #FFC1CC, transparent) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. DATA LOADING & AUTO-DELETE (14 DAYS) ---
def load_and_prune_data():
    df = pd.read_csv('dashboard - Company.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    metrics = ['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']
    for col in metrics:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Date Published'] = pd.to_datetime(df['Date Published'], errors='coerce')
    
    # Auto-delete older than 14 days
    cutoff_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=14)
    df = df[df['Date Published'] >= cutoff_date]
    
    df['Total Engagement'] = df['Likes'] + df['Comments'] + df['Shares']
    return df

df = load_and_prune_data()

# --- 4. SIDEBAR ---
st.sidebar.header("Dashboard Filters")
platforms = st.sidebar.multiselect(
    "Filter by Platform:",
    options=df["Platform"].unique(),
    default=df["Platform"].unique()
)
filtered_df = df[df["Platform"].isin(platforms)]

# --- 5. MAIN DASHBOARD CONTENT (ORIGINAL TITLES) ---
st.title("Social Media Performance Dashboard")

# Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Views", f"{int(filtered_df['Views'].sum()):,}")
col2.metric("Total Likes", int(filtered_df["Likes"].sum()))
col3.metric("Comments", int(filtered_df["Comments"].sum()))
col4.metric("Shares", int(filtered_df["Shares"].sum()))
col5.metric("Followers Gained", int(filtered_df["New Follow Count"].sum()))

st.markdown("<hr>", unsafe_allow_html=True)

# --- 6. VISUALS (COQUETTE PALETTE) ---
coquette_palette = ["#FFC1CC", "#FFD1DC", "#FFB7C5", "#E0B0FF", "#FADADD"]

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Cumulative Metrics Summary")
    metrics_melted = filtered_df[['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']].sum().reset_index()
    metrics_melted.columns = ['Metric', 'Total']
    fig1 = px.bar(metrics_melted, x="Metric", y="Total", color="Metric", text_auto=True, color_discrete_sequence=coquette_palette)
    fig1.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Georgia")
    st.plotly_chart(fig1, use_container_width=True)

with row1_col2:
    st.subheader("Engagement by Topic Category")
    topic_eng = filtered_df.groupby('Topic Category')['Total Engagement'].sum().reset_index()
    fig2 = px.bar(topic_eng, x="Total Engagement", y="Topic Category", orientation='h', color="Topic Category", color_discrete_sequence=coquette_palette[::-1])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Georgia")
    st.plotly_chart(fig2, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Shares per Platform")
    shares_df = filtered_df.groupby("Platform")["Shares"].sum().reset_index()
    fig3 = px.bar(shares_df, x="Platform", y="Shares", color="Platform", color_discrete_sequence=coquette_palette)
    st.plotly_chart(fig3, use_container_width=True)

with row2_col2:
    st.subheader("Views Distribution by Category")
    fig4 = px.pie(filtered_df, values='Views', names='Topic Category', hole=0.5, color_discrete_sequence=coquette_palette)
    fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- 7. DATA EDITOR ---
st.subheader("Detailed Content Breakdown")
st.info("Edit your content metrics below and save to update the charts. ✨")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Save Changes"):
    edited_df.to_csv('dashboard - Company.csv', index=False)
    st.success("Data successfully updated!")
    st.rerun()