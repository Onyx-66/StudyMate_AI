from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="StudyMate AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
        }
        
        .main .block-container {
            padding-top: 2rem;
            max-width: 1400px;
        }
        
        .stExpander {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
        }
        
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }
        
        [data-testid="stFileUploader"] {
            border: 2px dashed #4a5568;
            border-radius: 12px;
            padding: 2rem;
            background-color: #1a202c;
            transition: all 0.3s ease;
        }
        
        [data-testid="stFileUploader"]:hover {
            border-color: #10b981;
            background-color: #1e293b;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #1e293b;
            padding: 0.5rem;
            border-radius: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #10b981;
        }
        
        .stProgress > div > div {
            background-color: #10b981;
        }
        
        .stSelectbox, .stTextInput {
            margin-bottom: 1rem;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .element-container {
            animation: fadeIn 0.3s ease;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Logo with clickable link to home
    st.markdown("""
        <div style='text-align: left; padding: 1rem 0; border-bottom: 2px solid #334155;'>
            <h1 style='color: #10b981; font-size: 1.5rem; margin: 0;'>
                StudyMate AI
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Make logo clickable
    if st.button("← Home", key="logo_home", use_container_width=True):
        st.session_state.current_page = "Home"
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Navigation section
    st.markdown("""
        <div style='padding: 0 0.5rem;'>
            <p style='color: #64748b; font-size: 0.75rem; text-transform: uppercase; 
                      letter-spacing: 1px; margin-bottom: 0.5rem; font-weight: 600;'>
                Navigation
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    
    pages = {
        "Home": "🏠",
        "Study": "📚",
        "Community": "👥",
        "History": "📊"
    }
    
    for page_name, icon in pages.items():
        is_selected = st.session_state.current_page == page_name
        
        if st.button(
            f"{icon} {page_name}", 
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        ):
            st.session_state.current_page = page_name
            st.rerun()
    
    # Footer
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='position: fixed; bottom: 0; left: 0; right: 0; padding: 1.5rem; 
                    border-top: 1px solid #334155; 
                    background: linear-gradient(180deg, transparent 0%, #0f1419 100%);
                    width: inherit;'>
            <p style='color: #64748b; font-size: 0.75rem; text-align: center; margin: 0;'>
                Made with ❤️ for Education
            </p>
            <p style='color: #475569; font-size: 0.7rem; text-align: center; margin-top: 0.25rem;'>
                Powered by Onyx Team
            </p>
        </div>
    """, unsafe_allow_html=True)

# Main content
page = st.session_state.current_page

if page == "Home":
    from pages import home
    home.show()
elif page == "Study":
    from pages import study
    study.show()
elif page == "Community":
    from pages import community
    community.show()
elif page == "History":
    from pages import history
    history.show()
