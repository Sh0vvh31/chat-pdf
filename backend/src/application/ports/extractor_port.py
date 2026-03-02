from typing import Protocol, List, Dict, Any

class ExtractedChunk:
    def __init__(self, page_number: int, content: str, chunk_type: str = "text", metadata: Dict[str, Any] = None):
        self.page_number = page_number
        self.content = content
        self.chunk_type = chunk_type
        self.metadata = metadata or {}

class ExtractorPort(Protocol):
    def extract(self, file_path: str) -> List[ExtractedChunk]:
        """
        PDFファイルを受け取り、ページごとのテキストや抽出された情報のチャンクリストを返す
        """
        ...
