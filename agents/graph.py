import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from agents import AgentState
from agents.parser import parser_agent
from agents.ats_agent import ats_agent
from agents.improve_agent import improve_agent
from agents.interview_agent import interview_agent
from agents.career_agent import career_agent
from utils.report_generator import generate_markdown_report

logger = logging.getLogger(__name__)

def report_node(state: AgentState) -> AgentState:
    """
    Final node in the graph that compiles the individual findings into a structured markdown report.
    """
    logger.info("Starting Report Generator Node...")
    if state.get("error"):
        logger.warning("Skipping report generation due to previous errors.")
        return state
        
    try:
        report_markdown = generate_markdown_report(state)
        return {
            **state,
            "report_markdown": report_markdown
        }
    except Exception as e:
        logger.exception("Error in Report Generator Node")
        return {
            **state,
            "error": f"Report Generator failed: {str(e)}"
        }

def create_resume_workflow():
    """
    Builds and compiles the LangGraph state graph.
    """
    # Initialize the graph with the AgentState type
    workflow = StateGraph(AgentState)
    
    # Register all agent nodes
    workflow.add_node("parser", parser_agent)
    workflow.add_node("ats", ats_agent)
    workflow.add_node("improve", improve_agent)
    workflow.add_node("interview", interview_agent)
    workflow.add_node("career", career_agent)
    workflow.add_node("reporter", report_node)
    
    # Establish sequential flow
    workflow.set_entry_point("parser")
    workflow.add_edge("parser", "ats")
    workflow.add_edge("ats", "improve")
    workflow.add_edge("improve", "interview")
    workflow.add_edge("interview", "career")
    workflow.add_edge("career", "reporter")
    workflow.add_edge("reporter", END)
    
    return workflow.compile()

def run_resume_analysis(pdf_bytes: bytes, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Orchestrates the entire resume review workflow.
    
    Args:
        pdf_bytes (bytes): The uploaded PDF file bytes.
        api_key (str): Optional Gemini API Key.
        
    Returns:
        dict: The final AgentState after execution.
    """
    # Define initial state
    initial_state = {
        "pdf_bytes": pdf_bytes,
        "resume_text": "",
        "ats_score": 0,
        "extracted_skills": [],
        "missing_skills": [],
        "weak_sections": [],
        "strengths": [],
        "weaknesses": [],
        "improved_bullets": [],
        "formatting_suggestions": [],
        "project_suggestions": [],
        "hr_questions": [],
        "technical_questions": [],
        "java_questions": [],
        "dsa_questions": [],
        "sql_questions": [],
        "project_questions": [],
        "learning_roadmap": [],
        "certifications": [],
        "missing_technologies": [],
        "summary": "",
        "report_markdown": "",
        "error": None
    }
    
    app_graph = create_resume_workflow()
    
    # Pass API key config to nodes
    config = {"configurable": {"api_key": api_key}}
    
    logger.info("Executing LangGraph Resume Review Pipeline...")
    final_state = app_graph.invoke(initial_state, config=config)
    return final_state
