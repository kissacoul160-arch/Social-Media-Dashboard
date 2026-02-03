import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Analytics Dashboard 🎀", layout="wide")

# --- 2. COQUETTE STYLING (CSS) ---
st.markdown(
    """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600&family=Great+Vibes&display=swap" rel="stylesheet">
    <style>
    .stApp { background-color: #FFF5F7 !important; background-image: url("https://www.transparenttextures.com/patterns/white-lace.png") !important; }
    h1 { font-family: 'Great Vibes', cursive !important; color: #D4778B !important; font-size: 4.5rem !important; text-align: center !important; }
    h2, h3, .stSubheader { font-family: 'Dancing Script', cursive !important; color: #D4778B !important; }
    div[data-testid="stMetric"] { background-color: rgba(255, 255, 255, 0.8) !important; border: 2px dashed #FFC1CC !important; border-radius: 20px !important; }
    section[data-testid="stSidebar"] { background-color: #FFE4E8 !important; border-right: 3px double #FFC1CC !important; }
    .stButton > button { background-color: #FFC1CC !important; color: white !important; border-radius: 20px !important; width: 100%; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. NAVIGATION & FILE ROUTING ---
st.sidebar.markdown("### 🎀 Navigation")
page = st.sidebar.radio("Go to:", ["Social Media Dashboard", "Forum Dashboard"])

# Set correct file based on choice
if page == "Social Media Dashboard":
    TARGET_FILE = 'dashboard - Company.csv'
else:
    TARGET_FILE = 'dashboard - General.csv'

# --- 4. DATA PROCESSING FUNCTIONS ---

def clean_dataframe_for_editor(df):
    """Makes the dataframe 'typable' by fixing types and removing N/A strings."""
    # 1. Remove unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # 2. Replace the literal string "N/A" with actual empty values (NaN)
    # This allows you to type numbers into these cells
    df = df.replace(['N/A', 'n/a', 'nan', 'NaN'], None)
    
    # 3. Force numeric columns so the editor gives you a number-pad/typing ability
    num_cols = ['Views', 'Likes/Votes', 'Comments/Replies', 'Shares', 'New Follow Count', 'Likes', 'Comments']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # 4. Self-Healing: Fix 2026 dates to 2025
    if 'Date Published' in df.columns:
        df['Date Published'] = df['Date Published'].astype(str).str.replace('2026', '2025')
        
    return df

def get_filtered_data(df):
    """Applies the 14-day rule for charts."""
    if df.empty: return df
    
    temp_df = df.copy()
    # Standardize column names for chart logic
    temp_df = temp_df.rename(columns={'Likes/Votes': 'Likes', 'Comments/Replies': 'Comments'})
    
    if 'Date Published' in temp_df.columns:
        temp_df['Date Published'] = pd.to_datetime(temp_df['Date Published'], errors='coerce')
        cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=14)
        temp_df = temp_df[temp_df['Date Published'] >= cutoff]
        
    # Final numeric cleanup for totals
    for c in ['Views', 'Likes', 'Comments']:
        if c in temp_df.columns:
            temp_df[c] = pd.to_numeric(temp_df[c], errors='coerce').fillna(0)
            
    if not temp_df.empty:
        temp_df['Total Engagement'] = temp_df.get('Likes', 0) + temp_df.get('Comments', 0)
        
    return temp_df

# --- 5. APP LOGIC ---

st.title(page)

# Check if file exists, if not create a template
if not os.path.exists(TARGET_FILE):
    st.info(f"✨ Creating a new template for {TARGET_FILE}. Please upload your data in the sidebar!")
    pd.DataFrame(columns=['Post Title/URL', 'Platform', 'Topic Category', 'Views', 'Likes/Votes', 'Comments/Replies', 'Date Published']).to_csv(TARGET_FILE, index=False)

# Load and Clean
raw_df = pd.read_csv(TARGET_FILE)
raw_df = clean_dataframe_for_editor(raw_df)
display_df = get_filtered_data(raw_df)

# --- 6. METRICS & CHARTS (14-Day Rule) ---
c1, c2, c3 = st.columns(3)
if not display_df.empty:
    c1.metric("Total Views", f"{int(display_df['Views'].sum()):,}")
    c2.metric("Total Likes", f"{int(display_df['Likes'].sum()):,}")
    c3.metric("Comments", f"{int(display_df['Comments'].sum()):,}")
else:
    st.warning("No data found for the last 14 days in this file.")

st.markdown("---")

if not display_df.empty:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Performance Overview")
        m_plot = display_df[['Views', 'Likes', 'Comments']].sum().reset_index()
        m_plot.columns = ['Metric', 'Total']
        fig1 = px.bar(m_plot, x='Metric', y='Total', color='Metric', color_discrete_sequence=["#FFC1CC", "#FFB7C5", "#E0B0FF"])
        st.plotly_chart(fig1, use_container_width=True, key=f"bar_{page}")
        
    with col_b:
        st.subheader("Engagement by Topic")
        cat_col = 'Topic Category' if 'Topic Category' in display_df.columns else 'Platform'
        topic_data = display_df.groupby(cat_col)['Total Engagement'].sum().sort_values().reset_index()
        fig2 = px.bar(topic_data, x='Total Engagement', y=cat_col, orientation='h', color_discrete_sequence=["#D4778B"])
        st.plotly_chart(fig2, use_container_width=True, key=f"topic_{page}")

# --- 7. THE RAW DATA EDITOR (Fixed for Typing) ---
st.markdown("---")
st.subheader(f"📝 Edit {TARGET_FILE} Rows")
st.write("✨ **Tip:** Double-click a cell to type. Use the empty bottom row to add new data.")

# data_editor handles the manual typing
edited_df = st.data_editor(
    raw_df, 
    num_rows="dynamic", 
    use_container_width=True, 
    key=f"editor_widget_{page}",
    # This ensures the columns are treated as the right types
    column_config={
        "Date Published": st.column_config.TextColumn("Date Published (M/D/YY)"),
        "Views": st.column_config.NumberColumn("Views", format="%d"),
        "Likes/Votes": st.column_config.NumberColumn("Likes", format="%d"),
        "Comments/Replies": st.column_config.NumberColumn("Comments", format="%d")
    }
)

if st.button("💖 Save All Changes Permanently", key=f"save_btn_{page}"):
    # Final date fix before saving
    if 'Date Published' in edited_df.columns:
        edited_df['Date Published'] = edited_df['Date Published'].astype(str).str.replace('2026', '2025')
    
    edited_df.to_csv(TARGET_FILE, index=False)
    st.success("Changes Saved Successfully! 🪄")
    st.rerun()

# --- 8. SIDEBAR UPLOADER ---
st.sidebar.markdown("---")
st.sidebar.subheader(f"Upload New {page} CSV")
up_file = st.sidebar.file_uploader("Choose File", type="csv", key=f"up_{page}")
if up_file:
    new_up = pd.read_csv(up_file)
    new_up.to_csv(TARGET_FILE, index=False)
    st.sidebar.success("File Overwritten! ✨")
    st.rerun()