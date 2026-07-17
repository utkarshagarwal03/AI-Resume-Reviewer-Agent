import re
import logging
from PyPDF2 import PdfReader
import io

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts and cleans text from a PDF file object.
    
    Args:
        pdf_file: A file-like object representing the PDF (e.g., BytesIO or UploadedFile).
        
    Returns:
        str: The extracted and cleaned text from the PDF.
    """
    text = ""
    try:
        reader = PdfReader(pdf_file)
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        # Clean formatting
        text = clean_extracted_text(text)
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise e

def clean_extracted_text(text: str) -> str:
    """
    Cleans raw extracted PDF text by removing double spaces, 
    excessive newlines, and standardizing whitespaces.
    """
    if not text:
        return ""
        
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Replace three or more newlines with a double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Strip leading/trailing whitespaces
    return text.strip()
