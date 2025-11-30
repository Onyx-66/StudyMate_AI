from __future__ import annotations

from typing import Dict, List

from io import BytesIO

from ddgs import DDGS
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file_obj) -> str:
    """
    Extract text from a PDF file-like object.
    """
    try:
        reader = PdfReader(file_obj)
        pages_text: List[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
        return "\n\n".join(pages_text)
    except Exception as exc:
        raise RuntimeError(f"Error while reading PDF: {exc}") from exc


def extract_text_from_docx(file_obj) -> str:
    """
    Extract text from a DOCX file-like object.
    """
    try:
        if hasattr(file_obj, "read"):
            data = file_obj.read()
        else:
            data = file_obj
        doc = Document(BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs)
    except Exception as exc:
        raise RuntimeError(f"Error while reading DOCX: {exc}") from exc


def extract_text_from_file(uploaded_file) -> str:
    """
    Detect file type (by extension) and extract text.
    Supports PDF, DOCX, and plain TXT.
    """
    if uploaded_file is None:
        raise ValueError("No file uploaded.")

    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    if filename.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)
    if filename.endswith(".txt"):
        try:
            content = uploaded_file.read()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="ignore")
            return str(content)
        except Exception as exc:
            raise RuntimeError(f"Error while reading TXT file: {exc}") from exc

    raise ValueError("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")


def _ddg_text(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Helper wrapper around DDGS().text for general web search.
    """
    try:
        with DDGS() as ddgs:
            # ddgs.text returns an iterator of dicts: {"title","href","body",...}
            results_iter = ddgs.text(query, max_results=max_results)
            results = list(results_iter)
        return results
    except Exception as exc:
        return [
            {
                "title": "Search error",
                "href": "",
                "body": f"DDGS search failed: {exc}",
            }
        ]


def search_text(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    General-purpose text search.
    """
    return _ddg_text(query, max_results=max_results)


def search_videos(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search for video tutorials.
    """
    return _ddg_text(query, max_results=max_results)


def search_projects(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search for GitHub / DockerHub projects.
    """
    return _ddg_text(query, max_results=max_results)


def search_exams(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search for past exam PDFs.
    """
    return _ddg_text(query, max_results=max_results)
