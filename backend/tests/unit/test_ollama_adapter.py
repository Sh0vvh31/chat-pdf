import pytest
from unittest.mock import patch, MagicMock
from src.infrastructure.llm.ollama_adapter import OllamaAdapter
from src.application.ports.llm_port import LLMResponse
import base64

def test_ollama_adapter_text_generate():
    adapter = OllamaAdapter(base_url="http://dummy:11434")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"}
    ]
    
    with patch("src.infrastructure.llm.ollama_adapter.ChatOllama") as mock_chat_ollama:
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.content = "Hi there!"
        mock_instance.invoke.return_value = mock_response
        
        response = adapter.generate_chat_response(
            messages=messages,
            model_name="gemma:2b"
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Hi there!"
        assert response.used_model == "gemma:2b"
        
        # Verify the invoke was called with correct LangChain message objects
        called_args = mock_instance.invoke.call_args[0][0]
        assert len(called_args) == 2
        assert called_args[0].content == "You are a helpful assistant."
        assert called_args[1].content == "Hello"

def test_ollama_adapter_multimodal_generate():
    adapter = OllamaAdapter()
    
    messages = [{"role": "user", "content": "What is in this image?"}]
    dummy_image_1 = b"dummy_image_data_1"
    
    with patch("src.infrastructure.llm.ollama_adapter.ChatOllama") as mock_chat_ollama:
        mock_instance = MagicMock()
        mock_chat_ollama.return_value = mock_instance
        
        mock_response = MagicMock()
        mock_response.content = "It is a picture of a cat."
        mock_instance.invoke.return_value = mock_response
        
        response = adapter.generate_chat_response(
            messages=messages,
            model_name="minicpm-v",
            image_bytes=[dummy_image_1]
        )
        
        assert response.content == "It is a picture of a cat."
        
        called_args = mock_instance.invoke.call_args[0][0]
        user_message_content = called_args[0].content
        
        assert isinstance(user_message_content, list)
        assert user_message_content[0]["type"] == "text"
        assert user_message_content[0]["text"] == "What is in this image?"
        assert user_message_content[1]["type"] == "image_url"
        
        expected_b64 = base64.b64encode(dummy_image_1).decode("utf-8")
        assert expected_b64 in user_message_content[1]["image_url"]
