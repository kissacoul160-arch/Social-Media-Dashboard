import streamlit as st
import pandas as pd
import plotly.express as px

# Set page title and layout
st.set_page_config(page_title="Social Media Dashboard", layout="wide")

st.title("📊 Social Media Performance Dashboard")

# --- 1. DATA LOADING & CLEANING ---
@st.cache_data
def load_data():
    # Load the file
    df = pd.read_csv('dashboard - Company.csv')
    
    # Remove empty "Unnamed" columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean numeric columns and handle 'n/a' or strings
    metrics = ['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']
    for col in metrics:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Clean Date Column
    df['Date Published'] = pd.to_datetime(df['Date Published'], errors='coerce')
    
    # Add Total Engagement (Sum of Likes, Comments, Shares)
    df['Total Engagement'] = df['Likes'] + df['Comments'] + df['Shares']
    
    return df

df = load_data()

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
col1.metric("Total Views", int(filtered_df["Views"].sum()))
col2.metric("Total Likes", int(filtered_df["Likes"].sum()))
col3.metric("Comments", int(filtered_df["Comments"].sum()))
col4.metric("Shares", int(filtered_df["Shares"].sum()))
col5.metric("Followers Gained", int(filtered_df["New Follow Count"].sum()))

st.markdown("---")

# --- 4. DASHBOARD VISUALS ---

# Row 1: Trends and Topic Performance
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Views Trend (Static Dashboard Metric)")
    fig_trend = px.line(filtered_df.sort_values("Date Published"), 
                        x="Date Published", y="Views", 
                        markers=True, template="plotly_white",
                        color="Platform")
    st.plotly_chart(fig_trend, use_container_width=True)

with row1_col2:
    st.subheader("Engagement by Topic Category")
    topic_eng = filtered_df.groupby('Topic Category')['Total Engagement'].sum().reset_index()
    fig_topic = px.bar(topic_eng, x="Total Engagement", y="Topic Category", 
                       orientation='h', color="Topic Category",
                       title="Likes + Comments + Shares per Topic")
    st.plotly_chart(fig_topic, use_container_width=True)

# Row 2: Cumulative Metrics and Platform Shares
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Cumulative Metrics Summary")
    # Melt the dataframe to make it "long" format for Plotly
    metrics_melted = filtered_df[['Views', 'Likes', 'Comments', 'Shares', 'New Follow Count']].sum().reset_index()
    metrics_melted.columns = ['Metric', 'Total']
    fig_metrics = px.bar(metrics_melted, x="Metric", y="Total", 
                         color="Metric", text_auto=True)
    st.plotly_chart(fig_metrics, use_container_width=True)

with row2_col2:
    st.subheader("Shares per Platform")
    shares_df = filtered_df.groupby("Platform")["Shares"].sum().reset_index()
    fig_shares = px.bar(shares_df, x="Platform", y="Shares", 
                        color="Platform", text_auto=True,
                        title="Total Shares across Platforms")
    st.plotly_chart(fig_shares, use_container_width=True)

# --- 5. DATA EXPLORER ---
st.subheader("Detailed Content Breakdown")

st.dataframe(filtered_df[['Date Published', 'Platform', 'Topic', 'Views', 'Likes', 'Shares', 'Total Engagement']], use_container_width=True)
