from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

# ルーターのインポート
from src.api.routers import users, documents, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS (StreamlitからのUI呼び出しを許可)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発環境向け。本番は限定する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to ChatPDF API"}

# APIルーターの登録
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
