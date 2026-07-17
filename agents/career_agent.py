import logging
from typing import Dict, Any, Optional
from agents import AgentState, get_llm, clean_and_parse_json
from prompts.career_prompt import CAREER_ADVISOR_PROMPT

logger = logging.getLogger(__name__)

def career_agent(state: AgentState, config: Optional[Dict[str, Any]] = None) -> AgentState:
    """
    Analyzes the resume to suggest professional certifications, missing technologies, 
    and a personalized career development roadmap.
    """
    logger.info("Starting Career Advisor Agent...")
    
    if state.get("error"):
        logger.warning("Skipping Career Agent due to existing state error.")
        return state
        
    resume_text = state.get("resume_text")
    if not resume_text:
        logger.error("No resume text found in state.")
        return {**state, "error": "Career Agent: No resume text found."}
        
    try:
        api_key = None
        if config and "configurable" in config:
            api_key = config["configurable"].get("api_key")
            
        llm = get_llm(api_key=api_key)
        
        prompt = CAREER_ADVISOR_PROMPT.format(resume_text=resume_text)
        response = llm.invoke(prompt)
        
        result = clean_and_parse_json(response.content)
        
        return {
            **state,
            "certifications": list(result.get("certifications", [])),
            "missing_technologies": list(result.get("missing_technologies", [])),
            "learning_roadmap": list(result.get("learning_roadmap", [])),
            "error": None
        }
    except Exception as e:
        logger.exception("Error in Career Advisor Agent")
        return {
            **state,
            "error": f"Career Agent failed: {str(e)}"
        }
