import logging
from typing import Dict, Any, Optional
from agents import AgentState, get_llm, clean_and_parse_json
from prompts.interview_prompt import INTERVIEW_QUESTIONS_PROMPT

logger = logging.getLogger(__name__)

def interview_agent(state: AgentState, config: Optional[Dict[str, Any]] = None) -> AgentState:
    """
    Analyzes the resume and generates tailored HR, Java, DSA, SQL, and project-specific questions.
    """
    logger.info("Starting Interview Agent...")
    
    if state.get("error"):
        logger.warning("Skipping Interview Agent due to existing state error.")
        return state
        
    resume_text = state.get("resume_text")
    if not resume_text:
        logger.error("No resume text found in state.")
        return {**state, "error": "Interview Agent: No resume text found."}
        
    try:
        api_key = None
        if config and "configurable" in config:
            api_key = config["configurable"].get("api_key")
            
        llm = get_llm(api_key=api_key)
        
        prompt = INTERVIEW_QUESTIONS_PROMPT.format(resume_text=resume_text)
        response = llm.invoke(prompt)
        
        result = clean_and_parse_json(response.content)
        
        # We can also populate a general technical_questions list for ease of access
        technical_questions = []
        technical_questions.extend(result.get("java_questions", []))
        technical_questions.extend(result.get("dsa_questions", []))
        technical_questions.extend(result.get("sql_questions", []))
        
        return {
            **state,
            "hr_questions": list(result.get("hr_questions", [])),
            "java_questions": list(result.get("java_questions", [])),
            "dsa_questions": list(result.get("dsa_questions", [])),
            "sql_questions": list(result.get("sql_questions", [])),
            "project_questions": list(result.get("project_questions", [])),
            "technical_questions": technical_questions,
            "error": None
        }
    except Exception as e:
        logger.exception("Error in Interview Agent")
        return {
            **state,
            "error": f"Interview Agent failed: {str(e)}"
        }
