"""
Live Prediction Page
Single sample prediction interface
"""

import streamlit as st
import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def generate_derived_features(user_inputs):
    """Generate derived features with intelligent patterns based on port and traffic characteristics"""
    features = [0.0] * 78
    
    # All 78 features in order
    all_features = [
        'Destination Port', 'Flow Duration', 'Total Fwd Packets',
        'Total Backward Packets', 'Total Length of Fwd Packets',
        'Total Length of Bwd Packets', 'Fwd Packet Length Max',
        'Fwd Packet Length Min', 'Fwd Packet Length Mean',
        'Fwd Packet Length Std', 'Bwd Packet Length Max',
        'Bwd Packet Length Min', 'Bwd Packet Length Mean',
        'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s',
        'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
        'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max',
        'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
        'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags', 'Bwd PSH Flags',
        'Fwd URG Flags', 'Bwd URG Flags', 'Fwd Header Length',
        'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s',
        'Min Packet Length', 'Max Packet Length', 'Packet Length Mean',
        'Packet Length Std', 'Packet Length Variance', 'FIN Flag Count',
        'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
        'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count',
        'ECE Flag Count', 'Down/Up Ratio', 'Average Packet Size',
        'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
        'Fwd Header Length.1', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk',
        'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk',
        'Bwd Avg Bulk Rate', 'Subflow Fwd Packets', 'Subflow Fwd Bytes',
        'Subflow Bwd Packets', 'Subflow Bwd Bytes', 'Init_Win_bytes_forward',
        'Init_Win_bytes_backward', 'act_data_pkt_fwd', 'min_seg_size_forward',
        'Active Mean', 'Active Std', 'Active Max', 'Active Min',
        'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min'
    ]
    
    # Get user inputs
    dst_port = user_inputs.get('Destination Port', 80)
    flow_duration = user_inputs.get('Flow Duration', 5000)
    total_fwd_packets = user_inputs.get('Total Fwd Packets', 25)
    total_bwd_packets = user_inputs.get('Total Backward Packets', 20)
    fwd_bytes = user_inputs.get('Total Length of Fwd Packets', 2000)
    bwd_bytes = user_inputs.get('Total Length of Bwd Packets', 1500)
    fwd_mean = user_inputs.get('Fwd Packet Length Mean', 100)
    bwd_mean = user_inputs.get('Bwd Packet Length Mean', 100)
    syn_count = user_inputs.get('SYN Flag Count', 0)
    ack_count = user_inputs.get('ACK Flag Count', 5)
    
    # Fill in direct user inputs
    features[all_features.index('Destination Port')] = dst_port
    features[all_features.index('Flow Duration')] = flow_duration
    features[all_features.index('Total Fwd Packets')] = total_fwd_packets
    features[all_features.index('Total Backward Packets')] = total_bwd_packets
    features[all_features.index('Total Length of Fwd Packets')] = fwd_bytes
    features[all_features.index('Total Length of Bwd Packets')] = bwd_bytes
    features[all_features.index('Fwd Packet Length Mean')] = fwd_mean
    features[all_features.index('Bwd Packet Length Mean')] = bwd_mean
    
    # >>> INTELLIGENT PATTERN DETECTION <<<
    # Determine traffic characteristics based on user input
    packet_ratio = total_bwd_packets / max(total_fwd_packets, 1)
    
    # Pattern detection logic
    is_port_scan_pattern = (packet_ratio < 0.3 and syn_count >= 5) or (packet_ratio < 0.2)
    is_ddos_pattern = (total_fwd_packets > 200 and packet_ratio < 0.15) or (total_fwd_packets > 300)
    is_bruteforce_pattern = (syn_count > 8 and ack_count > 8 and (dst_port == 22 or dst_port == 23))
    is_normal_pattern = (packet_ratio > 0.6 and flow_duration > 2000 and syn_count <= 2)
    
    # If user provided explicit SYN/ACK values, use them as-is (respect user input)
    # Otherwise, intelligently infer based on patterns
    if syn_count == 0 and ack_count == 0:  # User didn't specify
        if is_port_scan_pattern:
            syn_count = 8
            ack_count = 0
        elif is_ddos_pattern:
            syn_count = 0
            ack_count = 0
        elif is_bruteforce_pattern:
            syn_count = 12
            ack_count = 10
        else:  # Normal/benign by default
            syn_count = 0
            ack_count = 6
    
    # Set the flag values
    # Set the flag values
    features[all_features.index('SYN Flag Count')] = syn_count
    features[all_features.index('ACK Flag Count')] = ack_count
    
    # Calculate flow rates
    total_packets = total_fwd_packets + total_bwd_packets
    total_bytes = fwd_bytes + bwd_bytes
    time_sec = max(flow_duration / 1000.0, 0.001)
    
    # === ENHANCED FEATURE GENERATION FOR DISTINCTIVE PATTERNS ===
    
    # 1. Header lengths - varies by traffic type
    if is_port_scan_pattern:
        # Port scans typically have minimal headers
        fwd_header = 20  # Minimal TCP header
        bwd_header = 20
    elif is_bruteforce_pattern:
        # Brute force has normal headers
        fwd_header = 32
        bwd_header = 32
    elif is_ddos_pattern:
        # DDoS may have fragmented packets
        fwd_header = 20
        bwd_header = 20
    else:
        # Normal traffic
        fwd_header = 40
        bwd_header = 40
    
    features[all_features.index('Fwd Header Length')] = fwd_header
    features[all_features.index('Bwd Header Length')] = bwd_header
    
    # 2. Down/Up ratio (backward/forward) - distinctive by attack type
    down_up_ratio = packet_ratio  # Already calculated
    features[all_features.index('Down/Up Ratio')] = down_up_ratio
    
    # 3. Window bytes - OpenFlow signature features
    if is_port_scan_pattern:
        init_win_fwd = 4096
        init_win_bwd = 0  # Many port scans don't establish full connections
    elif is_bruteforce_pattern:
        init_win_fwd = 65535
        init_win_bwd = 65535  # Full TCP handshake
    elif is_ddos_pattern:
        init_win_fwd = 1024  # Often fragmented
        init_win_bwd = 0
    else:
        # Normal
        init_win_fwd = 65535
        init_win_bwd = 65535
    
    features[all_features.index('Init_Win_bytes_forward')] = init_win_fwd
    features[all_features.index('Init_Win_bytes_backward')] = init_win_bwd
    
    # 4. PSH flag patterns
    features[all_features.index('Fwd PSH Flags')] = 1 if (is_bruteforce_pattern or is_normal_pattern) else 0
    features[all_features.index('Bwd PSH Flags')] = 1 if (is_bruteforce_pattern or is_normal_pattern) else 0
    
    # 5. FIN flag - indicates graceful close (normal traffic, brute force)
    features[all_features.index('FIN Flag Count')] = 1 if (is_normal_pattern or is_bruteforce_pattern) else 0
    
    # 6. RST flag - resets common in port scans and attacks
    features[all_features.index('RST Flag Count')] = 1 if is_port_scan_pattern else 0
    
    # Packet length variations - reduce random noise
    if fwd_mean > 0:
        fwd_max = fwd_mean * 1.5  # More predictable
        fwd_min = max(20, fwd_mean * 0.5)
        fwd_std = fwd_mean * 0.2  # Lower variance
    else:
        fwd_max = fwd_min = fwd_std = 0
    
    if bwd_mean > 0:
        bwd_max = bwd_mean * 1.5
        bwd_min = max(20, bwd_mean * 0.5)
        bwd_std = bwd_mean * 0.2
    else:
        bwd_max = bwd_min = bwd_std = 0
    
    features[all_features.index('Fwd Packet Length Max')] = fwd_max
    features[all_features.index('Fwd Packet Length Min')] = fwd_min
    features[all_features.index('Fwd Packet Length Std')] = fwd_std
    features[all_features.index('Bwd Packet Length Max')] = bwd_max
    features[all_features.index('Bwd Packet Length Min')] = bwd_min
    features[all_features.index('Bwd Packet Length Std')] = bwd_std
    
    # Flow rates
    flow_bytes_s = total_bytes / time_sec if time_sec > 0 else 0
    flow_packets_s = total_packets / time_sec if time_sec > 0 else 0
    features[all_features.index('Flow Bytes/s')] = flow_bytes_s
    features[all_features.index('Flow Packets/s')] = flow_packets_s
    
    # IAT (Inter-Arrival Time) stats - use deterministic values
    iat_mean = (flow_duration / max(total_packets - 1, 1)) if total_packets > 1 else flow_duration
    iat_std = iat_mean * 0.4  # Reduce randomness
    iat_max = iat_mean * 2.0
    iat_min = iat_mean * 0.2
    
    features[all_features.index('Flow IAT Mean')] = iat_mean
    features[all_features.index('Flow IAT Std')] = iat_std
    features[all_features.index('Flow IAT Max')] = iat_max
    features[all_features.index('Flow IAT Min')] = iat_min
    
    # Forward IAT
    fwd_iat_total = flow_duration * (total_fwd_packets / max(total_packets, 1)) if total_packets > 0 else flow_duration
    features[all_features.index('Fwd IAT Total')] = fwd_iat_total
    features[all_features.index('Fwd IAT Mean')] = fwd_iat_total / max(total_fwd_packets - 1, 1)
    features[all_features.index('Fwd IAT Std')] = features[all_features.index('Fwd IAT Mean')] * 0.4
    
    # Backward IAT
    bwd_iat_total = flow_duration * (total_bwd_packets / max(total_packets, 1)) if total_packets > 0 else 0
    features[all_features.index('Bwd IAT Total')] = bwd_iat_total
    features[all_features.index('Bwd IAT Mean')] = bwd_iat_total / max(total_bwd_packets - 1, 1) if total_bwd_packets > 1 else 0
    features[all_features.index('Bwd IAT Std')] = max(0, features[all_features.index('Bwd IAT Mean')] * 0.4)
    
    # Packet rate derivatives
    features[all_features.index('Fwd Packets/s')] = total_fwd_packets / time_sec
    features[all_features.index('Bwd Packets/s')] = total_bwd_packets / time_sec
    
    # Packet lengths
    features[all_features.index('Min Packet Length')] = min(fwd_min, bwd_min)
    features[all_features.index('Max Packet Length')] = max(fwd_max, bwd_max)
    features[all_features.index('Packet Length Mean')] = (fwd_mean + bwd_mean) / 2
    packet_len_std = ((fwd_std + bwd_std) / 2) if (fwd_std + bwd_std) > 0 else 0
    features[all_features.index('Packet Length Std')] = packet_len_std
    features[all_features.index('Packet Length Variance')] = packet_len_std ** 2
    
    # Flag counts - set intelligently
    features[all_features.index('Fwd PSH Flags')] = 1 if (total_fwd_packets > 20 and not is_port_scan_pattern) else 0
    features[all_features.index('Bwd PSH Flags')] = 1 if (total_bwd_packets > 20 and not is_port_scan_pattern) else 0
    features[all_features.index('FIN Flag Count')] = max(0, min(1, total_fwd_packets // 50)) if not is_port_scan_pattern else 0
    features[all_features.index('RST Flag Count')] = 0
    features[all_features.index('PSH Flag Count')] = max(1, (total_fwd_packets + total_bwd_packets) // 50) if not is_ddos_pattern else 0
    
    # Average sizes
    avg_pkt_size = total_bytes / max(total_packets, 1)
    features[all_features.index('Average Packet Size')] = avg_pkt_size
    features[all_features.index('Avg Fwd Segment Size')] = fwd_mean
    features[all_features.index('Avg Bwd Segment Size')] = bwd_mean
    
    # Ratio
    features[all_features.index('Down/Up Ratio')] = bwd_bytes / max(fwd_bytes, 1)
    
    # Header lengths (TCP/IP standard)
    features[all_features.index('Fwd Header Length')] = 20 + 20  # IP + TCP
    features[all_features.index('Bwd Header Length')] = 20 + 20
    features[all_features.index('Fwd Header Length.1')] = 20 + 20
    
    # Subflow stats
    features[all_features.index('Subflow Fwd Packets')] = max(1, total_fwd_packets // 2)
    features[all_features.index('Subflow Fwd Bytes')] = max(1, fwd_bytes // 2)
    features[all_features.index('Subflow Bwd Packets')] = max(1, total_bwd_packets // 2)
    features[all_features.index('Subflow Bwd Bytes')] = max(1, bwd_bytes // 2)
    
    # Note: Init_Win_bytes already set above based on pattern detection
    
    # Active/Idle times
    features[all_features.index('Active Mean')] = flow_duration * 0.3
    features[all_features.index('Active Std')] = flow_duration * 0.1
    features[all_features.index('Active Max')] = flow_duration * 0.8
    features[all_features.index('Active Min')] = 1.0
    features[all_features.index('Idle Mean')] = flow_duration * 0.2
    features[all_features.index('Idle Std')] = flow_duration * 0.05
    features[all_features.index('Idle Max')] = flow_duration * 0.5
    features[all_features.index('Idle Min')] = 0.0
    
    # Fill remaining features with sensible defaults
    features[all_features.index('Fwd IAT Max')] = iat_max
    features[all_features.index('Fwd IAT Min')] = iat_min
    features[all_features.index('Bwd IAT Max')] = iat_max
    features[all_features.index('Bwd IAT Min')] = iat_min
    features[all_features.index('Fwd URG Flags')] = 0
    features[all_features.index('Bwd URG Flags')] = 0
    features[all_features.index('URG Flag Count')] = 0
    features[all_features.index('CWE Flag Count')] = 0
    features[all_features.index('ECE Flag Count')] = 0
    features[all_features.index('act_data_pkt_fwd')] = total_fwd_packets
    features[all_features.index('min_seg_size_forward')] = 20
    features[all_features.index('Fwd Avg Bytes/Bulk')] = fwd_bytes / max(total_fwd_packets // 10, 1)
    features[all_features.index('Fwd Avg Packets/Bulk')] = max(1, total_fwd_packets // 5)
    features[all_features.index('Fwd Avg Bulk Rate')] = fwd_bytes / max(total_fwd_packets // 10, 1)
    features[all_features.index('Bwd Avg Bytes/Bulk')] = bwd_bytes / max(total_bwd_packets // 10, 1) if total_bwd_packets > 0 else 0
    features[all_features.index('Bwd Avg Packets/Bulk')] = max(1, total_bwd_packets // 5) if total_bwd_packets > 0 else 1
    features[all_features.index('Bwd Avg Bulk Rate')] = bwd_bytes / max(total_bwd_packets // 10, 1) if total_bwd_packets > 0 else 0
    
    # Convert numpy types to native Python floats to avoid JSON serialization issues
    return [float(max(0, f)) for f in features]


def show_live_prediction():
    st.markdown("# 🔍 Live Intrusion Detection")
    st.markdown("Enter essential network flow information for real-time threat detection")
    st.markdown("---")
    
    # Create input form with ONLY essential features
    st.markdown("### 📝 Network Flow Information (Essential Fields Only)")
    st.info("💡 Tip: Provide the key network metrics. Derived metrics are calculated automatically.")
    
    with st.form("prediction_form"):
        # Row 1: Port and Duration
        col1, col2 = st.columns(2)
        with col1:
            dst_port = st.number_input(
                "Destination Port",
                value=80,
                min_value=0,
                max_value=65535,
                step=1,
                help="Target port number (0-65535)"
            )
        with col2:
            flow_duration = st.number_input(
                "Flow Duration (ms)",
                value=1000.0,
                min_value=0.0,
                step=100.0,
                help="Total flow duration in milliseconds"
            )
        
        # Row 2: Packet counts
        col3, col4 = st.columns(2)
        with col3:
            total_fwd_packets = st.number_input(
                "Total Forward Packets",
                value=10,
                min_value=0,
                step=1,
                help="Number of packets sent forward"
            )
        with col4:
            total_bwd_packets = st.number_input(
                "Total Backward Packets",
                value=10,
                min_value=0,
                step=1,
                help="Number of packets sent backward"
            )
        
        # Row 3: Packet sizes
        col5, col6 = st.columns(2)
        with col5:
            fwd_bytes = st.number_input(
                "Total Fwd Packet Bytes",
                value=1000.0,
                min_value=0.0,
                step=100.0,
                help="Total bytes in forward packets"
            )
        with col6:
            bwd_bytes = st.number_input(
                "Total Bwd Packet Bytes",
                value=1000.0,
                min_value=0.0,
                step=100.0,
                help="Total bytes in backward packets"
            )
        
        # Row 4: Mean packet sizes
        col7, col8 = st.columns(2)
        with col7:
            fwd_mean = st.number_input(
                "Avg Fwd Packet Length",
                value=100.0,
                min_value=0.0,
                step=10.0,
                help="Average size of forward packets"
            )
        with col8:
            bwd_mean = st.number_input(
                "Avg Bwd Packet Length",
                value=100.0,
                min_value=0.0,
                step=10.0,
                help="Average size of backward packets"
            )
        
        # Row 5: Flow rates
        col9, col10 = st.columns(2)
        with col9:
            syn_count = st.number_input(
                "SYN Flag Count",
                value=1,
                min_value=0,
                step=1,
                help="Number of SYN flags (TCP connection)"
            )
        with col10:
            ack_count = st.number_input(
                "ACK Flag Count",
                value=5,
                min_value=0,
                step=1,
                help="Number of ACK flags"
            )
        
        st.markdown("---")
        
        # Submit button
        submitted = st.form_submit_button(
            "🔮 Predict Threat Level",
            use_container_width=True,
            type="primary"
        )
    
    if submitted:
        with st.spinner("🔄 Analyzing network flow..."):
            try:
                # Collect user inputs
                user_inputs = {
                    'Destination Port': dst_port,
                    'Flow Duration': flow_duration,
                    'Total Fwd Packets': total_fwd_packets,
                    'Total Backward Packets': total_bwd_packets,
                    'Total Length of Fwd Packets': fwd_bytes,
                    'Total Length of Bwd Packets': bwd_bytes,
                    'Fwd Packet Length Mean': fwd_mean,
                    'Bwd Packet Length Mean': bwd_mean,
                    'SYN Flag Count': syn_count,
                    'ACK Flag Count': ack_count
                }
                
                # Generate all 78 features
                features = generate_derived_features(user_inputs)
                
                response = requests.post(
                    f"{API_BASE_URL}/api/predict",
                    json={"features": features}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.markdown("---")
                    st.markdown("### 🎯 Prediction Results")
                    
                    # Create columns for results
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if result['is_attack']:
                            st.markdown(
                                '<div style="background-color: #ffe6e6; padding: 20px; '
                                'border-radius: 10px; border-left: 4px solid #ff6b6b;">'
                                '<h3 style="color: #cc0000; margin: 0;">🚨 ATTACK DETECTED</h3>'
                                '</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                '<div style="background-color: #e6ffe6; padding: 20px; '
                                'border-radius: 10px; border-left: 4px solid #51cf66;">'
                                '<h3 style="color: #2f5233; margin: 0;">✅ BENIGN TRAFFIC</h3>'
                                '</div>',
                                unsafe_allow_html=True
                            )
                    
                    with col2:
                        st.metric(
                            "Classification",
                            result['prediction'],
                            "Network Flow Type"
                        )
                    
                    with col3:
                        st.metric(
                            "Confidence Score",
                            f"{result['confidence']:.2%}",
                            "Detection Certainty"
                        )
                    
                    st.markdown("---")
                    
                    # Detailed probabilities
                    st.markdown("### 📊 Class Probabilities")
                    
                    prob_data = pd.DataFrame([
                        {
                            'Classification': k,
                            'Probability': f"{v:.2%}",
                            'Score': v
                        }
                        for k, v in result['probabilities'].items()
                    ]).sort_values('Score', ascending=False)
                    
                    # Create probability chart
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[
                        go.Bar(
                            x=prob_data['Classification'],
                            y=prob_data['Score'],
                            marker_color=['#ff6b6b' if c != 'BENIGN' else '#51cf66'
                                        for c in prob_data['Classification']],
                            text=[f"{v:.1%}" for v in prob_data['Score']],
                            textposition='outside'
                        )
                    ])
                    fig.update_layout(
                        title='Prediction Probability Distribution',
                        xaxis_title='Classification',
                        yaxis_title='Probability',
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("---")
                    
                    # Timestamp
                    st.caption(f"Prediction made at: {result['timestamp']}")
                    
                else:
                    st.error(f"Prediction failed: {response.json()}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Example values section
    st.markdown("---")
    st.markdown("### 💡 Example Network Flows")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "**Benign HTTP Traffic (Port 80)**\n\n"
            "Typical characteristics:\n"
            "- Destination Port: 80\n"
            "- Regular packet flow\n"
            "- Normal duration\n"
            "- Balanced flags"
        )
    
    with col2:
        st.warning(
            "**Potential Attack Pattern**\n\n"
            "Watch for:\n"
            "- Port scanning (unusual ports)\n"
            "- Unusual flow duration\n"
            "- Abnormal packet counts\n"
            "- Suspicious flag combinations"
        )
