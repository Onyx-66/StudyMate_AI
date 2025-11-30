from __future__ import annotations

import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_deepseek import ChatDeepSeek
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_xai import ChatXAI

from utils import (
    extract_text_from_file,
    search_text,
    search_videos,
    search_projects,
    search_exams,
)

# Load environment variables from .env into environment
load_dotenv()

parser = StrOutputParser()


class EngineError(RuntimeError):
    """Raised when an AI engine cannot be initialized (missing key, etc.)."""


def get_llm(engine_code: str):
    """
    Return a LangChain chat model based on engine_code.

    engine_code:
      - "openai"  -> OpenAI (Chat GPT 5.1 in the UI)
      - "deepseek" -> Deepseek 3.1
      - "gemini" -> Gemini 3.1
      - "grok"   -> Grok 4.1
    """
    engine = (engine_code or "").lower()

    if engine == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EngineError(
                "OPENAI_API_KEY is missing. Add it to your .env file to use Chat GPT 5.1."
            )
        return ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.2,
            api_key=api_key,
        )

    if engine == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise EngineError(
                "DEEPSEEK_API_KEY is missing. Add it to your .env file to use Deepseek 3.1."
            )
        return ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.2,
            api_key=api_key,
        )

    if engine == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EngineError(
                "GOOGLE_API_KEY is missing. Add it to your .env file to use Gemini 3.1."
            )
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.2,
            google_api_key=api_key,
        )

    if engine == "grok":
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise EngineError(
                "XAI_API_KEY is missing. Add it to your .env file to use Grok 4.1."
            )
        return ChatXAI(
            model="grok-4",
            temperature=0.2,
            api_key=api_key,
        )

    raise EngineError(f"Unknown engine code '{engine_code}'. Use openai/deepseek/gemini/grok.")


def a1_everything(subject: str, chapter: str) -> str:
    """
    A1_Everything: global web search for the specific chapter.
    """
    query = f"{subject} {chapter} course explanation pdf"
    results = search_text(query, max_results=6)
    if not results:
        return "No web results were found."
    lines: List[str] = []
    for idx, r in enumerate(results, start=1):
        title = r.get("title") or "No title"
        href = r.get("href") or r.get("url") or ""
        body = r.get("body") or r.get("description") or ""
        lines.append(f"[{idx}] {title}\nURL: {href}\nSnippet: {body}\n")
    return "\n\n".join(lines)


def a2_cleaner(llm, subject: str, raw_results: str) -> str:
    """
    A2_Cleaner: keep only information that is relevant to the subject.
    """
    prompt = ChatPromptTemplate.from_template(
        """
You are A2_Cleaner, a strict relevance filter for study material.

User subject: {subject}

Below is raw web search output with mixed relevance:

---------------- RAW RESULTS ----------------
{raw_results}
---------------------------------------------

Task:
1) Keep only content that is clearly about the subject (matiere) above.
2) Discard unrelated topics, advertisements, duplicate links, and off-topic material.
3) Output a cleaned, compact textual context (NOT a summary), grouping related ideas.
4) Preserve useful URLs in parentheses after each bullet when available.

Return ONLY the cleaned context, ready for summarization.
"""
    )
    chain = prompt | llm | parser
    try:
        return chain.invoke({"subject": subject, "raw_results": raw_results})
    except Exception as exc:
        return f"[A2_Cleaner ERROR] {exc}"


def a3_adapter(file) -> str:
    """
    A3_Adapter: file ingestion agent.
    Uses utils.extract_text_from_file to read PDF / DOCX / TXT.
    """
    try:
        text = extract_text_from_file(file)
        if not text.strip():
            return "Uploaded file contains no readable text."
        return text
    except Exception as exc:
        return f"[A3_Adapter ERROR] Could not read file: {exc}"


def a4_summarizer(llm, context: str, guide_mode: bool) -> str:
    """
    A4_Summarizer: convert context into easy study notes.
    """
    prompt = ChatPromptTemplate.from_template(
        """
You are A4_Summarizer, a patient study coach.

You receive context extracted from web results or from the student course file.

---------------- CONTEXT ----------------
{context}
-----------------------------------------

Write clear, concise study notes for a beginner:
- Start with a short overview (3 to 4 lines) of the chapter.
- Then list the key concepts as bullet points.
- For each concept, explain it in simple language and add one short example.
- End with a short "What you must remember" list.

Guide mode is: {guide_mode}

If guide_mode is True:
- Add a final section called "Mini study plan for this chapter" with:
  - Step 1: what to read
  - Step 2: what to write or summarize
  - Step 3: what to practice (questions, exercises, etc.).

Answer in the same language as the context if obvious, otherwise default to English.
"""
    )
    chain = prompt | llm | parser
    try:
        return chain.invoke({"context": context, "guide_mode": guide_mode})
    except Exception as exc:
        return f"[A4_Summarizer ERROR] {exc}"


def a5_collector_videos(subject: str, chapter: str) -> str:
    """
    A5_Collector: search for video tutorials.
    """
    query = f"{subject} {chapter} tutorial site:youtube.com OR site:youtu.be"
    results = search_videos(query, max_results=5)
    if not results:
        return "No videos found."
    lines: List[str] = []
    for idx, r in enumerate(results, start=1):
        title = r.get("title") or "No title"
        href = r.get("href") or r.get("url") or ""
        lines.append(f"[{idx}] {title}\n{href}")
    return "\n\n".join(lines)


def a6_relations_projects(subject: str, chapter: str) -> str:
    """
    A6_Relations: GitHub and DockerHub related projects.
    """
    query_code = f"{subject} {chapter} project example site:github.com"
    query_docker = f"{subject} {chapter} lab exercise site:hub.docker.com"
    results_code = search_projects(query_code, max_results=5)
    results_docker = search_projects(query_docker, max_results=5)

    if not results_code and not results_docker:
        return "No related open source projects were found."

    def fmt(results: List[Dict[str, str]]) -> List[str]:
        items: List[str] = []
        for idx, r in enumerate(results, start=1):
            title = r.get("title") or "No title"
            href = r.get("href") or r.get("url") or ""
            body = r.get("body") or r.get("description") or ""
            items.append(f"[{idx}] {title}\nURL: {href}\nNote: {body}")
        return items

    sections: List[str] = []
    if results_code:
        sections.append("GitHub projects:\n" + "\n\n".join(fmt(results_code)))
    if results_docker:
        sections.append("DockerHub images / labs:\n" + "\n\n".join(fmt(results_docker)))

    return "\n\n---------------------\n\n".join(sections)


def a7_ai_companion_quiz(llm, summary: str) -> str:
    """
    A7_AI_Companion: generate quizzes and exercises from the summary.
    """
    prompt = ChatPromptTemplate.from_template(
        """
You are A7_AI_Companion, a friendly quiz generator.

Student summary notes:

---------------- SUMMARY ----------------
{summary}
----------------------------------------

Create:
1) Three multiple choice questions (MCQ) with 4 options (A,B,C,D) each.
2) Two short open questions or exercises.

Format STRICTLY like this (do not add anything else):

[QUIZ]
Q1: ...
A) ...
B) ...
C) ...
D) ...
Correct answer: X

Q2: ...


Q3: ...


[EXERCISES]
E1: ...
E2: ...

Keep questions clear and at beginner level.
"""
    )
    chain = prompt | llm | parser
    try:
        return chain.invoke({"summary": summary})
    except Exception as exc:
        return f"[A7_AI_Companion ERROR] {exc}"


def a8_examiner(subject: str, chapter: str) -> str:
    """
    A8_Examiner: look for real past exams and PDFs.
    """
    query = f"{subject} {chapter} exam pdf filetype:pdf"
    results = search_exams(query, max_results=6)
    if not results:
        return "No past exam PDFs could be found."
    lines: List[str] = []
    for idx, r in enumerate(results, start=1):
        title = r.get("title") or "No title"
        href = r.get("href") or r.get("url") or ""
        lines.append(f"[{idx}] {title}\nPDF link: {href}")
    return "\n\n".join(lines)


def a9_guide(
    llm,
    summary: str,
    self_score: Optional[int] = None,
    total_questions: int = 3,
) -> str:
    """
    A9_Guide: generate a study roadmap based on performance and summary.
    """
    if self_score is None or self_score < 0:
        performance_text = (
            "The student did not provide a quiz score. Assume average understanding."
        )
    else:
        performance_text = (
            f"The student reported {self_score} correct answers out of {total_questions} questions."
        )

    prompt = ChatPromptTemplate.from_template(
        """
You are A9_Guide, an academic coach.

Student performance info:
{performance_text}

Summary of the chapter:

---------------- SUMMARY ----------------
{summary}
----------------------------------------

Create a step-by-step roadmap for mastering this chapter:
- Start with a short diagnosis of the student's level (beginner, ok, or strong).
- Then give a 5 to 7 step roadmap.
- Include time suggestions (for example "30 minutes" or "1 hour") for each step.
- Mention when to re-take quizzes or search for more exercises.
- End with 3 motivational tips.

Use simple, encouraging language.
"""
    )
    chain = prompt | llm | parser
    try:
        return chain.invoke({"performance_text": performance_text, "summary": summary})
    except Exception as exc:
        return f"[A9_Guide ERROR] {exc}"
