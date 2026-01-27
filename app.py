import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Social Media Dashboard 🎀", layout="wide")

# 2. Custom CSS for the Coquette Vibe + Cursive
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&family=Playfair+Display:ital@1&display=swap');

    /* Background: Lace Pattern Over Pink */
    .stApp {
        background-color: #FFF5F7;
        background-image: url("https://www.transparenttextures.com/patterns/white-lace.png");
        background-attachment: fixed;
    }
    
    /* Main Title */
    h1 {
        color: #D4778B !important;
        font-family: 'Great Vibes', cursive;
        font-size: 4rem !important;
        text-align: center;
        text-shadow: 2px 2px 5px rgba(255, 193, 204, 0.5);
    }
    
    /* Section Titles */
    h2, h3 {
        color: #D4778B !important;
        font-family: 'Dancing Script', cursive;
        font-size: 2.2rem !important;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.75);
        border: 2px dashed #FFC1CC;
        border-radius: 35px !important;
        padding: 20px;
        box-shadow: 0px 8px 15px rgba(212, 119, 139, 0.1);
        backdrop-filter: blur(5px);
    }

    /* Metric Font Settings */
    [data-testid="stMetricLabel"] {
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.5rem !important;
        color: #D4778B !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        color: #FF85A2 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 228, 232, 0.9) !important;
        border-right: 4px double #FFC1CC;
    }

    /* Buttons */
    .stButton>button {
        background-color: #FFC1CC !important;
        color: white !important;
        border-radius: 50px !important;
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.3rem !important;
        border: 2px solid #FFF !important;
        padding: 8px 35px !important;
    }

    /* Decorative Divider */
    hr {
        border: 0;
        height: 2px;
        background-image: linear-gradient(to right, transparent, #FFC1CC, transparent);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Social Media Performance Dashboard")

# --- DATA LOADING & AUTO-DELETE (14 DAYS) ---
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

# --- SIDEBAR FILTERS ---
st.sidebar.markdown("### Dashboard Filters")
platforms = st.sidebar.multiselect(
    "Filter by Platform:",
    options=df["Platform"].unique(),
    default=df["Platform"].unique()
)
filtered_df = df[df["Platform"].isin(platforms)]

# --- KEY METRIC CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Views", f"{int(filtered_df['Views'].sum()):,}")
col2.metric("Total Likes", int(filtered_df["Likes"].sum()))
col3.metric("Comments", int(filtered_df["Comments"].sum()))
col4.metric("Shares", int(filtered_df["Shares"].sum()))
col5.metric("Followers Gained", int(filtered_df["New Follow Count"].sum()))

st.markdown("<hr>", unsafe_allow_stdio=True)

# --- DASHBOARD VISUALS ---
coquette_palette = ["#FFC1CC", "#FFD1DC", "#FFB7C5", "#E0B0FF", "#FADADD"]

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Cumulative Metrics Summary")
    metrics_melted = filtered_df[['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']].sum().reset_index()
    metrics_melted.columns = ['Metric', 'Total']
    fig_metrics = px.bar(metrics_melted, x="Metric", y="Total", 
                         color="Metric", text_auto=True,
                         color_discrete_sequence=coquette_palette)
    fig_metrics.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Georgia")
    st.plotly_chart(fig_metrics, use_container_width=True)

with row1_col2:
    st.subheader("Engagement by Topic Category")
    topic_eng = filtered_df.groupby('Topic Category')['Total Engagement'].sum().reset_index()
    fig_topic = px.bar(topic_eng, x="Total Engagement", y="Topic Category", 
                       orientation='h', color="Topic Category",
                       color_discrete_sequence=coquette_palette[::-1])
    fig_topic.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Georgia")
    st.plotly_chart(fig_topic, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Shares per Platform")
    shares_df = filtered_df.groupby("Platform")["Shares"].sum().reset_index()
    fig_shares = px.bar(shares_df, x="Platform", y="Shares", color="Platform",
                        color_discrete_sequence=coquette_palette)
    st.plotly_chart(fig_shares, use_container_width=True)

with row2_col2:
    st.subheader("Views Distribution by Category")
    fig_pie = px.pie(filtered_df, values='Views', names='Topic Category', hole=0.5,
                     color_discrete_sequence=coquette_palette)
    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<hr>", unsafe_allow_stdio=True)

# --- DATA EDITOR (Detailed Content Breakdown) ---
st.subheader("Detailed Content Breakdown")
st.info("Edit your content metrics below and save to update the charts. ✨")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Save Changes"):
    edited_df.to_csv('dashboard - Company.csv', index=False)
    st.success("Data successfully updated!")

    st.rerun()
