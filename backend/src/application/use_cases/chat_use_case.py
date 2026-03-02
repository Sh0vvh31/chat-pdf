from typing import List, Optional
from uuid import UUID
from src.application.ports.document_repository import DocumentRepositoryPort
from src.application.ports.embedding_port import EmbeddingPort
from src.application.ports.llm_port import LLMPort
from src.application.ports.chat_history_repository import ChatHistoryRepositoryPort
from src.application.workflows.rag_graph import RAGWorkflow

class ChatUseCase:
    def __init__(
        self,
        document_repo: DocumentRepositoryPort,
        embedding_port: EmbeddingPort,
        llm_port: LLMPort,
        chat_history_repo: ChatHistoryRepositoryPort
    ):
        self.chat_history_repo = chat_history_repo
        self.workflow = RAGWorkflow(
            document_repo=document_repo,
            embedding_port=embedding_port,
            llm_port=llm_port
        )
        
    def handle_chat_message(
        self, 
        user_id: UUID,
        thread_id: UUID,
        question: str, 
        document_id: Optional[UUID] = None,
        model_name: Optional[str] = None,
        image_bytes: Optional[List[bytes]] = None
    ) -> dict:
        """
        ユーザーの質問を受け取り、履歴をDBから取得してRAGで回答を生成、
        その後ユーザーの質問とAIの回答（XAI用のソース情報付き）をDBに保存する。
        """
        
        # 1. 過去のメッセージ履歴をDBから取得
        history_msgs = self.chat_history_repo.get_thread_messages(thread_id)
        chat_history = [{"role": m.role, "content": m.content} for m in history_msgs]
        
        # 2. ユーザーの質問をDBに保存
        self.chat_history_repo.save_message(
            thread_id=thread_id,
            role="user",
            content=question,
            sources=None # user doesn't have RAG sources
        )
        
        # 3. RAGワークフローの実行状態を設定
        initial_state = {
            "user_id": str(user_id),
            "document_id": str(document_id) if document_id else None,
            "question": question,
            "chat_history": chat_history,
            "retrieved_chunks": [],
            "final_answer": "",
            "used_model": "",
            "requested_model": model_name,
            "image_bytes": image_bytes
        }
        
        # 4. 実行
        final_state = self.workflow.invoke(initial_state)
        
        # 5. 回答とソース（XAI用データ）を保存
        # sourcesに格納することで「なぜその回答をしたか」の説明根拠(XAI)となる
        xai_sources = {
            "retrieved_chunks": final_state["retrieved_chunks"],
            "model_used": final_state["used_model"]
        }
        
        self.chat_history_repo.save_message(
            thread_id=thread_id,
            role="assistant",
            content=final_state["final_answer"],
            sources=xai_sources
        )
        
        return {
            "answer": final_state["final_answer"],
            "model_used": final_state["used_model"],
            "sources": final_state["retrieved_chunks"]
        }
