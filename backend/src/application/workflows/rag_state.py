from typing import TypedDict, List, Dict, Any, Optional
from uuid import UUID

class MessageState(TypedDict):
    role: str
    content: str
    
class RAGState(TypedDict):
    user_id: str
    document_id: Optional[str]
    question: str
    chat_history: List[MessageState]
    retrieved_chunks: List[Dict[str, Any]]
    final_answer: str
    used_model: str
    requested_model: Optional[str]
    image_bytes: Optional[List[bytes]]
