from __future__ import annotations

import streamlit as st
from datetime import datetime


def init_community_state():
    """Initialize community chat state."""
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "user": "StudyMate Bot",
                "message": "Welcome to the StudyMate Community! Share your learning journey, ask questions, and help others.",
                "timestamp": datetime.now().strftime("%H:%M"),
                "is_bot": True
            }
        ]
    if "current_user" not in st.session_state:
        st.session_state.current_user = "Student"


def show():
    """Display the community chat page."""
    init_community_state()
    
    st.markdown("""
        <div style='background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%);
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0; font-size: 2.5rem;'>👥 Community</h1>
            <p style='color: #f0f0f0; margin-top: 0.5rem; font-size: 1rem;'>
                Connect with fellow learners, share knowledge, and grow together
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>1,234</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>Active Members</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>5,678</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>Messages Today</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                        padding: 1.5rem; border-radius: 12px; text-align: center;'>
                <h3 style='color: white; margin: 0; font-size: 2rem;'>892</h3>
                <p style='color: #f0f0f0; margin: 0.5rem 0 0 0;'>Topics Discussed</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;'>
            <h2 style='color: #10b981; margin-bottom: 1rem;'>💬 General Chat</h2>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    messages_container = st.container()
    
    with messages_container:
        for msg in st.session_state.chat_messages:
            if msg.get("is_bot", False):
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                                padding: 1rem; border-radius: 12px; margin-bottom: 1rem;
                                border-left: 4px solid #10b981;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                            <strong style='color: #10b981;'>🤖 {msg['user']}</strong>
                            <span style='color: #64748b; font-size: 0.85rem;'>{msg['timestamp']}</span>
                        </div>
                        <p style='color: #94a3b8; margin: 0;'>{msg['message']}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                                padding: 1rem; border-radius: 12px; margin-bottom: 1rem;
                                border-left: 4px solid #3b82f6;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                            <strong style='color: #3b82f6;'>👤 {msg['user']}</strong>
                            <span style='color: #64748b; font-size: 0.85rem;'>{msg['timestamp']}</span>
                        </div>
                        <p style='color: #94a3b8; margin: 0;'>{msg['message']}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("message_form", clear_on_submit=True):
        col_input, col_button = st.columns([4, 1])
        
        with col_input:
            message_input = st.text_input(
                "Type your message...",
                key="message_input",
                label_visibility="collapsed",
                placeholder="Share your thoughts, ask questions, or help others..."
            )
        
        with col_button:
            submit_button = st.form_submit_button("Send", use_container_width=True, type="primary")
        
        if submit_button and message_input.strip():
            new_message = {
                "user": st.session_state.current_user,
                "message": message_input,
                "timestamp": datetime.now().strftime("%H:%M"),
                "is_bot": False
            }
            st.session_state.chat_messages.append(new_message)
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Quick Actions")
    
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("💡 Ask a Question", use_container_width=True):
            st.info("Type your question in the chat above!")
    
    with col_action2:
        if st.button("📚 Share Resources", use_container_width=True):
            st.info("Share helpful study materials in the chat!")
    
    with col_action3:
        if st.button("🤝 Find Study Buddy", use_container_width=True):
            st.info("Connect with other learners!")
