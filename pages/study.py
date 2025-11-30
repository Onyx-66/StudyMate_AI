from __future__ import annotations

import os
import re
from typing import Dict, Any, List
import streamlit as st

from agents import (
    get_llm,
    a1_everything,
    a2_cleaner,
    a3_adapter,
    a4_summarizer,
    a5_collector_videos,
    a6_relations_projects,
    a7_ai_companion_quiz,
    a8_examiner,
    a9_guide,
)

ENGINE_OPTIONS: Dict[str, Dict[str, str]] = {
    "Chat GPT 5.1 (OpenAI)": {"code": "openai", "env_var": "OPENAI_API_KEY"},
    "Deepseek 3.1": {"code": "deepseek", "env_var": "DEEPSEEK_API_KEY"},
    "Gemini 3.1": {"code": "gemini", "env_var": "GOOGLE_API_KEY"},
    "Grok 4.1": {"code": "grok", "env_var": "XAI_API_KEY"},
}
DEFAULT_ENGINE = "deepseek"

SUBJECTS_DB = {
    "Mathematics": ["Derivatives and Limits", "Integrals", "Linear Algebra", "Statistics", "Probability"],
    "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Physics", "Optics"],
    "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry"],
    "Computer Science": ["Data Structures", "Algorithms", "Operating Systems", "Networks", "Databases"],
    "Biology": ["Cell Biology", "Genetics", "Evolution", "Ecology", "Human Anatomy"],
    "History": ["World War 2", "Ancient Civilizations", "Industrial Revolution", "Cold War"],
    "Literature": ["Shakespeare", "Poetry Analysis", "Modern Literature", "Literary Criticism"],
    "Economics": ["Microeconomics", "Macroeconomics", "International Trade", "Game Theory"]
}


def check_api_key(env_var: str) -> bool:
    return bool(os.getenv(env_var))


def init_session_state():
    defaults = {
        "mas_output": None,
        "summary": "",
        "videos": "",
        "projects": "",
        "quizzes": "",
        "exams": "",
        "roadmap": "",
        "engine_code": DEFAULT_ENGINE,
        "help_types": ["Summarize (Default)", "Quizzes/Exercises"],
        "study_history": [],
        "quiz_score": 0,
        "quiz_answers": {},
        "quiz_submitted": False,
        "selected_subject": "Mathematics",
        "selected_chapter": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def sanitize_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        text = str(value)
        return text.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    except Exception:
        return "Error while preparing text for display."


def format_links_as_clickable(text: str) -> str:
    import re
    url_pattern = r'(https?://[^\s\)]+)'
    
    def replace_url(match):
        url = match.group(1)
        return f"[Click Here]({url})"
    
    return re.sub(url_pattern, replace_url, text)


def parse_projects(projects_text: str) -> Dict[str, List[Dict[str, str]]]:
    """Parse projects and separate GitHub from DockerHub."""
    github_projects = []
    docker_projects = []
    
    sections = projects_text.split("---------------------")
    
    for section in sections:
        is_github = "GitHub" in section or "github.com" in section
        is_docker = "DockerHub" in section or "hub.docker.com" in section or "Docker" in section
        
        entries = re.split(r'\[\d+\]', section)
        
        for entry in entries[1:]:
            lines = entry.strip().split('\n')
            if len(lines) >= 2:
                title = lines[0].strip()
                url = ""
                description = ""
                
                for line in lines[1:]:
                    if line.startswith("URL:"):
                        url = line.replace("URL:", "").strip()
                    elif line.startswith("Note:"):
                        description = line.replace("Note:", "").strip()
                
                repo_name = title
                creator = "Unknown"
                
                if "github.com" in url:
                    parts = url.split("github.com/")
                    if len(parts) > 1:
                        path_parts = parts[1].split("/")
                        if len(path_parts) >= 2:
                            creator = path_parts[0]
                            repo_name = path_parts[1]
                
                project_data = {
                    "title": title,
                    "repo_name": repo_name,
                    "creator": creator,
                    "url": url,
                    "description": description
                }
                
                if is_github or "github.com" in url:
                    github_projects.append(project_data)
                elif is_docker or "hub.docker.com" in url:
                    docker_projects.append(project_data)
    
    return {
        "github": github_projects,
        "docker": docker_projects
    }


def parse_videos(videos_text: str) -> List[Dict[str, str]]:
    videos = []
    entries = re.split(r'\[\d+\]', videos_text)
    
    for entry in entries[1:]:
        lines = entry.strip().split('\n')
        if len(lines) >= 2:
            title = lines[0].strip()
            url = lines[1].strip() if len(lines) > 1 else ""
            
            video_id = ""
            if "youtube.com/watch?v=" in url:
                video_id = url.split("watch?v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            
            videos.append({
                "title": title,
                "url": url,
                "video_id": video_id
            })
    
    return videos


def parse_quiz(quiz_text: str) -> Dict[str, Any]:
    quiz_data = {
        "questions": [],
        "exercises": []
    }
    
    parts = quiz_text.split("[EXERCISES]")
    quiz_section = parts[0].replace("[QUIZ]", "").strip()
    exercises_section = parts[1].strip() if len(parts) > 1 else ""
    
    question_pattern = r'Q(\d+):\s*(.*?)\nA\)(.*?)\nB\)(.*?)\nC\)(.*?)\nD\)(.*?)\nCorrect answer:\s*([A-D])'
    matches = re.findall(question_pattern, quiz_section, re.DOTALL)
    
    for match in matches:
        q_num, question, opt_a, opt_b, opt_c, opt_d, correct = match
        quiz_data["questions"].append({
            "number": int(q_num),
            "question": question.strip(),
            "options": {
                "A": opt_a.strip(),
                "B": opt_b.strip(),
                "C": opt_c.strip(),
                "D": opt_d.strip()
            },
            "correct": correct.strip()
        })
    
    exercise_pattern = r'E(\d+):\s*(.*?)(?=E\d+:|$)'
    ex_matches = re.findall(exercise_pattern, exercises_section, re.DOTALL)
    
    for match in ex_matches:
        e_num, exercise = match
        quiz_data["exercises"].append({
            "number": int(e_num),
            "text": exercise.strip()
        })
    
    return quiz_data


def run_pipeline(
    subject: str,
    chapter: str,
    help_types: list[str],
    guide_mode: bool,
    uploaded_file,
    engine_code: str,
) -> Dict[str, Any]:
    llm = get_llm(engine_code)

    context_text = ""
    a1_output = ""
    a2_output = ""
    a3_output = ""

    if uploaded_file is not None:
        a3_output = a3_adapter(uploaded_file)
        context_text = a3_output
    else:
        a1_output = a1_everything(subject, chapter)
        a2_output = a2_cleaner(llm, subject, a1_output)
        context_text = a2_output

    summary = a4_summarizer(llm, context_text, guide_mode=guide_mode)

    videos = ""
    projects = ""
    quizzes = ""
    exams = ""

    if "Videos" in help_types:
        videos = a5_collector_videos(subject, chapter)
    if "Related Projects" in help_types:
        projects = a6_relations_projects(subject, chapter)
    if "Quizzes/Exercises" in help_types:
        quizzes = a7_ai_companion_quiz(llm, summary)
    if "Exams" in help_types:
        exams = a8_examiner(subject, chapter)

    return {
        "a1_output": a1_output,
        "a2_output": a2_output,
        "a3_output": a3_output,
        "summary": summary,
        "videos": videos,
        "projects": projects,
        "quizzes": quizzes,
        "exams": exams,
    }


def show():
    """Display the study page."""
    init_session_state()

    st.markdown("""
        <div style='background: linear-gradient(90deg, #10b981 0%, #059669 100%);
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h1 style='color: white; margin: 0; font-size: 2.5rem;'>Your Studies Companion</h1>
            <p style='color: #f0f0f0; margin-top: 0.5rem; font-size: 1rem;'>
                Multi-Agent Study Assistant: Generate comprehensive study materials powered by AI
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Section 1
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 2rem;'>
            <h2 style='color: #10b981; margin-bottom: 1rem; display: flex; align-items: center;'>
                <span style='background: #10b981; color: white; width: 32px; height: 32px; 
                             border-radius: 50%; display: inline-flex; align-items: center; 
                             justify-content: center; margin-right: 0.75rem; font-size: 1.2rem;'>1</span>
                Subject Information
            </h2>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Speciality**")
        selected_subject = st.selectbox(
            "Choose speciality",
            options=list(SUBJECTS_DB.keys()),
            index=list(SUBJECTS_DB.keys()).index(st.session_state.selected_subject),
            key="subject_select",
            label_visibility="collapsed"
        )
        st.session_state.selected_subject = selected_subject
    
    with col2:
        st.markdown("**Subject (Matiere)**")
        subject = st.text_input(
            "Enter subject",
            value=selected_subject,
            key="subject_input",
            label_visibility="collapsed"
        )
    
    with col3:
        st.markdown("**Chapter (Chapitre)**")
        suggested_chapters = SUBJECTS_DB.get(selected_subject, [])
        
        if suggested_chapters:
            chapter_options = ["Custom..."] + suggested_chapters
            chapter_selection = st.selectbox(
                "Select or enter chapter",
                options=chapter_options,
                key="chapter_select",
                label_visibility="collapsed"
            )
            
            if chapter_selection == "Custom...":
                chapter = st.text_input(
                    "Enter custom chapter",
                    value="",
                    key="custom_chapter",
                    label_visibility="collapsed"
                )
            else:
                chapter = chapter_selection
        else:
            chapter = st.text_input(
                "Enter chapter",
                value="",
                key="chapter_input",
                label_visibility="collapsed"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Section 2
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 2rem;'>
            <h2 style='color: #10b981; margin-bottom: 1rem; display: flex; align-items: center;'>
                <span style='background: #10b981; color: white; width: 32px; height: 32px; 
                             border-radius: 50%; display: inline-flex; align-items: center; 
                             justify-content: center; margin-right: 0.75rem; font-size: 1.2rem;'>2</span>
                Optional: Upload Your Course File
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Drag and drop file here or click to browse",
        type=["pdf", "docx", "txt"],
        help="Limit 200MB per file • PDF, DOCX, TXT"
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Section 3
    st.markdown("""
        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 2rem;'>
            <h2 style='color: #10b981; margin-bottom: 1rem; display: flex; align-items: center;'>
                <span style='background: #10b981; color: white; width: 32px; height: 32px; 
                             border-radius: 50%; display: inline-flex; align-items: center; 
                             justify-content: center; margin-right: 0.75rem; font-size: 1.2rem;'>3</span>
                Select AI Engine and Help Options
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    col_engine, col_options = st.columns([1, 1])
    
    with col_engine:
        st.markdown("### AI Engine")
        engine_labels = list(ENGINE_OPTIONS.keys())
        default_label = "Deepseek 3.1"
        default_index = engine_labels.index(default_label) if default_label in engine_labels else 0
        engine_label = st.selectbox(
            "Choose your AI engine",
            engine_labels,
            index=default_index,
            key="engine_selector"
        )
        engine_info = ENGINE_OPTIONS[engine_label]
        engine_code = engine_info["code"]
        engine_env_var = engine_info["env_var"]

        st.session_state.engine_code = engine_code

        api_ok = check_api_key(engine_env_var)
        if api_ok:
            st.success(f"✓ {engine_label} key found")
        else:
            st.error(f"✗ {engine_label} key missing")

    with col_options:
        st.markdown("### Learning Resources")
        
        help_option_1 = st.checkbox("Summarize (Default)", value=True, key="help_summarize")
        help_option_2 = st.checkbox("Videos", value=False, key="help_videos")
        help_option_3 = st.checkbox("Related Projects", value=False, key="help_projects")
        help_option_4 = st.checkbox("Quizzes/Exercises", value=True, key="help_quizzes")
        help_option_5 = st.checkbox("Exams", value=False, key="help_exams")
        
        help_types = []
        if help_option_1:
            help_types.append("Summarize (Default)")
        if help_option_2:
            help_types.append("Videos")
        if help_option_3:
            help_types.append("Related Projects")
        if help_option_4:
            help_types.append("Quizzes/Exercises")
        if help_option_5:
            help_types.append("Exams")

        guide_mode = st.checkbox("Activate guide mode", value=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Generate study pack", type="primary", use_container_width=True):
        if not subject.strip() or not chapter.strip():
            st.error("⚠️ Please fill in both subject and chapter.")
        elif not check_api_key(engine_env_var):
            st.error(f"⚠️ {engine_label} key is missing.")
        else:
            with st.spinner("Running multi-agent pipeline..."):
                try:
                    output = run_pipeline(
                        subject=subject,
                        chapter=chapter,
                        help_types=help_types,
                        guide_mode=guide_mode,
                        uploaded_file=uploaded_file,
                        engine_code=engine_code,
                    )
                    st.session_state.mas_output = output
                    st.session_state.summary = output["summary"]
                    st.session_state.videos = output["videos"]
                    st.session_state.projects = output["projects"]
                    st.session_state.quizzes = output["quizzes"]
                    st.session_state.exams = output["exams"]
                    st.session_state.roadmap = ""
                    
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    
                    from datetime import datetime
                    history_entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "subject": subject,
                        "chapter": chapter,
                        "engine": engine_label,
                        "help_types": help_types
                    }
                    st.session_state.study_history.append(history_entry)
                    
                    st.success("✅ Study pack generated!")
                except Exception as exc:
                    st.error(f"❌ Error: {exc}")

    if st.session_state.mas_output is None:
        st.info("💡 Fill in the fields above and click **Generate study pack**.")
        return

    st.markdown("---")

    tabs = st.tabs([
        "Summary",
        "Videos",
        "Projects",
        "Quizzes",
        "Exams",
        "Roadmap",
        "Debug",
    ])

    with tabs[0]:
        st.markdown("### Summary")
        summary_text = sanitize_text(st.session_state.summary)
        formatted_summary = format_links_as_clickable(summary_text)
        st.markdown(formatted_summary)

    with tabs[1]:
        st.markdown("### Recommended Videos")
        if st.session_state.videos:
            videos = parse_videos(st.session_state.videos)
            
            for idx, video in enumerate(videos):
                with st.container():
                    col_img, col_details = st.columns([1, 2])
                    
                    with col_img:
                        if video["video_id"]:
                            thumbnail_url = f"https://img.youtube.com/vi/{video['video_id']}/mqdefault.jpg"
                            st.image(thumbnail_url, use_container_width=True)
                    
                    with col_details:
                        st.markdown(f"**{video['title']}**")
                        st.markdown(f"[▶️ Watch Video]({video['url']})")
                    
                    if idx < len(videos) - 1:
                        st.markdown("---")
        else:
            st.info("No videos generated.")

    with tabs[2]:
        st.markdown("### Related Projects")
        if st.session_state.projects:
            projects_dict = parse_projects(st.session_state.projects)
            
            # GitHub Projects
            if projects_dict["github"]:
                st.markdown("#### 🐙 GitHub Projects")
                for project in projects_dict["github"]:
                    with st.expander(f"**{project['repo_name']}** by {project['creator']}", expanded=False):
                        st.markdown(f"**Description:** {project['description']}")
                        st.markdown(f"**Link:** [View Repository]({project['url']})")
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Docker Projects
            if projects_dict["docker"]:
                st.markdown("#### 🐳 DockerHub Projects")
                for project in projects_dict["docker"]:
                    with st.expander(f"**{project['repo_name']}** by {project['creator']}", expanded=False):
                        st.markdown(f"**Description:** {project['description']}")
                        st.markdown(f"**Link:** [View Repository]({project['url']})")
        else:
            st.info("No projects generated.")

    with tabs[3]:
        st.markdown("### Quizzes and Exercises")
        
        if st.session_state.quizzes:
            quiz_data = parse_quiz(st.session_state.quizzes)
            
            total_questions = len(quiz_data["questions"])
            max_score = 20
            points_per_question = max_score / total_questions if total_questions > 0 else 0
            
            col_score1, col_score2 = st.columns([3, 1])
            with col_score1:
                st.progress(st.session_state.quiz_score / max_score if max_score > 0 else 0)
            with col_score2:
                st.markdown(f"### {st.session_state.quiz_score}/{max_score}")
            
            st.markdown("---")
            
            for q_idx, question in enumerate(quiz_data["questions"]):
                q_num = question["number"]
                
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                                padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;
                                margin-bottom: 1.5rem;'>
                        <h4 style='color: #10b981;'>Q{q_num}: {question['question']}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                question_key = f"q_{q_num}"
                current_answer = st.session_state.quiz_answers.get(question_key, None)
                
                for option_key, option_text in question["options"].items():
                    is_selected = current_answer == option_key
                    is_correct = option_key == question["correct"]
                    
                    # PINK before submit, GREEN/RED after
                    if st.session_state.quiz_submitted:
                        if is_selected:
                            if is_correct:
                                bg_color = "#10b981"
                                border_color = "#059669"
                            else:
                                bg_color = "#ef4444"
                                border_color = "#dc2626"
                        else:
                            bg_color = "#1e293b"
                            border_color = "#334155"
                    else:
                        if is_selected:
                            bg_color = "#ec4899"  # PINK
                            border_color = "#db2777"
                        else:
                            bg_color = "#1e293b"
                            border_color = "#334155"
                    
                    col_opt_label, col_opt_button = st.columns([0.08, 0.92])
                    
                    with col_opt_label:
                        st.markdown(f"**{option_key})**")
                    
                    with col_opt_button:
                        if not st.session_state.quiz_submitted:
                            if st.button(
                                option_text,
                                key=f"btn_{question_key}_{option_key}",
                                use_container_width=True
                            ):
                                st.session_state.quiz_answers[question_key] = option_key
                                st.rerun()
                        else:
                            st.markdown(f"""
                                <div style='background: {bg_color}; color: white; padding: 0.75rem 1rem;
                                            border: 2px solid {border_color}; border-radius: 8px;
                                            margin-bottom: 0.5rem;'>
                                    {option_text}
                                </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            if not st.session_state.quiz_submitted:
                if st.button("Submit Answers", type="primary", use_container_width=True):
                    score = 0
                    for question in quiz_data["questions"]:
                        question_key = f"q_{question['number']}"
                        if st.session_state.quiz_answers.get(question_key) == question["correct"]:
                            score += points_per_question
                    
                    st.session_state.quiz_score = round(score, 1)
                    st.session_state.quiz_submitted = True
                    st.rerun()
            else:
                st.success(f"Score: {st.session_state.quiz_score}/{max_score}")
                if st.button("Retake Quiz", use_container_width=True):
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_score = 0
                    st.rerun()
            
            if quiz_data["exercises"]:
                st.markdown("---")
                st.markdown("### Exercises")
                for exercise in quiz_data["exercises"]:
                    st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                                    padding: 1.5rem; border-radius: 12px; border: 1px solid #334155;
                                    margin-bottom: 1rem;'>
                            <strong>E{exercise['number']}:</strong> {exercise['text']}
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### Personalize Your Roadmap")
            
            if st.button("Generate Roadmap", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        engine_code_for_roadmap = st.session_state.get("engine_code", DEFAULT_ENGINE)
                        llm_for_roadmap = get_llm(engine_code_for_roadmap)
                        
                        score_ratio = st.session_state.quiz_score / max_score
                        correct_answers = round(score_ratio * 3)
                        
                        roadmap = a9_guide(
                            llm=llm_for_roadmap,
                            summary=st.session_state.summary,
                            self_score=correct_answers,
                            total_questions=3,
                        )
                        st.session_state.roadmap = roadmap
                        st.success("✅ Roadmap generated!")
                    except Exception as exc:
                        st.error(f"Error: {exc}")
        else:
            st.info("No quizzes generated.")

    with tabs[4]:
        st.markdown("### Past Exam PDFs")
        if st.session_state.exams:
            exams_text = sanitize_text(st.session_state.exams)
            formatted_exams = format_links_as_clickable(exams_text)
            st.markdown(formatted_exams)
        else:
            st.info("No exams generated.")

    with tabs[5]:
        st.markdown("### Study Roadmap")
        if st.session_state.roadmap:
            roadmap_text = sanitize_text(st.session_state.roadmap)
            formatted_roadmap = format_links_as_clickable(roadmap_text)
            st.markdown(formatted_roadmap)
        else:
            st.info("Generate roadmap from Quizzes tab.")

    with tabs[6]:
        st.markdown("### Debug Information - AI Agents Workflow")
        output = st.session_state.mas_output

        st.markdown("""
            <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        padding: 1.5rem; border-radius: 12px; border: 1px solid #334155; margin-bottom: 1rem;'>
                <h3 style='color: #10b981;'>Pipeline Execution Summary</h3>
                <p style='color: #94a3b8;'>Below is the detailed workflow of each AI agent in the pipeline.</p>
            </div>
        """, unsafe_allow_html=True)

        # Agent 1
        with st.expander("🔍 A1_Everything - Web Search Agent", expanded=False):
            st.markdown("**Function:** Global web search for study materials")
            st.markdown("**Input:** Subject and Chapter")
            st.markdown("**Output:** Raw web search results with URLs and snippets")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("a1_output") else "⏭️ Skipped (file uploaded)"))
            st.text(sanitize_text(output.get("a1_output") or "Skipped - File was uploaded"))

        # Agent 2
        with st.expander("🧹 A2_Cleaner - Content Filter Agent", expanded=False):
            st.markdown("**Function:** Filters and cleans raw search results")
            st.markdown("**Input:** Raw web search output from A1")
            st.markdown("**Output:** Cleaned, relevant content grouped by topic")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("a2_output") else "⏭️ Skipped (file uploaded)"))
            st.text(sanitize_text(output.get("a2_output") or "Skipped - File was uploaded"))

        # Agent 3
        with st.expander("📄 A3_Adapter - File Ingestion Agent", expanded=False):
            st.markdown("**Function:** Extracts text from uploaded files")
            st.markdown("**Input:** PDF, DOCX, or TXT file")
            st.markdown("**Output:** Plain text content from the file")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("a3_output") and "ERROR" not in output.get("a3_output", "") else "⏭️ No file uploaded"))
            st.text(sanitize_text(output.get("a3_output") or "No file uploaded"))

        # Agent 4
        with st.expander("📝 A4_Summarizer - Study Notes Generator", expanded=False):
            st.markdown("**Function:** Creates study notes from cleaned content")
            st.markdown("**Input:** Cleaned context from A2 or A3")
            st.markdown("**Output:** Structured study notes with key concepts")
            st.markdown("**Status:** ✅ Executed")
            st.text(sanitize_text(output.get("summary")))

        # Agent 5
        with st.expander("🎥 A5_Collector - Video Search Agent", expanded=False):
            st.markdown("**Function:** Finds relevant YouTube tutorial videos")
            st.markdown("**Input:** Subject and Chapter")
            st.markdown("**Output:** List of video titles and URLs")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("videos") else "⏭️ Not requested"))
            st.text(sanitize_text(output.get("videos") or "Not requested"))

        # Agent 6
        with st.expander("💻 A6_Relations - Projects Finder Agent", expanded=False):
            st.markdown("**Function:** Searches GitHub and DockerHub for related projects")
            st.markdown("**Input:** Subject and Chapter")
            st.markdown("**Output:** Project listings with descriptions and URLs")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("projects") else "⏭️ Not requested"))
            st.text(sanitize_text(output.get("projects") or "Not requested"))

        # Agent 7
        with st.expander("✅ A7_AI_Companion - Quiz Generator Agent", expanded=False):
            st.markdown("**Function:** Generates practice questions and exercises")
            st.markdown("**Input:** Summary from A4")
            st.markdown("**Output:** MCQ questions and open exercises")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("quizzes") else "⏭️ Not requested"))
            st.text(sanitize_text(output.get("quizzes") or "Not requested"))

        # Agent 8
        with st.expander("📄 A8_Examiner - Exam Finder Agent", expanded=False):
            st.markdown("**Function:** Searches for past exam papers")
            st.markdown("**Input:** Subject and Chapter")
            st.markdown("**Output:** List of exam PDF links")
            st.markdown("**Status:** " + ("✅ Executed" if output.get("exams") else "⏭️ Not requested"))
            st.text(sanitize_text(output.get("exams") or "Not requested"))

        # Agent 9
        with st.expander("🗺️ A9_Guide - Roadmap Generator Agent", expanded=False):
            st.markdown("**Function:** Creates personalized study roadmap")
            st.markdown("**Input:** Summary and quiz performance")
            st.markdown("**Output:** Step-by-step learning plan")
            st.markdown("**Status:** " + ("✅ Executed" if st.session_state.roadmap else "⏭️ Not generated yet"))
            st.text(sanitize_text(st.session_state.roadmap or "Not generated yet"))

        st.markdown("""
            <div style='background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                        padding: 1.5rem; border-radius: 12px; border: 1px solid #10b981; margin-top: 1rem;'>
                <h4 style='color: #10b981;'>Pipeline Flow</h4>
                <p style='color: #94a3b8;'>A1 → A2 → A4 → {A5, A6, A7, A8} → A9</p>
                <p style='color: #94a3b8; font-size: 0.9rem;'>Or: A3 → A4 → {A5, A6, A7, A8} → A9 (when file is uploaded)</p>
            </div>
        """, unsafe_allow_html=True)
