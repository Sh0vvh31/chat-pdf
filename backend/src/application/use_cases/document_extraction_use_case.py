from typing import Dict
from uuid import UUID
from src.application.ports.document_repository import DocumentRepositoryPort
from src.application.ports.extractor_port import ExtractorPort
from src.application.ports.embedding_port import EmbeddingPort

class DocumentExtractionUseCase:
    def __init__(
        self,
        document_repo: DocumentRepositoryPort,
        embedding_port: EmbeddingPort,
        extractors: Dict[str, ExtractorPort] # 複数対応の注入
    ):
        self.document_repo = document_repo
        self.embedding_port = embedding_port
        self.extractors = extractors
        
    def _select_extractor(self, user_id: UUID) -> str:
        """
        過去のユーザーフィードバックに基づいて抽出器を選択する想定（ABテスト・学習ロジック）
        現在は、指定されたデフォルト(pymupdf)か、ランダム(あるいは固定)選択とする
        """
        # TODO: UserRepository/FeedbackRepositoryから過去の評価を取得し、メソッドを動的選択する
        # ここではシミュレーションとして、pymupdf が存在すればそれを返す
        if "pymupdf" in self.extractors:
            return "pymupdf"
        elif "unstructured" in self.extractors:
            return "unstructured"
        
        # fallback
        return list(self.extractors.keys())[0]

    def process_document(self, user_id: UUID, file_path: str, filename: str) -> UUID:
        """PDFアップロードから抽出・ベクトル化・保存までを一貫処理する"""
        
        # 1. DBに初期登録
        document_id = self.document_repo.save_document(user_id, filename)
        
        # 2. 抽出器の選択(フィードバックルーティング)
        extractor_name = self._select_extractor(user_id)
        selected_extractor = self.extractors[extractor_name]
        
        # 3. PDF抽出
        extracted_chunks = selected_extractor.extract(file_path)
        
        if not extracted_chunks:
            return document_id # 空ドキュメント
        
        # 4. エンベディングの生成 (テキストバッチ処理を想定)
        texts = [chunk.content for chunk in extracted_chunks]
        embeddings = self.embedding_port.embed_documents(texts)
        
        # 5. DBに保存
        chunk_types = [chunk.chunk_type for chunk in extracted_chunks]
        metadatas = [chunk.metadata for chunk in extracted_chunks]
        
        self.document_repo.save_chunks(
            document_id=document_id,
            contents=texts,
            chunk_types=chunk_types,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return document_id
