"""
Batch Analysis Page
CSV file upload and batch prediction
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
import csv

API_BASE_URL = "http://localhost:8000"

def show_batch_analysis():
    st.markdown("# 📤 Batch Analysis")
    st.markdown("Upload CSV file for batch intrusion detection")
    st.markdown("---")
    
    # File uploader
    st.markdown("### 📁 Upload CSV File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="CSV should contain network features without Label column (or with Label column)"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        with col3:
            st.metric("Type", "CSV")
        
        # Preview data
        st.markdown("### 👁️ Data Preview")
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head(10), use_container_width=True)
            
            st.info(f"📊 Total rows: {len(df)} | Columns: {len(df.columns)}")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()
        
        st.markdown("---")
        
        # Process button
        if st.button("🚀 Start Batch Analysis", use_container_width=True, type="primary"):
            with st.spinner("⏳ Processing batch predictions... This may take a moment"):
                try:
                    # Prepare file for upload
                    csv_buffer = io.BytesIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    
                    # Send to backend
                    files = {'file': ('batch_analysis.csv', csv_buffer, 'text/csv')}
                    response = requests.post(
                        f"{API_BASE_URL}/api/batch_predict",
                        files=files,
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("---")
                        st.markdown("### ✅ Analysis Complete!")
                        
                        # Summary statistics
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                "Total Samples",
                                f"{result['total_samples']:,}",
                                "analyzed"
                            )
                        
                        with col2:
                            st.metric(
                                "🚨 Attacks",
                                f"{result['total_attacks']:,}",
                                f"{result['attack_percentage']:.1f}%",
                                delta_color="inverse"
                            )
                        
                        with col3:
                            st.metric(
                                "✅ Benign",
                                f"{result['total_samples'] - result['total_attacks']:,}",
                                f"{100 - result['attack_percentage']:.1f}%"
                            )
                        
                        with col4:
                            st.metric(
                                "⏱️ Processing Time",
                                "< 5s",
                                "completed"
                            )
                        
                        st.markdown("---")
                        
                        # Attack Type Breakdown
                        st.markdown("### 🎯 Attack Type Breakdown")
                        
                        # Count attack types from predictions
                        attack_type_counts = {}
                        for pred in result['predictions']:
                            attack_type = pred['prediction']
                            if attack_type != 'BENIGN':
                                attack_type_counts[attack_type] = attack_type_counts.get(attack_type, 0) + 1
                        
                        if attack_type_counts:
                            # Create columns for attack type metrics
                            attack_types_cols = st.columns(len(attack_type_counts))
                            
                            attack_type_colors = {
                                'DDoS': '#FF4444',
                                'PortScan': '#FF8844',
                                'BruteForce': '#FFBB44',
                                'Botnet': '#FF6B6B',
                                'Infiltration': '#FF3333',
                                'SQLInjection': '#DD3333'
                            }
                            
                            for idx, (attack_type, count) in enumerate(sorted(attack_type_counts.items())):
                                with attack_types_cols[idx]:
                                    percentage = (count / result['total_attacks'] * 100) if result['total_attacks'] > 0 else 0
                                    st.metric(
                                        f"🚨 {attack_type}",
                                        f"{count}",
                                        f"{percentage:.1f}% of attacks"
                                    )
                        
                        st.markdown("---")
                        
                        # Visualization
                        st.markdown("### 📊 Results Visualization")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pie chart
                            fig = go.Figure(data=[go.Pie(
                                labels=['🚨 Attacks', '✅ Benign'],
                                values=[result['total_attacks'], result['total_samples'] - result['total_attacks']],
                                marker=dict(colors=['#FF6B6B', '#51CF66']),
                                textposition='inside',
                                textinfo='label+percent'
                            )])
                            fig.update_layout(height=400, showlegend=True)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Bar chart
                            fig = go.Figure(data=[
                                go.Bar(
                                    name='Attacks',
                                    x=['Classification'],
                                    y=[result['total_attacks']],
                                    marker_color='#FF6B6B'
                                ),
                                go.Bar(
                                    name='Benign',
                                    x=['Classification'],
                                    y=[result['total_samples'] - result['total_attacks']],
                                    marker_color='#51CF66'
                                )
                            ])
                            fig.update_layout(
                                barmode='stack',
                                height=400,
                                xaxis_title='Classification Result',
                                yaxis_title='Count'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Attack Type Distribution
                        if attack_type_counts:
                            st.markdown("#### Attack Type Distribution")
                            
                            # Bar chart for attack types
                            attack_types_list = list(attack_type_counts.keys())
                            attack_counts_list = list(attack_type_counts.values())
                            
                            fig_attacks = go.Figure(data=[
                                go.Bar(
                                    x=attack_types_list,
                                    y=attack_counts_list,
                                    marker_color=['#FF4444', '#FF8844', '#FFBB44', '#FF6B6B', '#FF3333', '#DD3333'][:len(attack_types_list)],
                                    text=attack_counts_list,
                                    textposition='auto'
                                )
                            ])
                            fig_attacks.update_layout(
                                height=350,
                                xaxis_title='Attack Type',
                                yaxis_title='Count',
                                showlegend=False
                            )
                            st.plotly_chart(fig_attacks, use_container_width=True)
                        
                        st.markdown("---")
                        
                        # Results table
                        st.markdown("### 📋 Detailed Results (First 50)")
                        
                        results_records = []
                        for i, pred in enumerate(result['predictions'][:50]):
                            results_records.append({
                                'Index': i + 1,
                                'Attack Type': pred['prediction'],
                                'Confidence': f"{pred['confidence']:.2%}",
                                'Status': '🚨 ATTACK' if pred['is_attack'] else '✅ BENIGN'
                            })
                        
                        df_results = pd.DataFrame(results_records)
                        st.dataframe(df_results, use_container_width=True, hide_index=True)
                        
                        # Download results
                        st.markdown("---")
                        st.markdown("### 💾 Export Results")
                        
                        # Create download dataframe
                        export_data = []
                        for i, pred in enumerate(result['predictions']):
                            export_data.append({
                                'Sample_Index': i + 1,
                                'Attack_Type': pred['prediction'],
                                'Confidence': pred['confidence'],
                                'Is_Attack': pred['is_attack']
                            })
                        
                        df_export = pd.DataFrame(export_data)
                        csv_export = df_export.to_csv(index=False)
                        
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv_export,
                            file_name="batch_predictions.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        # Timestamp
                        st.caption(f"Analysis completed at: {result['timestamp']}")
                    
                    else:
                        st.error(f"Error: {response.json()}")
                
                except Exception as e:
                    st.error(f"Processing error: {str(e)}")
    
    st.markdown("---")
    
    # Guidelines
    st.markdown("### 📋 Guidelines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "**CSV Format Requirements:**\n\n"
            "✓ All 82 network features\n"
            "✓ Numeric values only\n"
            "✓ Comma-separated values\n"
            "✓ No missing values\n"
            "✓ Can include 'Label' column"
        )
    
    with col2:
        st.warning(
            "**Performance Tips:**\n\n"
            "• Recommended: < 10,000 rows\n"
            "• Processing time: ~5 seconds\n"
            "• For larger files: split into batches\n"
            "• Check file encoding (UTF-8)\n"
            "• Remove duplicate rows"
        )
