import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from src.infrastructure.db.models import Base, User

# テスト用のDB接続 (同じローカルDBを使うが、本来はテスト専用DBを別立てするのが望ましい)
# 今回は疎通確認のため既存のDBを使用
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    # テスト開始時にテーブルを作成 (Vector拡張機能が必要)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # 今回の簡単なテストではDROPしない（永続確認のため）

def test_db_connection_and_table_creation(db_session):
    """
    DBへの接続と users テーブルの作成・簡単なINSERTが正常に行えるか（pgvector拡張等の問題がないか）テストする
    """
    # 既存のテストユーザーがいれば削除
    db_session.query(User).filter(User.username == "test_user_tdd").delete()
    db_session.commit()
    
    # 新規作成
    new_user = User(username="test_user_tdd", hashed_password="fakehash")
    db_session.add(new_user)
    db_session.commit()
    
    # 検索
    db_user = db_session.query(User).filter(User.username == "test_user_tdd").first()
    
    assert db_user is not None
    assert db_user.username == "test_user_tdd"
    assert db_user.hashed_password == "fakehash"
