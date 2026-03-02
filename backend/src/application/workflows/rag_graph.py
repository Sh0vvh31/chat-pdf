from langgraph.graph import StateGraph, START, END
from src.application.workflows.rag_state import RAGState
from src.application.ports.document_repository import DocumentRepositoryPort
from src.application.ports.embedding_port import EmbeddingPort
from src.application.ports.llm_port import LLMPort
import uuid

class RAGWorkflow:
    def __init__(
        self,
        document_repo: DocumentRepositoryPort,
        embedding_port: EmbeddingPort,
        llm_port: LLMPort,
        default_model: str = "gemma:2b"
    ):
        self.document_repo = document_repo
        self.embedding_port = embedding_port
        self.llm_port = llm_port
        self.default_model = default_model
        self.graph = self._build_graph()

    def _retrieve_node(self, state: RAGState) -> RAGState:
        """Vector DBから関連するチャンクを検索する"""
        question = state.get("question", "")
        doc_id_str = state.get("document_id")
        
        # 質問をベクトル化
        query_embedding = self.embedding_port.embed_text(question)
        
        doc_id = uuid.UUID(doc_id_str) if doc_id_str else None
        
        # 類似チャンク検索
        results = self.document_repo.search_similar_chunks(
            query_embedding=query_embedding,
            limit=3,
            document_filter_id=doc_id
        )
        
        retrieved_chunks = [
            {"content": r.content, "metadata": r.metadata, "distance": r.distance}
            for r in results
        ]
        
        return {**state, "retrieved_chunks": retrieved_chunks}

    def _generate_node(self, state: RAGState) -> RAGState:
        """LLMを使って回答を生成する"""
        question = state.get("question", "")
        retrieved_chunks = state.get("retrieved_chunks", [])
        chat_history = state.get("chat_history", [])
        image_bytes = state.get("image_bytes", None)
        requested_model = state.get("requested_model", None)
        
        # コンテキストの組み立て
        context_text = "\n\n".join([chunk["content"] for chunk in retrieved_chunks])
        
        system_prompt = (
            "You are a helpful assistant for reading PDF documents. "
            "Use the following pieces of context to answer the user's question. "
            "If you don't know the answer or the context doesn't contain it, "
            "just say that you don't know, don't try to make up an answer.\n\n"
            f"Context:\n{context_text}"
        )
        
        # LLM用メッセージの構築
        llm_messages = [{"role": "system", "content": system_prompt}]
        
        # 履歴の追加
        for msg in chat_history:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})
            
        # 最新の質問
        llm_messages.append({"role": "user", "content": question})
        
        # 画像がある場合はマルチモーダル(MiniCPM-V 等)にルーティング
        # そうでなければ、フロントから指定されたモデル（無ければデフォルト）を使用
        if image_bytes and len(image_bytes) > 0:
            model_name = "minicpm-v" 
        else:
            model_name = requested_model if requested_model else self.default_model
            
        llm_response = self.llm_port.generate_chat_response(
            messages=llm_messages,
            model_name=model_name,
            image_bytes=image_bytes
        )
        
        return {
            **state,
            "final_answer": llm_response.content,
            "used_model": llm_response.used_model
        }

    def _build_graph(self):
        workflow = StateGraph(RAGState)
        
        # ノードの追加
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate", self._generate_node)
        
        # エッジ(フロー)の定義
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        # グラフをコンパイル
        return workflow.compile()

    def invoke(self, initial_state: dict) -> dict:
        """ワークフローを実行する"""
        return self.graph.invoke(initial_state)
