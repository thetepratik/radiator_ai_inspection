"""
Custom CSS styles for the Radiator Inspection System
Provides a premium, professional look with glassmorphism and modern UI elements.
"""

CSS = """
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        margin-bottom: 20px;
    }

    /* Premium Metric Card */
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border-left: 5px solid #007bff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-ok {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-fail {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #1a1c23;
        margin-bottom: 5px;
    }
    .sub-header {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    /* Custom Dataframe */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Button Styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
"""
