from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.api.deps import get_db
from src.infrastructure.db.repositories.user_repository import PgUserRepository

router = APIRouter()

class UserCreateRequest(BaseModel):
    username: str
    password: str

class UserCreateResponse(BaseModel):
    user_id: str
    username: str

@router.post("/register", response_model=UserCreateResponse)
def register_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    """ユーザー登録のエンドポイント (今回は平文ハッシュなど簡略化)"""
    repo = PgUserRepository(db)
    
    # 既存チェック
    existing = repo.get_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # 本番ではBcryptなどでハッシュ化する
    hashed_pw = f"hash_{request.password}" 
    
    new_user = repo.create(username=request.username, hashed_password=hashed_pw)
    
    return {"user_id": str(new_user.id), "username": new_user.username}

@router.post("/login")
def login(request: UserCreateRequest, db: Session = Depends(get_db)):
    """仮のログインエンドポイント"""
    repo = PgUserRepository(db)
    user = repo.get_by_username(request.username)
    
    if not user or user.hashed_password != f"hash_{request.password}":
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    return {"access_token": "fake-token", "user_id": str(user.id), "username": user.username}
