import os
import logging
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger = logging.getLogger(__name__)

def get_embeddings(api_key: str = None) -> GoogleGenerativeAIEmbeddings:
    """
    Returns an instance of GoogleGenerativeAIEmbeddings.
    """
    key = api_key or os.getenv("GOOGLE_API_KEY")
    if not key:
        raise ValueError("Google Gemini API Key is missing for embeddings generation.")
        
    logger.info("Initializing Google Generative AI Embeddings...")
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=key
    )
