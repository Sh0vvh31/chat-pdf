from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from src.api.schemas import ChatMessageRequest, ChatMessageResponse, ThreadCreateRequest, ThreadCreateResponse, MessageHistorySchema
from src.api.deps import get_chat_use_case, get_chat_history_repo, get_db
from src.application.use_cases.chat_use_case import ChatUseCase
from src.application.ports.chat_history_repository import ChatHistoryRepositoryPort

router = APIRouter()

@router.post("/threads", response_model=ThreadCreateResponse)
def create_thread(request: ThreadCreateRequest, repo: ChatHistoryRepositoryPort = Depends(get_chat_history_repo)):
    """新しいチャットスレッドを作成する"""
    try:
        user_uuid = UUID(request.user_id)
        doc_uuid = UUID(request.document_id) if request.document_id else None
        thread_id = repo.create_thread(user_id=user_uuid, document_id=doc_uuid, title=request.title)
        return {"thread_id": thread_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/threads/{thread_id}/messages", response_model=List[MessageHistorySchema])
def get_thread_messages(thread_id: str, repo: ChatHistoryRepositoryPort = Depends(get_chat_history_repo)):
    """指定したスレッドの過去のメッセージとXAIソース履歴を取得する"""
    try:
        t_uuid = UUID(thread_id)
        messages = repo.get_thread_messages(t_uuid)
        return [
            MessageHistorySchema(role=m.role, content=m.content, sources=m.sources)
            for m in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/messages", response_model=ChatMessageResponse)
def send_message(request: ChatMessageRequest, use_case: ChatUseCase = Depends(get_chat_use_case)):
    """メッセージを送信し、RAGを通して回答を得る"""
    try:
        user_uuid = UUID(request.user_id)
        thread_uuid = UUID(request.thread_id)
        doc_uuid = UUID(request.document_id) if request.document_id else None
        
        result = use_case.handle_chat_message(
            user_id=user_uuid,
            thread_id=thread_uuid,
            question=request.question,
            document_id=doc_uuid,
            model_name=request.model_name
        )
        
        return ChatMessageResponse(
            answer=result["answer"],
            model_used=result["model_used"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
