from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class ChatMessageRequest(BaseModel):
    user_id: str # 本来はTokenから取得するが簡略化
    thread_id: str
    question: str
    document_id: Optional[str] = None
    model_name: Optional[str] = None
    # image_bytes: マルチパートリダクション等で対応する場合は別経路

class SearchResultSchema(BaseModel):
    content: str
    metadata: Dict[str, Any]
    distance: float

class ChatMessageResponse(BaseModel):
    answer: str
    model_used: str
    sources: List[SearchResultSchema] # XAI (Explainable AI)

class ThreadCreateRequest(BaseModel):
    user_id: str
    title: str = "New Chat"
    document_id: Optional[str] = None

class ThreadCreateResponse(BaseModel):
    thread_id: UUID

class MessageHistorySchema(BaseModel):
    role: str
    content: str
    sources: Optional[Dict[str, Any]] = None
