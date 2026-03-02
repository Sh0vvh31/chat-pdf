from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from src.application.ports.document_repository import DocumentRepositoryPort, SearchResult
from src.infrastructure.db.models import Document as DBDocument, DocumentChunk

class PgDocumentRepository(DocumentRepositoryPort):
    def __init__(self, db: Session):
        self.db = db

    def save_document(self, user_id: UUID, filename: str) -> UUID:
        new_doc = DBDocument(user_id=user_id, filename=filename, status="processing")
        self.db.add(new_doc)
        self.db.commit()
        self.db.refresh(new_doc)
        return new_doc.id

    def save_chunks(self, document_id: UUID, contents: List[str], chunk_types: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]] = None) -> None:
        if not metadatas:
            metadatas = [{} for _ in contents]
            
        new_chunks = []
        for content, c_type, embedding, metadata in zip(contents, chunk_types, embeddings, metadatas):
            page_num = metadata.get("page_number", None)
            new_chunk = DocumentChunk(
                document_id=document_id,
                content=content,
                chunk_type=c_type,
                embedding=embedding,
                metadata_=metadata,
                page_number=page_num
            )
            new_chunks.append(new_chunk)
            
        self.db.add_all(new_chunks)
        # ドキュメントのステータスを更新
        doc = self.db.query(DBDocument).filter(DBDocument.id == document_id).first()
        if doc:
            doc.status = "processed"
        self.db.commit()

    def search_similar_chunks(self, query_embedding: List[float], limit: int = 5, document_filter_id: Optional[UUID] = None) -> List[SearchResult]:
        query = self.db.query(DocumentChunk, DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"))
        
        if document_filter_id:
            query = query.filter(DocumentChunk.document_id == document_filter_id)
            
        # 距離が近い（類似度が高い）順に取得
        results = query.order_by("distance").limit(limit).all()
        
        search_results = []
        for chunk, distance in results:
            search_results.append(SearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                content=chunk.content,
                distance=float(distance), # dbの出力はfloatとは限らないためキャスト
                metadata=chunk.metadata_
            ))
            
        return search_results
