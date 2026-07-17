import logging
from typing import Dict, Any, Optional
from agents import AgentState, get_llm, clean_and_parse_json
from prompts.improve_prompt import RESUME_IMPROVEMENT_PROMPT

logger = logging.getLogger(__name__)

def improve_agent(state: AgentState, config: Optional[Dict[str, Any]] = None) -> AgentState:
    """
    Analyzes the resume text to rewrite weak bullet points using action verbs and metrics,
    and suggest layout/formatting improvements and relevant projects.
    """
    logger.info("Starting Resume Improvement Agent...")
    
    # Check for previous agent errors
    if state.get("error"):
        logger.warning("Skipping Improve Agent due to existing state error.")
        return state
        
    resume_text = state.get("resume_text")
    if not resume_text:
        logger.error("No resume text found in state.")
        return {**state, "error": "Improve Agent: No resume text found."}
        
    try:
        api_key = None
        if config and "configurable" in config:
            api_key = config["configurable"].get("api_key")
            
        llm = get_llm(api_key=api_key)
        
        prompt = RESUME_IMPROVEMENT_PROMPT.format(resume_text=resume_text)
        response = llm.invoke(prompt)
        
        result = clean_and_parse_json(response.content)
        
        return {
            **state,
            "improved_bullets": list(result.get("improved_bullets", [])),
            "formatting_suggestions": list(result.get("formatting_suggestions", [])),
            "project_suggestions": list(result.get("project_suggestions", [])),
            "error": None
        }
    except Exception as e:
        logger.exception("Error in Resume Improvement Agent")
        return {
            **state,
            "error": f"Improve Agent failed: {str(e)}"
        }
