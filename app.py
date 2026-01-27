import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set page title and layout
st.set_page_config(page_title="Social Media Dashboard", layout="wide")

st.title("📊 Social Media Performance Dashboard")

# --- 1. DATA LOADING, CLEANING & AUTO-DELETE ---
def load_and_prune_data():
    # Load the file
    df = pd.read_csv('dashboard - Company.csv')
    
    # Remove empty "Unnamed" columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean numeric columns
    metrics = ['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']
    for col in metrics:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Clean Date Column
    df['Date Published'] = pd.to_datetime(df['Date Published'], errors='coerce')
    
    # --- AUTO-DELETE LOGIC ---
    # Calculate the cutoff (14 days ago from today)
    cutoff_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=14)
    
    # Identify old posts
    initial_count = len(df)
    df = df[df['Date Published'] >= cutoff_date]
    deleted_count = initial_count - len(df)
    
    # If posts were removed, overwrite the CSV file to make it permanent
    if deleted_count > 0:
        df.to_csv('dashboard - Company.csv', index=False)
        st.warning(f"🧹 Auto-Cleanup: Removed {deleted_count} posts older than 14 days (posted before {cutoff_date.strftime('%Y-%m-%d')}).")
    
    # Add Total Engagement
    df['Total Engagement'] = df['Likes'] + df['Comments'] + df['Shares']
    
    return df

# We remove @st.cache_data here so the auto-delete checks every time the page refreshes
df = load_and_prune_data()

# --- 2. SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters")
platforms = st.sidebar.multiselect(
    "Filter by Platform:",
    options=df["Platform"].unique(),
    default=df["Platform"].unique()
)

# Apply filters
filtered_df = df[df["Platform"].isin(platforms)]

# --- 3. KEY METRIC CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)
# Using filtered_df for metrics to reflect sidebar choices
col1.metric("Total Views", int(filtered_df["Views"].sum()))
col2.metric("Total Likes", int(filtered_df["Likes"].sum()))
col3.metric("Comments", int(filtered_df["Comments"].sum()))
col4.metric("Shares", int(filtered_df["Shares"].sum()))
col5.metric("Followers Gained", int(filtered_df["New Follow Count"].sum()))

st.markdown("---")

# --- 4. DASHBOARD VISUALS ---
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Cumulative Metrics Summary")
    metrics_melted = filtered_df[['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']].sum().reset_index()
    metrics_melted.columns = ['Metric', 'Total']
    fig_metrics = px.bar(metrics_melted, x="Metric", y="Total", color="Metric", text_auto=True, template="plotly_white")
    st.plotly_chart(fig_metrics, use_container_width=True)

with row1_col2:
    st.subheader("Engagement by Topic Category")
    topic_eng = filtered_df.groupby('Topic Category')['Total Engagement'].sum().reset_index()
    fig_topic = px.bar(topic_eng, x="Total Engagement", y="Topic Category", orientation='h', color="Topic Category")
    st.plotly_chart(fig_topic, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Shares per Platform")
    shares_df = filtered_df.groupby("Platform")["Shares"].sum().reset_index()
    fig_shares = px.bar(shares_df, x="Platform", y="Shares", color="Platform", text_auto=True)
    st.plotly_chart(fig_shares, use_container_width=True)

with row2_col2:
    st.subheader("Views Distribution by Category")
    fig_pie = px.pie(filtered_df, values='Views', names='Topic Category', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- 5. DATA EDITOR (Detailed Content Breakdown) ---
st.subheader("Detailed Content Breakdown")
st.info("Edit cells below and click 'Save Changes'. Posts older than 14 days are automatically removed on refresh.")

# We show the full dataframe (df) in the editor so you can see everything before saving
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

if st.button("Save Changes"):
    edited_df.to_csv('dashboard - Company.csv', index=False)
    st.success("Data saved successfully!")
    st.rerun()