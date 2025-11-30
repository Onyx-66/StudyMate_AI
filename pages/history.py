from __future__ import annotations

import streamlit as st
import pandas as pd


def show():
    """Display the enhanced study history page."""
    
    st.markdown("""
        <div style='background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0; font-size: 2.5rem;'>📊 Study History</h1>
            <p style='color: #f0f0f0; margin-top: 0.5rem; font-size: 1rem;'>
                View your past study sessions and track your progress
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    if "study_history" not in st.session_state:
        st.session_state.study_history = []
    
    history = st.session_state.study_history
    
    if not history:
        st.markdown("""
            <div style='text-align: center; padding: 4rem 2rem;
                        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        border-radius: 16px; border: 2px dashed #334155;'>
                <h2 style='color: #64748b; margin-bottom: 1rem;'>No Study Sessions Yet</h2>
                <p style='color: #94a3b8; font-size: 1.1rem;'>
                    Go to the <strong>Study</strong> page to generate your first study pack!
                </p>
            </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown("### Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    subjects = list(set([h["subject"] for h in history]))
    engines = list(set([h["engine"] for h in history]))
    total_resources = sum([len(h["help_types"]) for h in history])
    
    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>{len(history)}</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>Total Sessions</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>{len(subjects)}</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>Unique Subjects</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>{len(engines)}</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>AI Engines</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>{total_resources}</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>Resources</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Session History")
    
    df_data = []
    for idx, entry in enumerate(reversed(history), 1):
        df_data.append({
            "#": len(history) - idx + 1,
            "Date & Time": entry["timestamp"],
            "Subject": entry["subject"],
            "Chapter": entry["chapter"],
            "AI Engine": entry["engine"],
            "Resources": ", ".join(entry["help_types"])
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### Manage History")
    
    col_clear1, col_clear2 = st.columns([3, 1])
    
    with col_clear1:
        st.markdown("""
            <div style='background: #7f1d1d; padding: 1rem; border-radius: 8px; border: 1px solid #991b1b;'>
                <p style='color: #fca5a5; margin: 0;'>
                    ⚠️ Warning: This will permanently delete all history.
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_clear2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear History", type="secondary", use_container_width=True):
            st.session_state.study_history = []
            st.rerun()
