import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.application.use_cases.document_extraction_use_case import DocumentExtractionUseCase
from src.application.ports.extractor_port import ExtractedChunk

def test_document_extraction_success():
    mock_doc_repo = MagicMock()
    mock_embedding_port = MagicMock()
    mock_extractor = MagicMock()
    
    # 疑似戻り値セットアップ
    test_doc_id = uuid4()
    mock_doc_repo.save_document.return_value = test_doc_id
    
    mock_chunk1 = ExtractedChunk(page_number=1, content="Page 1 Text", chunk_type="text")
    mock_chunk2 = ExtractedChunk(page_number=2, content="Page 2 Text", chunk_type="text")
    mock_extractor.extract.return_value = [mock_chunk1, mock_chunk2]
    
    mock_embedding_port.embed_documents.return_value = [[0.1, 0.1], [0.2, 0.2]]
    
    use_case = DocumentExtractionUseCase(
        document_repo=mock_doc_repo,
        embedding_port=mock_embedding_port,
        extractors={"pymupdf": mock_extractor}
    )
    
    user_id = uuid4()
    result_doc_id = use_case.process_document(user_id=user_id, file_path="dummy.pdf", filename="test.pdf")
    
    assert result_doc_id == test_doc_id
    
    mock_doc_repo.save_document.assert_called_once_with(user_id, "test.pdf")
    mock_extractor.extract.assert_called_once_with("dummy.pdf")
    mock_embedding_port.embed_documents.assert_called_once_with(["Page 1 Text", "Page 2 Text"])
    
    # 最終的な保存処理が呼ばれているか
    assert mock_doc_repo.save_chunks.called
    called_args = mock_doc_repo.save_chunks.call_args[1]
    assert called_args["document_id"] == test_doc_id
    assert called_args["contents"] == ["Page 1 Text", "Page 2 Text"]
    assert called_args["embeddings"] == [[0.1, 0.1], [0.2, 0.2]]
