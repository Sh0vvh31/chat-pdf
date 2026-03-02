import pytest
from unittest.mock import MagicMock
from src.application.workflows.rag_graph import RAGWorkflow, RAGState
from src.application.ports.document_repository import SearchResult
from src.application.ports.llm_port import LLMResponse

def test_rag_workflow_execution():
    # Arrange Ports
    mock_doc_repo = MagicMock()
    mock_embedding_port = MagicMock()
    mock_llm_port = MagicMock()
    
    # Setup Returns
    mock_embedding_port.embed_text.return_value = [0.1, 0.2]
    
    mock_search_result = SearchResult(
        chunk_id="chunk_id",
        document_id="doc_id",
        content="This is relevant content from pdf.",
        distance=0.1
    )
    mock_doc_repo.search_similar_chunks.return_value = [mock_search_result]
    
    mock_llm_response = LLMResponse(content="Yes, the pdf says this.", used_model="gemma:2b")
    mock_llm_port.generate_chat_response.return_value = mock_llm_response
    
    # Initialize Workflow
    workflow = RAGWorkflow(
        document_repo=mock_doc_repo,
        embedding_port=mock_embedding_port,
        llm_port=mock_llm_port
    )
    
    initial_state: RAGState = {
        "user_id": "user123",
        "document_id": "00000000-0000-0000-0000-000000000000",
        "question": "What does the pdf say?",
        "chat_history": [],
        "retrieved_chunks": [],
        "final_answer": "",
        "used_model": "",
        "image_bytes": None
    }
    
    # Act
    final_state = workflow.invoke(initial_state)
    
    # Assert
    assert mock_embedding_port.embed_text.called
    assert mock_doc_repo.search_similar_chunks.called
    assert mock_llm_port.generate_chat_response.called
    
    assert final_state["final_answer"] == "Yes, the pdf says this."
    assert final_state["used_model"] == "gemma:2b"
    assert len(final_state["retrieved_chunks"]) == 1
    assert final_state["retrieved_chunks"][0]["content"] == "This is relevant content from pdf."
