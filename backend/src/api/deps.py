from fastapi import Depends
from sqlalchemy.orm import Session
from src.infrastructure.db.database import get_db

from src.infrastructure.db.repositories.user_repository import PgUserRepository
from src.infrastructure.db.repositories.document_repository import PgDocumentRepository
from src.infrastructure.db.repositories.chat_history_repository import PgChatHistoryRepository

from src.infrastructure.extraction.pymupdf_adapter import PyMuPDFExtractor
from src.infrastructure.llm.ollama_adapter import OllamaAdapter
from src.infrastructure.llm.embedding_adapter import OllamaEmbeddingAdapter

from src.application.use_cases.document_extraction_use_case import DocumentExtractionUseCase
from src.application.use_cases.chat_use_case import ChatUseCase

def get_document_extraction_use_case(db: Session = Depends(get_db)):
    doc_repo = PgDocumentRepository(db)
    embedding_port = OllamaEmbeddingAdapter()
    extractor = PyMuPDFExtractor()
    
    return DocumentExtractionUseCase(
        document_repo=doc_repo,
        embedding_port=embedding_port,
        extractors={"pymupdf": extractor}
    )

def get_chat_use_case(db: Session = Depends(get_db)):
    doc_repo = PgDocumentRepository(db)
    embedding_port = OllamaEmbeddingAdapter()
    llm_port = OllamaAdapter()
    chat_history_repo = PgChatHistoryRepository(db)
    
    return ChatUseCase(
        document_repo=doc_repo,
        embedding_port=embedding_port,
        llm_port=llm_port,
        chat_history_repo=chat_history_repo
    )

def get_chat_history_repo(db: Session = Depends(get_db)):
    return PgChatHistoryRepository(db)
