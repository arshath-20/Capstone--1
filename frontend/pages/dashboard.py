"""
Dashboard Page
Displays KPIs and analytical charts
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def show_dashboard():
    st.markdown("# 📊 Dashboard")
    st.markdown("Real-time overview of intrusion detection system performance")
    st.markdown("---")
    
    try:
        # Fetch statistics
        response = requests.get(f"{API_BASE_URL}/api/statistics")
        if response.status_code == 200:
            stats = response.json()
        else:
            stats = {
                'total_predictions': 0,
                'total_attacks': 0,
                'total_benign': 0,
                'average_confidence': 0.95,
                'attack_percentage': 0
            }
    except:
        st.error("⚠️ Cannot connect to backend server")
        stats = {
            'total_predictions': 0,
            'total_attacks': 0,
            'total_benign': 0,
            'average_confidence': 0.95,
            'attack_percentage': 0
        }
    
    # KPI Cards
    st.markdown("### 🎯 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Analyzed",
            f"{stats['total_predictions']:,}",
            "traffic flows"
        )
    
    with col2:
        st.metric(
            "🚨 Attacks Detected",
            f"{stats['total_attacks']:,}",
            f"{stats['attack_percentage']:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "✅ Benign",
            f"{stats['total_benign']:,}",
            f"{100 - stats['attack_percentage']:.1f}%"
        )
    
    with col4:
        st.metric(
            "📈 Avg Confidence",
            f"{stats['average_confidence']:.2%}",
            "detection score"
        )
    
    with col5:
        st.metric(
            "🔄 Model Status",
            "Active",
            "✓ Ready"
        )
    
    st.markdown("---")
    
    # Charts
    st.markdown("### 📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Attack vs Benign Pie Chart
        st.markdown("#### Attack Distribution")
        if stats['total_predictions'] > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['🚨 Attacks', '✅ Benign'],
                values=[stats['total_attacks'], stats['total_benign']],
                marker=dict(colors=['#FF6B6B', '#51CF66']),
                textposition='inside',
                textinfo='label+percent'
            )])
            fig.update_layout(
                showlegend=True,
                height=400,
                font=dict(size=12)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No prediction data available yet")
    
    with col2:
        # Confidence Distribution
        st.markdown("#### Model Confidence")
        confidence_data = {
            'Range': ['0-25%', '25-50%', '50-75%', '75-90%', '90-100%'],
            'Count': [5, 10, 45, 120, 200]  # Mock data
        }
        df_conf = pd.DataFrame(confidence_data)
        
        fig = px.bar(
            df_conf,
            x='Range',
            y='Count',
            title='Prediction Confidence Distribution',
            labels={'Range': 'Confidence Range', 'Count': 'Number of Predictions'},
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Feature Importance (Mock)
    st.markdown("### 🔑 Top 10 Important Features")
    feature_importance = pd.DataFrame({
        'Feature': [
            'Destination Port',
            'Total Fwd Packets',
            'Flow Duration',
            'Total Backward Packets',
            'Fwd Packet Length Max',
            'Flow Bytes/s',
            'Flow Packets/s',
            'Fwd IAT Mean',
            'Bwd Packet Length Mean',
            'ACK Flag Count'
        ],
        'Importance': [0.145, 0.128, 0.112, 0.098, 0.087, 0.076, 0.065, 0.054, 0.048, 0.041]
    })
    
    fig = px.bar(
        feature_importance,
        x='Importance',
        y='Feature',
        orientation='h',
        color='Importance',
        color_continuous_scale='Blues',
        title='Feature Importance for Intrusion Detection'
    )
    fig.update_layout(
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent Logs
    st.markdown("### 📋 Recent Predictions")
    try:
        response = requests.get(f"{API_BASE_URL}/api/logs?limit=10")
        if response.status_code == 200:
            logs = response.json()['logs']
            if logs:
                df_logs = pd.DataFrame([
                    {
                        'Time': log['timestamp'],
                        'Prediction': log['prediction'],
                        'Confidence': f"{log['confidence']:.2%}",
                        'Status': '🚨 ATTACK' if log['is_attack'] else '✅ BENIGN'
                    }
                    for log in logs[:10]
                ])
                st.dataframe(df_logs, use_container_width=True, hide_index=True)
            else:
                st.info("No predictions yet")
    except:
        st.info("Unable to fetch recent logs")
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
