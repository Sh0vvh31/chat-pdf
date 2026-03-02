import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.application.use_cases.chat_use_case import ChatUseCase

def test_chat_use_case_handle_message():
    # Arrange Ports
    mock_doc_repo = MagicMock()
    mock_embedding_port = MagicMock()
    mock_llm_port = MagicMock()
    mock_chat_history_repo = MagicMock()
    
    # Fake history from DB
    mock_msg1 = MagicMock()
    mock_msg1.role = "user"
    mock_msg1.content = "previous question"
    mock_chat_history_repo.get_thread_messages.return_value = [mock_msg1]
    
    # Dependency returns for workflow
    mock_embedding_port.embed_text.return_value = [0.1, 0.2]
    mock_search_result = MagicMock()
    mock_search_result.content = "PDF Chunk Content"
    mock_search_result.metadata = {}
    mock_search_result.distance = 0.5
    mock_doc_repo.search_similar_chunks.return_value = [mock_search_result]
    
    mock_llm_response = MagicMock()
    mock_llm_response.content = "Answer based on chunk"
    mock_llm_response.used_model = "gemma:2b"
    mock_llm_port.generate_chat_response.return_value = mock_llm_response
    
    # Use Case setup
    use_case = ChatUseCase(
        document_repo=mock_doc_repo,
        embedding_port=mock_embedding_port,
        llm_port=mock_llm_port,
        chat_history_repo=mock_chat_history_repo
    )
    
    user_id = uuid4()
    thread_id = uuid4()
    
    # Act
    result = use_case.handle_chat_message(
        user_id=user_id,
        thread_id=thread_id,
        question="What?"
    )
    
    # Assert
    assert result["answer"] == "Answer based on chunk"
    assert result["model_used"] == "gemma:2b"
    assert len(result["sources"]) == 1
    
    # DB calls check
    assert mock_chat_history_repo.get_thread_messages.called
    assert mock_chat_history_repo.save_message.call_count == 2
    
    # ユーザー側の保存
    user_call_kwargs = mock_chat_history_repo.save_message.call_args_list[0][1]
    assert user_call_kwargs["role"] == "user"
    assert user_call_kwargs["content"] == "What?"
    assert user_call_kwargs["sources"] is None
    
    # AI側の保存 (XAI)
    assistant_call_kwargs = mock_chat_history_repo.save_message.call_args_list[1][1]
    assert assistant_call_kwargs["role"] == "assistant"
    assert assistant_call_kwargs["content"] == "Answer based on chunk"
    assert "retrieved_chunks" in assistant_call_kwargs["sources"]
    assert assistant_call_kwargs["sources"]["model_used"] == "gemma:2b"
