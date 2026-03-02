import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from src.infrastructure.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    documents = relationship("Document", back_populates="uploader")
    chat_threads = relationship("ChatThread", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    filename = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="uploaded")
    metadata_ = Column("metadata", JSONB, nullable=True) # Reserved keyword workaround
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    uploader = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document")
    feedbacks = relationship("ExtractionFeedback", back_populates="document")

class ExtractionFeedback(Base):
    __tablename__ = "extraction_feedbacks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    selected_method = Column(String(100), nullable=False)
    task_context = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    document = relationship("Document", back_populates="feedbacks")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    page_number = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    chunk_type = Column(String(50), nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)
    embedding = Column(Vector(768)) # Default Ollama Nomic or standard vector
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    document = relationship("Document", back_populates="chunks")

class ChatThread(Base):
    __tablename__ = "chat_threads"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True)
    title = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    owner = relationship("User", back_populates="chat_threads")
    messages = relationship("ChatMessage", back_populates="thread")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id"))
    role = Column(String(50), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    sources = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    thread = relationship("ChatThread", back_populates="messages")

class ErrorLog(Base):
    __tablename__ = "error_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("chat_threads.id"), nullable=True)
    error_level = Column(String(20), nullable=False) # ERROR, CRITICAL, WARNING
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    context = Column(JSONB, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
