from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any
import os
import tempfile
from src.api.deps import get_document_extraction_use_case, get_db
from src.application.use_cases.document_extraction_use_case import DocumentExtractionUseCase

router = APIRouter()

@router.post("/upload")
async def upload_document(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    use_case: DocumentExtractionUseCase = Depends(get_document_extraction_use_case)
):
    """PDFをアップロードし、テキスト抽出・ベクトル化・DB保存を行う"""
    try:
        user_uuid = UUID(user_id)
        
        # Tempfileに保存して処理 (実運用ではS3等に保存してから処理)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
            
        try:
            doc_id = use_case.process_document(
                user_id=user_uuid,
                file_path=tmp_path,
                filename=file.filename
            )
            return {"document_id": doc_id, "filename": file.filename, "status": "processed"}
        finally:
            # 処理が終わったらTempfile削除
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
