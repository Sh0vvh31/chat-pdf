from typing import Protocol, List, Optional, Dict, Any
from uuid import UUID

class SearchResult:
    def __init__(self, chunk_id: UUID, document_id: UUID, content: str, distance: float, metadata: Dict[str, Any] = None):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.distance = distance
        self.metadata = metadata or {}

class DocumentRepositoryPort(Protocol):
    def save_document(self, user_id: UUID, filename: str) -> UUID:
        """PDF等のファイル情報をDBに保存し、IDを返す"""
        ...
        
    def save_chunks(self, document_id: UUID, contents: List[str], chunk_types: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]] = None) -> None:
        """ベクトル化されたチャンク群を一括で保存する"""
        ...
        
    def search_similar_chunks(self, query_embedding: List[float], limit: int = 5, document_filter_id: Optional[UUID] = None) -> List[SearchResult]:
        """pgvectorを利用し、コサイン類似度で近似最近傍探索を行う"""
        ...
