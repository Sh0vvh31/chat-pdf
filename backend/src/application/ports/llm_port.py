from typing import Protocol, List, Optional

class LLMResponse:
    def __init__(self, content: str, used_model: str):
        self.content = content
        self.used_model = used_model

class LLMPort(Protocol):
    def generate_chat_response(
        self, 
        messages: List[dict], 
        model_name: str, 
        image_bytes: Optional[List[bytes]] = None
    ) -> LLMResponse:
        """
        messages: [{"role": "user", "content": "hello"}]
        image_bytes: VLM(マルチモーダル)で使用する画像のバイナリリスト
        """
        ...
