from __future__ import annotations

import streamlit as st


def show():
    """Display the enhanced home/landing page with improved visuals and spacing."""
    
    st.markdown("""
        <div style='text-align: center; padding: 5rem 2rem; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px; margin-bottom: 3rem;
                    box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);'>
            <h1 style='font-size: 4rem; margin-bottom: 1.5rem; color: white; 
                       text-shadow: 2px 2px 8px rgba(0,0,0,0.3); font-weight: 700;'>
                StudyMate AI
            </h1>
            <p style='font-size: 1.8rem; color: #f0f0f0; margin-bottom: 2rem; font-weight: 300;'>
                Your Studies Companion
            </p>
            <p style='font-size: 1.1rem; color: #e8e8e8; max-width: 700px; margin: 0 auto; line-height: 1.6;'>
                Leverage the power of multiple AI engines to create comprehensive study materials tailored to your learning style
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; margin: 4rem 0 3rem 0;'>
            <h2 style='font-size: 2.5rem; color: #10b981; margin-bottom: 0.5rem; font-weight: 700;'>
                ✨ Features
            </h2>
            <p style='font-size: 1.1rem; color: #94a3b8;'>
                Everything you need to excel in your studies
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    features = [
        {
            "icon": "🔍",
            "title": "Smart Search",
            "desc": "Automatically finds relevant study materials from the web using advanced search algorithms"
        },
        {
            "icon": "📝",
            "title": "Summarization",
            "desc": "Converts complex content into easy-to-understand study notes with key concepts highlighted"
        },
        {
            "icon": "🎥",
            "title": "Video Resources",
            "desc": "Discovers the best tutorial videos for your topics from YouTube and educational platforms"
        },
        {
            "icon": "💻",
            "title": "Related Projects",
            "desc": "Finds GitHub and DockerHub projects for hands-on learning and practical experience"
        },
        {
            "icon": "✅",
            "title": "Quizzes & Exams",
            "desc": "Generates practice questions and finds past exam papers to test your knowledge"
        },
        {
            "icon": "🗺️",
            "title": "Study Roadmap",
            "desc": "Creates personalized learning paths based on your performance and learning goals"
        }
    ]
    
    for idx, feature in enumerate(features):
        col = [col1, col2, col3][idx % 3]
        with col:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                            padding: 2.5rem 2rem; border-radius: 16px; margin-bottom: 2rem;
                            border: 1px solid #334155; min-height: 280px;
                            transition: transform 0.3s ease, box-shadow 0.3s ease;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);'>
                    <div style='font-size: 3.5rem; margin-bottom: 1.5rem; text-align: center;'>{feature['icon']}</div>
                    <h3 style='color: #10b981; margin-bottom: 1rem; font-size: 1.5rem; text-align: center; font-weight: 600;'>
                        {feature['title']}
                    </h3>
                    <p style='color: #94a3b8; font-size: 0.95rem; line-height: 1.6; text-align: center;'>
                        {feature['desc']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 4rem 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; margin: 5rem 0 3rem 0;'>
            <h2 style='font-size: 2.5rem; color: #10b981; margin-bottom: 0.5rem; font-weight: 700;'>
                🚀 How It Works
            </h2>
            <p style='font-size: 1.1rem; color: #94a3b8;'>
                Three simple steps to academic success
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    step1, step2, step3 = st.columns(3, gap="large")
    
    steps = [
        {
            "num": "1",
            "title": "Input",
            "desc": "Enter your subject and chapter, or upload a course file to get started with personalized content"
        },
        {
            "num": "2",
            "title": "Process",
            "desc": "Our AI agents search, clean, and organize the information using advanced algorithms"
        },
        {
            "num": "3",
            "title": "Learn",
            "desc": "Get comprehensive study materials tailored to your needs and learning preferences"
        }
    ]
    
    for idx, step in enumerate(steps):
        col = [step1, step2, step3][idx]
        with col:
            st.markdown(f"""
                <div style='text-align: center; padding: 3rem 2rem 2.5rem 2rem; 
                            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                            border-radius: 16px; position: relative; min-height: 260px;
                            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
                            transition: transform 0.3s ease;'>
                    <div style='position: absolute; top: -25px; left: 50%; transform: translateX(-50%);
                                background: white; color: #10b981; width: 50px; height: 50px;
                                border-radius: 50%; display: flex; align-items: center; 
                                justify-content: center; font-weight: bold; font-size: 1.8rem;
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);'>
                        {step['num']}
                    </div>
                    <h3 style='color: white; margin-top: 1.5rem; margin-bottom: 1rem; font-size: 1.8rem; font-weight: 600;'>
                        {step['title']}
                    </h3>
                    <p style='color: #f0f0f0; font-size: 1rem; line-height: 1.6;'>
                        {step['desc']}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 5rem 0;'></div>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
            <div style='text-align: center; padding: 4rem 3rem;
                        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        border-radius: 20px; border: 2px solid #10b981;
                        box-shadow: 0 20px 60px rgba(16, 185, 129, 0.2);'>
                <h2 style='color: #10b981; margin-bottom: 1.5rem; font-size: 2.5rem; font-weight: 700;'>
                    Ready to boost your learning?
                </h2>
                <p style='font-size: 1.2rem; color: #94a3b8; margin-bottom: 2.5rem; line-height: 1.6;'>
                    Start generating personalized study materials now and take your learning to the next level!
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        
        if st.button("🚀 Get Started Now", type="primary", use_container_width=True):
            st.session_state.current_page = "Study"
            st.rerun()
    
    st.markdown("<div style='margin: 3rem 0;'></div>", unsafe_allow_html=True)
