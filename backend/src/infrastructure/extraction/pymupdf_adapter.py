import fitz  # PyMuPDF
from typing import List
from src.application.ports.extractor_port import ExtractorPort, ExtractedChunk
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PyMuPDFExtractor(ExtractorPort):
    def __init__(self):
        # チャンクサイズを適度に小さく設計（Ollama embed制限対策）
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def extract(self, file_path: str) -> List[ExtractedChunk]:
        chunks = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text").strip()
                
                if text:
                    # ページテキストをLangChainのSplitterで分割
                    split_texts = self.text_splitter.split_text(text)
                    for split_text in split_texts:
                        chunk = ExtractedChunk(
                            page_number=page_num + 1,
                            content=split_text,
                            chunk_type="text",
                            metadata={"source": "pymupdf"}
                        )
                        chunks.append(chunk)
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from {file_path}: {str(e)}")
            
        return chunks
