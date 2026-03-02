from typing import Protocol, List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class ChatMessageDomainModel:
    def __init__(self, id: UUID, thread_id: UUID, role: str, content: str, sources: Optional[Dict[str, Any]] = None):
        self.id = id
        self.thread_id = thread_id
        self.role = role
        self.content = content
        self.sources = sources or {}

class ChatHistoryRepositoryPort(Protocol):
    def create_thread(self, user_id: UUID, document_id: Optional[UUID] = None, title: str = "New Chat") -> UUID:
        """新しいチャットスレッドを作成し、そのIDを返す"""
        ...
        
    def save_message(self, thread_id: UUID, role: str, content: str, sources: Optional[Dict[str, Any]] = None) -> ChatMessageDomainModel:
        """メッセージを保存する (XAIのためのRAGソース情報などを sources に含める)"""
        ...
        
    def get_thread_messages(self, thread_id: UUID) -> List[ChatMessageDomainModel]:
        """指定したスレッドのメッセージ履歴を古い順に取得する"""
        ...
