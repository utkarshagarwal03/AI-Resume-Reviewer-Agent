import logging
from typing import Dict, Any, Optional
from agents import AgentState, get_llm, clean_and_parse_json
from prompts.ats_prompt import ATS_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

def ats_agent(state: AgentState, config: Optional[Dict[str, Any]] = None) -> AgentState:
    """
    Analyzes the resume text for ATS score, strengths, weaknesses, extracted skills, 
    missing skills, and general profile summary.
    """
    logger.info("Starting ATS Analysis Agent...")
    resume_text = state.get("resume_text")
    
    if not resume_text:
        logger.error("No resume text found in state.")
        return {**state, "error": "ATS Agent: No resume text found in state."}
        
    try:
        # Extract API key if passed through config
        api_key = None
        if config and "configurable" in config:
            api_key = config["configurable"].get("api_key")
            
        llm = get_llm(api_key=api_key)
        
        # Build prompt and invoke LLM
        prompt = ATS_ANALYSIS_PROMPT.format(resume_text=resume_text)
        response = llm.invoke(prompt)
        
        # Parse the JSON response
        result = clean_and_parse_json(response.content)
        
        # Update the state keys
        return {
            **state,
            "ats_score": int(result.get("ats_score", 0)),
            "extracted_skills": list(result.get("extracted_skills", [])),
            "missing_skills": list(result.get("missing_skills", [])),
            "weak_sections": list(result.get("weak_sections", [])),
            "strengths": list(result.get("strengths", [])),
            "weaknesses": list(result.get("weaknesses", [])),
            "summary": str(result.get("summary", "")),
            "error": None
        }
    except Exception as e:
        logger.exception("Error in ATS Agent")
        return {
            **state,
            "error": f"ATS Agent failed: {str(e)}"
        }
