from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings

# DB接続エンジン
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True, # 接続が生きているか確認
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 全モデルの基底クラス
Base = declarative_base()

# FastAPI Depedency用のジェネレータ
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
