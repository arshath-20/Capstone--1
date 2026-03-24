"""
Main Streamlit Application
Entry point for the web UI
"""

import streamlit as st
import requests
import json
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Cyber Intrusion Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        /* Main color scheme */
        :root {
            --primary-color: #FF6B6B;
            --secondary-color: #4ECDC4;
            --accent-color: #45B7D1;
        }
        
        /* Custom card styling */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Header styling */
        .header-title {
            font-size: 3em;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        /* Danger alert */
        .danger-box {
            background-color: #ffe6e6;
            border-left: 4px solid #ff6b6b;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        /* Success alert */
        .success-box {
            background-color: #e6ffe6;
            border-left: 4px solid #51cf66;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# 🛡️ CYBER INTRUSION DETECTION")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🔍 Live Prediction", "📤 Batch Analysis", "📊 Reports", "ℹ️ About"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **About This System**\n\n"
    "Advanced machine learning-based network intrusion detection system. "
    "Analyzes network traffic patterns to identify potential cyber attacks in real-time."
)

# API configuration
API_BASE_URL = "http://localhost:8000"

@st.cache_resource
def get_predictor():
    """Get predictor (cached)"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/metrics")
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# Route to correct page
if page == "🏠 Dashboard":
    from pages.dashboard import show_dashboard
    show_dashboard()

elif page == "🔍 Live Prediction":
    from pages.live_prediction import show_live_prediction
    show_live_prediction()

elif page == "📤 Batch Analysis":
    from pages.batch_analysis import show_batch_analysis
    show_batch_analysis()

elif page == "📊 Reports":
    from pages.reports import show_reports
    show_reports()

elif page == "ℹ️ About":
    from pages.about import show_about
    show_about()
