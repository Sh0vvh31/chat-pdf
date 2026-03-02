from typing import List
from langchain_community.embeddings import OllamaEmbeddings
from src.application.ports.embedding_port import EmbeddingPort
from src.config import settings

class OllamaEmbeddingAdapter(EmbeddingPort):
    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = settings.OLLAMA_BASE_URL):
        self.embeddings = OllamaEmbeddings(
            base_url=base_url,
            model=model_name
        )

    def embed_text(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)
