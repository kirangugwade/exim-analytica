import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import json
import re
import os

# --- Page Config ---
st.set_page_config(
    page_title="India Trade Analytics",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Custom CSS ---
# st.markdown("""
# <style>
#     /* Global Background and Font */
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
#     html, body, [class*="css"]  {
#         font-family: 'Inter', sans-serif;
#     }
    
#     .stApp {
#         background: radial-gradient(circle at 10% 20%, rgb(17, 24, 39) 0%, rgb(0, 0, 0) 90%);
#         color: #e0e0e0;
#     }

#     /* Metric Cards */
#     div[data-testid="metric-container"] {
#         background: rgba(255, 255, 255, 0.05);
#         border: 1px solid rgba(255, 255, 255, 0.1);
#         padding: 20px;
#         border-radius: 15px;
#         backdrop-filter: blur(10px);
#         transition: transform 0.2s ease, box-shadow 0.2s ease;
#     }
#     div[data-testid="metric-container"]:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 10px 20px rgba(0,0,0,0.2);
#         border: 1px solid rgba(255, 255, 255, 0.2);
#     }
    
#     /* Headers */
#     h1, h2, h3 {
#         color: #ffffff;
#         font-weight: 700;
#         letter-spacing: -0.5px;
#     }
    
#     /* Tabs */
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 10px;
#         border-bottom: 1px solid rgba(255,255,255,0.1);
#     }
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         white-space: pre-wrap;
#         background-color: rgba(255,255,255,0.02);
#         border-radius: 5px 5px 0px 0px;
#         color: #a0a0a0;
#         font-weight: 600;
#     }
#     .stTabs [aria-selected="true"] {
#         background-color: rgba(255,255,255,0.1);
#         color: #ffffff;
#         border-bottom: 2px solid #3b82f6;
#     }

#     /* Sidebar */
#     section[data-testid="stSidebar"] {
#         background: rgba(10, 10, 20, 0.95);
#         border-right: 1px solid rgba(255,255,255,0.05);
#     }
    
#     /* Tables */
#     div[data-testid="stDataFrame"] {
#         background: rgba(255, 255, 255, 0.02);
#         border-radius: 10px;
#         padding: 10px;
#         border: 1px solid rgba(255, 255, 255, 0.05);
#     }

#     /* Plotly Charts Background */
#     .js-plotly-plot .plotly .main-svg {
#         background: transparent !important;
#     }
# </style>
# """, unsafe_allow_html=True)

# --- Data Loading Function ---
@st.cache_data(show_spinner=False)
def load_all_data():
    """
    Loads and consolidates Export and Import data.
    """
    data_sources = [
        {"type": "Export", "pattern": "export-data-commodity-wise/data-year-*.json"},
        {"type": "Import", "pattern": "import-data-commodity-wise/data-year-*.json"}
    ]
    
    all_data = []
    year_key_pattern = re.compile(r"^\d{4}\s*-\s*\d{4}$")
    
    files_processed = 0
    
    for source in data_sources:
        files = glob.glob(source["pattern"])
        files.sort()
        
        for fpath in files:
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            except Exception as e:
                continue
                
            rows = content.get('tbody', [])
            for row in rows:
                hscode = row.get('HSCode')
                if not hscode: continue
                
                hscode = hscode.strip()
                commodity = row.get('Commodity', '').strip()
                
                for key, val in row.items():
                    if year_key_pattern.match(key):
                        year_norm = key.replace(" ", "")
                        clean_val = 0.0
                        if isinstance(val, str) and val.strip():
                            try:
                                clean_val = float(val.replace(',', ''))
                            except ValueError:
                                pass
                        elif isinstance(val, (int, float)):
                            clean_val = float(val)

                        all_data.append({
                            'HSCode': hscode,
                            'Commodity': commodity,
                            'Year': year_norm,
                            'Value': clean_val,
                            'Type': source["type"]
                        })
            files_processed += 1

    if not all_data:
        return pd.DataFrame()
        
    df = pd.DataFrame(all_data)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['HSCode', 'Year', 'Type'], keep='last')
    
    # Sort
    df = df.sort_values(['Year', 'Type'])
    
    return df

# --- Main App ---

st.title("🇮🇳 India Trade Analytics")
st.markdown("<p style='font-size: 1.2rem; color: #a0a0a0;'>Comprehensive dashboard for tracking India's Exports and Imports.</p>", unsafe_allow_html=True)

# Load Data
with st.spinner('Loading and consolidating trade data...'):
    df = load_all_data()

if df.empty:
    st.error("No data found. Please check if the data directories exist.")
    st.stop()

# --- Sidebar ---
st.sidebar.title("🔍 Analytics Controls")
st.sidebar.markdown('---')

# Commodity Search
unique_commodities = df[['HSCode', 'Commodity']].drop_duplicates()
unique_commodities['Display'] = unique_commodities['HSCode'] + " - " + unique_commodities['Commodity']
search_options = sorted(unique_commodities['Display'].tolist())

selected_display = st.sidebar.selectbox("Select Commodity (HSCode):", search_options)

# Get selected HSCode
selected_hscode = selected_display.split(" - ")[0]
selected_commodity_name = " - ".join(selected_display.split(" - ")[1:])

# Filter Data
filtered_df = df[df['HSCode'] == selected_hscode].copy()

# Add Net Balance Column for later use (requires pivoting)
pivot_df = filtered_df.pivot(index='Year', columns='Type', values='Value').fillna(0).reset_index()
if 'Export' not in pivot_df.columns: pivot_df['Export'] = 0.0
if 'Import' not in pivot_df.columns: pivot_df['Import'] = 0.0
pivot_df['Trade Balance'] = pivot_df['Export'] - pivot_df['Import']

# --- Main Content Area ---
st.markdown("---")
st.subheader(f"HS Code: {selected_hscode}")
st.markdown(f"<h3 style='color: #4ade80;'>{selected_commodity_name}</h3>", unsafe_allow_html=True)

if pivot_df.empty:
    st.warning("No data available for this selection.")
else:
    # --- Metrics Row ---
    latest_year = pivot_df.iloc[-1]['Year']
    latest_export = pivot_df.iloc[-1]['Export']
    latest_import = pivot_df.iloc[-1]['Import']
    latest_balance = pivot_df.iloc[-1]['Trade Balance']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label=f"Exports ({latest_year})", value=f"₹{latest_export:,.2f} Cr", delta=None)
    with col2:
        st.metric(label=f"Imports ({latest_year})", value=f"₹{latest_import:,.2f} Cr", delta=None)
    with col3:
        st.metric(
            label="Trade Balance", 
            value=f"₹{latest_balance:,.2f} Cr", 
            delta=f"{'Surplus' if latest_balance >= 0 else 'Deficit'}",
            delta_color="normal" if latest_balance >= 0 else "inverse"
        )
    with col4:
         total_volume = latest_export + latest_import
         st.metric(label="Total Trade Volume", value=f"₹{total_volume:,.2f} Cr")

    st.markdown("---")

    # --- Charts & Analysis ---
    
    tab1, tab2, tab3 = st.tabs(["📈 Market Trends", "⚖️ Trade Balance", "📄 Raw Data"])
    
    with tab1:
        st.markdown("### Export vs Import Trends")
        fig_line = px.line(
            filtered_df, 
            x='Year', 
            y='Value', 
            color='Type',
            markers=True,
            title='Annual Trade Performance',
            labels={'Value': 'Value (Crore Rupees)', 'Type': 'Trade Type'},
            color_discrete_map={'Export': '#4ade80', 'Import': '#f87171'} # Green for Export, Red for Import
        )
        fig_line.update_traces(line_width=3, marker_size=8)
        fig_line.update_layout(
            hovermode="x unified", 
            font=dict(family="Inter, sans-serif"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e0e0',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        fig_line.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
        fig_line.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
        
        st.plotly_chart(fig_line, use_container_width=True)

    with tab2:
        st.markdown("### Trade Balance Analysis")
        # Color the bars: Green if > 0 (Surplus), Red if < 0 (Deficit)
        pivot_df['Color'] = pivot_df['Trade Balance'].apply(lambda x: '#4ade80' if x >= 0 else '#f87171')
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=pivot_df['Year'],
            y=pivot_df['Trade Balance'],
            marker_color=pivot_df['Color'],
            name='Trade Balance'
        ))
        
        fig_bar.update_layout(
            title='Net Trade Balance (Exports - Imports)',
            yaxis_title='Value (Crore Rupees)',
            font=dict(family="Inter, sans-serif"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e0e0e0',
        )
        fig_bar.update_xaxes(showgrid=False)
        fig_bar.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with tab3:
        st.markdown("### Detailed Trade Records")
        
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("*Filtered Data for Selected Commodity*")
            display_df = pivot_df.set_index('Year')[['Export', 'Import', 'Trade Balance']]
            st.dataframe(display_df.style.format("₹{:,.2f}"), use_container_width=True)
            
        with col_r:
             st.markdown("#### Download")
             csv = pivot_df.to_csv(index=False).encode('utf-8')
             st.download_button(
                 "📥 Download CSV",
                 csv,
                 f"Trade_Data_{selected_hscode}.csv",
                 "text/csv",
                 key='download-csv',
                 use_container_width=True
             )

# Footer
st.markdown("---")
st.markdown("<center style='color: #666;'>India Trade Analytics Dashboard © 2025</center>", unsafe_allow_html=True)

