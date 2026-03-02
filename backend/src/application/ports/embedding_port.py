from typing import Protocol, List

class EmbeddingPort(Protocol):
    def embed_text(self, text: str) -> List[float]:
        """テキストを単一のベクトルに変換して返す"""
        ...
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数テキストをベクトルのリストに変換して返す"""
        ...
