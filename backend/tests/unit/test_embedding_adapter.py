import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.llm.embedding_adapter import OllamaEmbeddingAdapter

def test_embed_text():
    with patch("src.infrastructure.llm.embedding_adapter.OllamaEmbeddings") as mock_ollama_embeddings:
        mock_instance = MagicMock()
        mock_ollama_embeddings.return_value = mock_instance
        
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        
        adapter = OllamaEmbeddingAdapter(base_url="http://dummy:11434")
        result = adapter.embed_text("hello world")
        
        assert len(result) == 3
        assert result == [0.1, 0.2, 0.3]
        mock_instance.embed_query.assert_called_once_with("hello world")

def test_embed_documents():
    with patch("src.infrastructure.llm.embedding_adapter.OllamaEmbeddings") as mock_ollama_embeddings:
        mock_instance = MagicMock()
        mock_ollama_embeddings.return_value = mock_instance
        
        mock_instance.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        adapter = OllamaEmbeddingAdapter()
        result = adapter.embed_documents(["hello", "world"])
        
        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]
        mock_instance.embed_documents.assert_called_once_with(["hello", "world"])
