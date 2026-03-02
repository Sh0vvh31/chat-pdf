from typing import List, Optional
import base64
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from src.application.ports.llm_port import LLMPort, LLMResponse
from src.config import settings

class OllamaAdapter(LLMPort):
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL):
        self.base_url = base_url

    def _convert_messages(self, messages: List[dict], image_bytes: Optional[List[bytes]]) -> List[BaseMessage]:
        langchain_msgs = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_msgs.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_msgs.append(AIMessage(content=content))
            elif role == "user":
                if image_bytes and len(image_bytes) > 0:
                    # マルチモーダル時の画像付与
                    content_list = [{"type": "text", "text": content}]
                    for img in image_bytes:
                        b64_img = base64.b64encode(img).decode("utf-8")
                        content_list.append({
                            "type": "image_url",
                            "image_url": f"data:image/jpeg;base64,{b64_img}"
                        })
                    langchain_msgs.append(HumanMessage(content=content_list))
                else:
                    langchain_msgs.append(HumanMessage(content=content))
                    
        return langchain_msgs

    def generate_chat_response(
        self, 
        messages: List[dict], 
        model_name: str, 
        image_bytes: Optional[List[bytes]] = None
    ) -> LLMResponse:
        
        # モデルごとのChatOllama初期化
        chat_model = ChatOllama(
            base_url=self.base_url,
            model=model_name,
            temperature=0.0
        )
        
        langchain_msgs = self._convert_messages(messages, image_bytes)
        
        # API呼び出し
        response = chat_model.invoke(langchain_msgs)
        
        return LLMResponse(
            content=str(response.content),
            used_model=model_name
        )
