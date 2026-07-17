import logging
from typing import Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embeddings
from agents import get_llm

try:
    from langchain_classic.chains import ConversationalRetrievalChain
except ImportError:
    from langchain.chains import ConversationalRetrievalChain

try:
    from langchain_classic.memory import ConversationBufferMemory
except ImportError:
    from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

def build_vector_store(text: str, api_key: Optional[str] = None) -> FAISS:
    """
    Splits the resume text into chunks, generates embeddings, and indexes them in a local FAISS store.
    """
    logger.info("Splitting resume text into chunks...")
    # Clean text first
    text = text.strip()
    
    # Simple chunking for short resumes
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    logger.info(f"Generated {len(chunks)} text chunks.")
    
    embeddings = get_embeddings(api_key=api_key)
    logger.info("Creating FAISS index...")
    vector_store = FAISS.from_texts(chunks, embeddings)
    logger.info("FAISS vector store successfully initialized.")
    return vector_store

def create_chat_chain(vector_store: FAISS, api_key: Optional[str] = None) -> ConversationalRetrievalChain:
    """
    Creates a conversational retrieval chain with memory for answering questions about the resume.
    """
    llm = get_llm(api_key=api_key)
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    
    # Store history for conversational capability
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    logger.info("Creating ConversationalRetrievalChain...")
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=True
    )
    return chain
