from typing import TypedDict, List, Dict, Any, Optional
import os
import logging
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    pdf_bytes: Optional[bytes]
    resume_text: str
    ats_score: int
    extracted_skills: List[str]
    missing_skills: List[str]
    weak_sections: List[str]
    strengths: List[str]
    weaknesses: List[str]
    improved_bullets: List[Dict[str, str]]
    formatting_suggestions: List[str]
    project_suggestions: List[str]
    hr_questions: List[str]
    technical_questions: List[str]
    java_questions: List[str]
    dsa_questions: List[str]
    sql_questions: List[str]
    project_questions: List[str]
    learning_roadmap: List[str]
    certifications: List[str]
    missing_technologies: List[str]
    summary: str
    report_markdown: str
    error: Optional[str]

def get_llm(api_key: Optional[str] = None) -> Any:
    """
    Initializes the Google Gemini 3.5 Flash model with a fallback to 1.5 Flash
    using the provided API key or falling back to the GOOGLE_API_KEY environment variable.
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google Gemini API Key is missing. Please set it in the environment or sidebar.")
    
    # Primary model: Gemini 3.5 Flash
    llm_primary = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        google_api_key=key,
        temperature=0.2
    )
    
    # Fallback model: Gemini 1.5 Flash
    llm_fallback = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=key,
        temperature=0.2
    )
    
    return llm_primary.with_fallbacks([llm_fallback])

import json
import re

def clean_and_parse_json(text: str) -> dict:
    """
    Cleans markdown code fences and parses JSON string.
    """
    # Remove markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\n", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\n```$", "", cleaned, flags=re.MULTILINE)
    return json.loads(cleaned)

