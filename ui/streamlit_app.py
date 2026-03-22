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

# Page configuration
st.set_page_config(
    page_title="Radiator Inspection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f5f5f5;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .ok-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    .not-ok-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 8px 12px;
        border-radius: 5px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000"

# Initialize session state
if 'inspection_results' not in st.session_state:
    st.session_state.inspection_results = []

# Header
st.title("🔍 Radiator Visual Inspection System")
st.markdown("AI-Powered Quality Control for Automotive Radiators")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Home", "Single Inspection", "Batch Inspection", "Results History", "Statistics"]
    )
    
    # API Health Check
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            st.success("✓ API Connected")
        else:
            st.error("✗ API Error")
    except:
        st.error("✗ API Unavailable")

# HOME PAGE
if page == "Home":
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 System Overview")
        st.info("""
        **Radiator Visual Inspection System**
        
        • Automated quality control using AI
        • Real-time component detection
        • Instant pass/fail decisions
        • Complete inspection reports
        """)
    
    with col2:
        st.markdown("### 🎯 Detection Components")
        components = [
            "✓ Fan Assembly",
            "✓ Connector",
            "✓ Pipe Routing",
            "✓ Drain Plug",
            "✓ Rubber Grommet",
            "✓ Mounting Clips",
            "✓ Radiator Fins"
        ]
        st.write("\n".join(components))
    
    st.divider()
    
    st.markdown("### 🚀 Quick Start")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Step 1: Upload Image**
        
        Go to "Single Inspection" to upload a radiator image
        """)
    
    with col2:
        st.markdown("""
        **Step 2: AI Analysis**
        
        The system analyzes the image and detects components
        """)
    
    with col3:
        st.markdown("""
        **Step 3: Results**
        
        Get instant OK/NOT OK result with details
        """)

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
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Inspect button
            if st.button("🔍 Run Inspection", key="inspect_btn", type="primary"):
                with st.spinner("Analyzing image..."):
                    try:
                        # Send to API
                        files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                        response = requests.post(f"{API_URL}/inspect", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.last_result = result
                            st.rerun()
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")
    
    with col2:
        st.subheader("Inspection Result")
        
        if 'last_result' in st.session_state:
            result = st.session_state.last_result
            
            # Status Badge
            status = result['status']
            if status == "OK":
                st.markdown(f"<div class='ok-badge'>✓ PASSED</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='not-ok-badge'>✗ FAILED</div>", unsafe_allow_html=True)
            
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
            st.dataframe(components_df, use_container_width=True, hide_index=True)
            
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
    
    if uploaded_files:
        st.write(f"📁 {len(uploaded_files)} image(s) selected")
        
        if st.button("🔍 Run Batch Inspection", type="primary"):
            with st.spinner("Processing images..."):
                try:
                    # Prepare files
                    files = [('files', (f.name, f.getvalue())) for f in uploaded_files]
                    response = requests.post(f"{API_URL}/inspect/batch", files=files)
                    
                    if response.status_code == 200:
                        batch_result = response.json()
                        
                        # Display results
                        st.divider()
                        st.subheader("📊 Batch Results")
                        
                        results_df = pd.DataFrame(batch_result['results'])
                        st.dataframe(results_df, use_container_width=True)
                        
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
                st.dataframe(results_df, use_container_width=True)
                
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
                st.metric("Total Inspections", stats['total_inspections'])
            with col2:
                st.metric("Passed", stats['passed'])
            with col3:
                st.metric("Failed", stats['failed'])
            with col4:
                st.metric("Pass Rate", f"{stats['pass_rate']:.1%}")
            
            st.divider()
            
            # Charts
            if stats['total_inspections'] > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Pie chart
                    fig = px.pie(
                        values=[stats['passed'], stats['failed']],
                        names=['Passed', 'Failed'],
                        title="Inspection Results Distribution",
                        color_discrete_map={'Passed': '#28a745', 'Failed': '#dc3545'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Pass rate metric
                    st.metric(
                        "Overall Quality Rate",
                        f"{stats['pass_rate']:.1%}",
                        delta=None,
                    )
                    st.info(f"""
                    **Summary**
                    - Inspections performed: {stats['total_inspections']}
                    - Quality radiators: {stats['passed']}
                    - Defective units: {stats['failed']}
                    """)
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Footer
st.divider()
st.markdown("""
---
**Radiator Visual Inspection System v1.0** | Powered by YOLOv8 & FastAPI
""")
