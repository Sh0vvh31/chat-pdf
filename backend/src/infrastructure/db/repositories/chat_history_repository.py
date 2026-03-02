from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from src.application.ports.chat_history_repository import ChatHistoryRepositoryPort, ChatMessageDomainModel
from src.infrastructure.db.models import ChatThread, ChatMessage

class PgChatHistoryRepository(ChatHistoryRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, db_msg: ChatMessage) -> ChatMessageDomainModel:
        return ChatMessageDomainModel(
            id=db_msg.id,
            thread_id=db_msg.thread_id,
            role=db_msg.role,
            content=db_msg.content,
            sources=db_msg.sources
        )

    def create_thread(self, user_id: UUID, document_id: Optional[UUID] = None, title: str = "New Chat") -> UUID:
        new_thread = ChatThread(user_id=user_id, document_id=document_id, title=title)
        self.db.add(new_thread)
        self.db.commit()
        self.db.refresh(new_thread)
        return new_thread.id

    def save_message(self, thread_id: UUID, role: str, content: str, sources: Optional[Dict[str, Any]] = None) -> ChatMessageDomainModel:
        # XAI目的のため、ソース（検索結果のチャンク情報など）をJSONとして保存可能
        new_msg = ChatMessage(
            thread_id=thread_id,
            role=role,
            content=content,
            sources=sources
        )
        self.db.add(new_msg)
        self.db.commit()
        self.db.refresh(new_msg)
        return self._to_domain(new_msg)

    def get_thread_messages(self, thread_id: UUID) -> List[ChatMessageDomainModel]:
        db_messages = self.db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).order_by(ChatMessage.created_at).all()
        return [self._to_domain(msg) for msg in db_messages]
