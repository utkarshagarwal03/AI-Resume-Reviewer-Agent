import io
import logging
from agents import AgentState
from utils.pdf_reader import extract_text_from_pdf

logger = logging.getLogger(__name__)

def parser_agent(state: AgentState) -> AgentState:
    """
    Reads the PDF bytes from the state, extracts the text, cleans the formatting,
    and updates the state with the cleaned text.
    """
    logger.info("Starting Parser Agent...")
    pdf_bytes = state.get("pdf_bytes")
    
    if not pdf_bytes:
        logger.error("No PDF bytes found in state.")
        return {**state, "error": "Parser Agent: No PDF bytes found in state."}
        
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        resume_text = extract_text_from_pdf(pdf_file)
        
        if not resume_text:
            raise ValueError("Extracted text is empty. PDF might be scanned or corrupted.")
            
        logger.info("Resume text successfully parsed and cleaned.")
        return {
            **state,
            "resume_text": resume_text,
            "error": None  # clear any previous error
        }
    except Exception as e:
        logger.exception("Error in Parser Agent")
        return {
            **state,
            "error": f"Parser Agent failed: {str(e)}"
        }
