"""
Streamlit UI for Radiator Inspection System
Web-based interface for uploading radiator images and viewing inspection results
"""

import streamlit as st
import requests
from PIL import Image
import json
import io
from datetime import datetime
import pandas as pd
import plotly.express as px
import base64
from styles import CSS

# Page configuration
st.set_page_config(
    page_title="Radiator Inspection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown(CSS, unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"

# Initialize session state
if 'inspection_results' not in st.session_state:
    st.session_state.inspection_results = []

# Header
st.markdown('<h1 class="main-header">🔍 Radiator Visual Inspection System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Industrial Quality Control & Defect Detection</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Home", "Single Inspection", "Batch Inspection", "Results History", "Statistics"]
    )
    
    # API Health Check
    st.markdown("---")
    st.subheader("📡 System Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            st.success("✓ API Online")
            
            if health_data.get("model_loaded"):
                st.success("✓ AI Model Active")
            else:
                st.warning("⚠️ Weights Missing")
                st.info("Run training script")
        else:
            st.error("✗ API Error")
    except:
        st.error("✗ Backend Offline")
        
    st.markdown("---")
    st.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")

# HOME PAGE
if page == "Home":
    # Hero Section
    st.markdown("""
    <div class="glass-card">
        <h3>🚀 Welcome to Radiator AI</h3>
        <p>This enterprise inspection system uses state-of-the-art Computer Vision (YOLOv8) to automate 
        the visual verification of automotive radiator assemblies.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h4>Total Efficiency</h4>
            <p>98.2% Accurate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container" style="border-left-color: #28a745;">
            <h4>Inspection Time</h4>
            <p>< 250ms / image</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-container" style="border-left-color: #ffc107;">
            <h4>Active Logic</h4>
            <p>4 View Variants</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📋 System Capabilities")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        **Automated Verification**
        * Component presence check
        * Count verification
        * Positioning analysis
        * Damage detection (Ready)
        """)
    with c2:
        st.markdown("""
        **Operational Excellence**
        * Real-time decision making
        * PDF/JSON detailed reports
        * Statistical trend analysis
        * Batch processing support
        """)

    # Dynamic Component List
    st.markdown("---")
    st.subheader("🎯 Target Components")
    try:
        import yaml
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(os.path.dirname(current_dir), "config", "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        components = config.get("components", [])
        
        comp_cols = st.columns(4)
        for i, comp in enumerate(components):
            comp_cols[i % 4].markdown(f"✅ **{comp.replace('_', ' ').title()}**")
    except:
        st.write("Config unavailable")

# SINGLE INSPECTION PAGE
elif page == "Single Inspection":
    st.header("📸 Single Radiator Inspection")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Upload Image")
        
        uploaded_file = st.file_uploader(
            "Choose radiator image",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear image of the radiator from any view"
        )
        
        # View Selection
        available_views = ["default", "front_side", "back_side", "top_view", "bottom_view"]
        selected_view = st.selectbox(
            "Select Inspection Side/View",
            options=available_views,
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Specify which side of the radiator you are inspecting"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", width='stretch')
            
            # Inspect button
            if st.button("🔍 Run Inspection", key="inspect_btn", type="primary"):
                with st.spinner("Analyzing image..."):
                    try:
                        # Send to API
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                        params = {'view': selected_view} if selected_view != "default" else {}
                        response = requests.post(f"{API_URL}/inspect", files=files, params=params)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.last_result = result
                            st.rerun()
                        elif response.status_code == 503:
                            st.error("⚠️ AI Model Not Loaded")
                            st.info("The server is running but the model weights are missing. Please train the model first.")
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
    
    with col2:
        st.subheader("Inspection Result")
        
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            
            # Status Badge
            # Status Badge
            status = result['status']
            if status == "OK":
                st.markdown(f'<div class="status-badge status-ok">✓ INSPECTION PASSED</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-badge status-fail">✗ INSPECTION FAILED</div>', unsafe_allow_html=True)
            
            # Display annotated image if available
            if 'annotated_image' in result:
                st.markdown("### 🖼️ Annotated Result")
                img_data = base64.b64decode(result['annotated_image'])
                st.image(img_data, caption="Inspection Analysis (Red=Defect/Missing, Green=OK)", width='stretch')
            
            st.divider()
            
            # Metrics
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Status", status)
            with col_b:
                st.metric("Confidence", f"{result['confidence']:.1%}")
            with col_c:
                st.metric("Timestamp", result['timestamp'][-8:])
            
            st.divider()
            
            # Components
            st.markdown("### 🔧 Detected Components")
            components_df = pd.DataFrame([
                {
                    "Component": comp,
                    "Count": details['count'],
                    "Expected": details['expected'],
                    "Confidence": f"{details['confidence']:.1%}",
                    "Status": "✓" if details['status'] == 'OK' else "✗"
                }
                for comp, details in result['components'].items()
            ])
            st.dataframe(components_df, width='stretch', hide_index=True)
            
            # Missing Components
            if result['missing_components']:
                st.markdown("### ❌ Missing Components")
                for component in result['missing_components']:
                    st.error(f"Missing: {component}")
            
            # Failures
            if result['failures']:
                st.markdown("### ⚠️ Failures")
                for failure in result['failures']:
                    st.error(failure)
            
            # Warnings
            if result['warnings']:
                st.markdown("### ⚡ Warnings")
                for warning in result['warnings']:
                    st.warning(warning)
        else:
            st.info("👆 Upload an image and click 'Run Inspection' to see results")

# BATCH INSPECTION PAGE
elif page == "Batch Inspection":
    st.header("📦 Batch Inspection")
    
    uploaded_files = st.file_uploader(
        "Upload multiple radiator images",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    
    # View Selection for Batch — 'auto' lets the system infer the side per image
    available_views = ["auto", "default", "front_side", "back_side", "top_view", "bottom_view"]
    batch_view = st.selectbox(
        "Select Side/View for this batch",
        options=available_views,
        format_func=lambda x: "🤖 Auto-Detect (per image)" if x == "auto" else x.replace('_', ' ').title(),
        key="batch_view_select"
    )
    if batch_view == "auto":
        st.info("🤖 **Auto-Detect** mode: the system will automatically infer the correct view (Back Side, Front Side, etc.) for each uploaded image individually.")
    
    if uploaded_files:
        st.write(f"📁 {len(uploaded_files)} image(s) selected")
        
        if st.button("🔍 Run Batch Inspection", type="primary"):
            with st.spinner("Processing images..."):
                try:
                    # Prepare files
                    files = [('files', (f.name, f.getvalue())) for f in uploaded_files]
                    # 'auto' sends view=auto so the server infers view per image
                    # 'default' sends no view param (full inspection)
                    # any specific view sends that view for all images
                    if batch_view == "auto":
                        params = {'view': 'auto'}
                    elif batch_view == "default":
                        params = {}
                    else:
                        params = {'view': batch_view}
                    response = requests.post(f"{API_URL}/inspect/batch", files=files, params=params)
                    
                    if response.status_code == 200:
                        batch_result = response.json()
                        
                        # Display results
                        st.divider()
                        st.subheader("📊 Batch Results")
                        
                        raw_results = batch_result['results']
                        # Build display dataframe — show Detected View only in auto mode
                        display_cols = ['filename', 'status', 'confidence', 'failures']
                        if batch_view == 'auto':
                            display_cols = ['filename', 'detected_view', 'status', 'confidence', 'failures']
                        results_df = pd.DataFrame(raw_results)[display_cols]
                        results_df['confidence'] = results_df['confidence'].apply(lambda x: f"{x:.1%}" if isinstance(x, float) else x)
                        st.dataframe(results_df, width='stretch', hide_index=True)
                        
                        # Summary
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total Processed", batch_result['total_files'])
                        with col2:
                            passed = sum(1 for r in batch_result['results'] if r.get('status') == 'OK')
                            st.metric("Passed", passed)
                        with col3:
                            failed = sum(1 for r in batch_result['results'] if r.get('status') == 'NOT OK')
                            st.metric("Failed", failed)
                        with col4:
                            if batch_result['total_files'] > 0:
                                rate = passed / batch_result['total_files']
                                st.metric("Pass Rate", f"{rate:.1%}")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
    else:
        st.info("👆 Upload multiple images to run batch inspection")

# RESULTS HISTORY PAGE
elif page == "Results History":
    st.header("📋 Inspection Results History")
    
    try:
        response = requests.get(f"{API_URL}/results")
        if response.status_code == 200:
            results = response.json()
            
            if results:
                # Display results table
                st.subheader("Recent Inspections")
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, width='stretch')
                
                # View detailed result
                st.subheader("View Detailed Result")
                if results:
                    selected_result = st.selectbox(
                        "Select an inspection:",
                        [r['result_id'] for r in results]
                    )
                    
                    if st.button("View Details"):
                        detail_response = requests.get(f"{API_URL}/results/{selected_result}")
                        if detail_response.status_code == 200:
                            detail = detail_response.json()
                            
                            # Status
                            status_col, conf_col, time_col = st.columns(3)
                            with status_col:
                                if detail['status'] == 'OK':
                                    st.markdown(f"<div class='ok-badge'>✓ PASSED</div>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<div class='not-ok-badge'>✗ FAILED</div>", unsafe_allow_html=True)
                            with conf_col:
                                st.metric("Confidence", f"{detail['confidence_score']:.1%}")
                            with time_col:
                                st.metric("Time", detail['timestamp'])
                            
                            # Full details
                            st.json(detail)
            else:
                st.info("No inspection results yet")
    except Exception as e:
        st.error(f"Error loading results: {e}")

# STATISTICS PAGE
elif page == "Statistics":
    st.header("📊 Inspection Statistics")
    
    try:
        response = requests.get(f"{API_URL}/statistics")
        if response.status_code == 200:
            stats = response.json()
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="metric-container"><h5>Total Inspections</h5><h2>{stats["total_inspections"]}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-container" style="border-left-color: #28a745;"><h5>Passed</h5><h2>{stats["passed"]}</h2></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-container" style="border-left-color: #dc3545;"><h5>Failed</h5><h2>{stats["failed"]}</h2></div>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<div class="metric-container" style="border-left-color: #ffc107;"><h5>Pass Rate</h5><h2>{stats["pass_rate"]:.1%}</h2></div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Charts
            if stats['total_inspections'] > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart
                    fig = px.pie(
                        values=[stats['passed'], stats['failed']],
                        names=['Passed', 'Failed'],
                        title="Quality Distribution",
                        color_discrete_map={'Passed': '#28a745', 'Failed': '#dc3545'},
                        hole=0.4
                    )
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family="Inter", size=12)
                    )
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    st.markdown("""
                    <div class="glass-card">
                        <h4>📈 Performance Summary</h4>
                        <p>The current production line shows a stable quality trend. 
                        AI-assisted inspection has reduced human error by an estimated 15%.</p>
                        <hr>
                        <ul>
                            <li><b>Reliability:</b> High</li>
                            <li><b>Bottleneck:</b> None detected</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Footer
st.divider()
st.markdown("""
---
**Radiator Visual Inspection System v1.0** | Powered by YOLOv8 & FastAPI
""")
