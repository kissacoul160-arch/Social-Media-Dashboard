import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Analytics Dashboard 🎀", layout="wide")

# --- 2. THE COQUETTE GLUE (CSS) ---
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&family=Playfair+Display:ital@1&display=swap" rel="stylesheet">
    
    <style>
    .stApp {
        background-color: #FFF5F7 !important;
        background-image: url("https://www.transparenttextures.com/patterns/white-lace.png") !important;
        background-attachment: fixed !important;
    }
    h1 {
        font-family: 'Great Vibes', cursive !important;
        color: #D4778B !important;
        font-size: 5rem !important;
        text-align: center !important;
    }
    h2, h3, .stSubheader {
        font-family: 'Dancing Script', cursive !important;
        color: #D4778B !important;
        font-size: 2.5rem !important;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 2px dashed #FFC1CC !important;
        border-radius: 30px !important;
        padding: 20px !important;
    }
    div[data-testid="stMetricLabel"] > div {
        font-family: 'Dancing Script', cursive !important;
        font-size: 1.8rem !important;
        color: #D4778B !important;
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 228, 232, 1) !important;
        border-right: 5px double #FFC1CC !important;
    }
    .stButton > button {
        background-color: #FFC1CC !important;
        color: white !important;
        border-radius: 50px !important;
        font-family: 'Dancing Script', cursive !important;
        border: 2px solid #FFF !important;
    }
    hr {
        border: 0; height: 3px;
        background-image: linear-gradient(to right, transparent, #FFC1CC, transparent) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. NAVIGATION & FILE ROUTING ---
st.sidebar.markdown("### Navigation")
page = st.sidebar.radio("Select Dashboard:", ["Social Media Dashboard", "Forum Dashboard"])

# Routing files based on your previous requests
if page == "Social Media Dashboard":
    TARGET_FILE = 'dashboard - Company.csv'
else:
    TARGET_FILE = 'dashboard - General.csv'

# --- 4. DATA LOADING & CLEANING ---
def load_data(file_path):
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        # Remove empty Unnamed columns often found in manual CSVs 
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Standardize column headers for logic consistency 
        df = df.rename(columns={'Likes/Votes': 'Likes', 'Comments/Replies': 'Comments'})
        
        # Numeric conversion and cleanup
        for col in ['Views', 'Likes', 'Comments']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0
                
        # 14-Day Pruning for Visualizations 
        if 'Date Published' in df.columns:
            df['Date Published'] = pd.to_datetime(df['Date Published'], errors='coerce')
            cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=14)
            df_display = df[df['Date Published'] >= cutoff].copy()
            df_display['Total Engagement'] = df_display['Likes'] + df_display['Comments']
            return df_display
        return df
    except:
        return pd.DataFrame()

# --- 5. SIDEBAR UPLOAD (Updates the specific CSV file) ---
st.sidebar.markdown("---")
st.sidebar.markdown(f"### Update {page} Data")
uploaded_file = st.sidebar.file_uploader(f"Upload new {TARGET_FILE}", type="csv", key=f"uploader_{page}")

if uploaded_file is not None:
    # Save the file to the current computer's local directory
    new_data = pd.read_csv(uploaded_file)
    new_data.to_csv(TARGET_FILE, index=False)
    st.sidebar.success(f"Successfully updated {TARGET_FILE}! ✨")
    st.rerun()

# Load filtered data for charts
display_df = load_data(TARGET_FILE)

# --- 6. MAIN DASHBOARD UI ---
st.title(page)
st.markdown(f"<p style='text-align: center; color: #D4778B;'>Reading from: <b>{TARGET_FILE}</b></p>", unsafe_allow_html=True)

# Metrics Summary Row
c1, c2, c3 = st.columns(3)
if not display_df.empty:
    c1.metric("Total Views", f"{int(display_df['Views'].sum()):,}")
    c2.metric("Total Likes", f"{int(display_df['Likes'].sum()):,}")
    c3.metric("Comments", f"{int(display_df['Comments'].sum()):,}")
else:
    c1.metric("Total Views", "0")
    c2.metric("Total Likes", "0")
    c3.metric("Comments", "0")

st.markdown("<hr>", unsafe_allow_html=True)

# Charts Section
if not display_df.empty:
    col_left, col_right = st.columns(2)
    palette = ["#FFC1CC", "#FFD1DC", "#FFB7C5", "#E0B0FF", "#FADADD"]
    
    with col_left:
        st.subheader("Metrics Distribution")
        m_data = display_df[['Views', 'Likes', 'Comments']].sum().reset_index()
        m_data.columns = ['Metric', 'Total']
        fig1 = px.bar(m_data, x="Metric", y="Total", color="Metric", color_discrete_sequence=palette)
        fig1.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        # Unique keys prevent the DuplicateElementId error 
        st.plotly_chart(fig1, use_container_width=True, key=f"bar_chart_{page}")

    with col_right:
        st.subheader("Engagement by Topic")
        # Handles column naming variation between files 
        cat_col = 'Topic Category' if 'Topic Category' in display_df.columns else 'Platform'
        topic_data = display_df.groupby(cat_col)['Total Engagement'].sum().reset_index()
        fig2 = px.bar(topic_data, x="Total Engagement", y=cat_col, orientation='h', color_discrete_sequence=[palette[2]])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True, key=f"topic_chart_{page}")
else:
    st.warning("No data found for the last 14 days. Please upload a file or add rows below! ✨")

st.markdown("<hr>", unsafe_allow_html=True)

# --- 7. RAW DATA EDITOR ---
st.subheader(f"Raw Data Editor: {TARGET_FILE}")
st.write("Edits made here update the file on this machine.")

if os.path.exists(TARGET_FILE):
    # Load the full raw file for editing (ignores the 14-day filter)
    raw_edit_df = pd.read_csv(TARGET_FILE)
    raw_edit_df = raw_edit_df.loc[:, ~raw_edit_df.columns.str.contains('^Unnamed')]
    
    # data_editor allows manual entry and row deletion
    edited_df = st.data_editor(raw_edit_df, num_rows="dynamic", use_container_width=True, key=f"editor_{page}")
    
    if st.button("Save Permanent Changes", key=f"save_btn_{page}"):
        edited_df.to_csv(TARGET_FILE, index=False)
        st.success(f"Changes saved to {TARGET_FILE}! 🪄")
        st.rerun()
else:
    st.info(f"The file {TARGET_FILE} does not exist yet. Upload it in the sidebar to begin.")