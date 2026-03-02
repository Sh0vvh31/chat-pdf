import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.infrastructure.db.repositories.document_repository import PgDocumentRepository, SearchResult
from src.infrastructure.db.models import Document as DBDocument

def test_save_document():
    mock_db = MagicMock()
    
    def side_effect_refresh(obj):
        obj.id = uuid4()
    mock_db.refresh.side_effect = side_effect_refresh
    
    repo = PgDocumentRepository(db=mock_db)
    user_id = uuid4()
    
    new_doc_id = repo.save_document(user_id=user_id, filename="test.pdf")
    
    assert mock_db.add.called
    assert mock_db.commit.called
    assert new_doc_id is not None

def test_save_chunks():
    mock_db = MagicMock()
    repo = PgDocumentRepository(db=mock_db)
    doc_id = uuid4()
    
    contents = ["chunk 1", "chunk 2"]
    chunk_types = ["text", "text"]
    embeddings = [[0.1, 0.2], [0.3, 0.4]]
    
    # 疑似的にドキュメントを取得できるようにする
    mock_doc = MagicMock()
    mock_db.query().filter().first.return_value = mock_doc
    
    repo.save_chunks(doc_id, contents, chunk_types, embeddings, [{"page_number": 1}, {"page_number": 2}])
    
    assert mock_db.add_all.called
    assert mock_db.commit.called
    assert mock_doc.status == "processed"

def test_search_similar_chunks():
    mock_db = MagicMock()
    repo = PgDocumentRepository(db=mock_db)
    
    # query chain mock
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    
    # limit -> all return two fake objects
    mock_chunk = MagicMock()
    mock_chunk.id = uuid4()
    mock_chunk.document_id = uuid4()
    mock_chunk.content = "found content"
    mock_chunk.metadata_ = {}
    
    # SQLAlchemy query returns tuple (ChunkObject, distance)
    mock_query.order_by().limit().all.return_value = [(mock_chunk, 0.15)]
    
    results = repo.search_similar_chunks([0.1, 0.2], limit=1)
    
    assert len(results) == 1
    assert results[0].content == "found content"
    assert results[0].distance == 0.15
    assert isinstance(results[0], SearchResult)
