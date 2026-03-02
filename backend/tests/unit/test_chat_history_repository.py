import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.infrastructure.db.repositories.chat_history_repository import PgChatHistoryRepository
from src.infrastructure.db.models import ChatThread, ChatMessage

def test_create_thread():
    mock_db = MagicMock()
    
    def side_effect_refresh(obj):
        obj.id = uuid4()
    mock_db.refresh.side_effect = side_effect_refresh
    
    repo = PgChatHistoryRepository(db=mock_db)
    user_id = uuid4()
    
    thread_id = repo.create_thread(user_id=user_id, title="Test Thread")
    
    assert mock_db.add.called
    assert mock_db.commit.called
    assert thread_id is not None

def test_save_message():
    mock_db = MagicMock()
    
    def side_effect_refresh(obj):
        obj.id = uuid4()
    mock_db.refresh.side_effect = side_effect_refresh
    
    repo = PgChatHistoryRepository(db=mock_db)
    thread_id = uuid4()
    sources_data = {"chunks": [{"content": "source text"}]}
    
    msg = repo.save_message(
        thread_id=thread_id,
        role="assistant",
        content="This is the answer.",
        sources=sources_data
    )
    
    assert mock_db.add.called
    assert mock_db.commit.called
    assert msg.role == "assistant"
    assert msg.content == "This is the answer."
    assert msg.sources == sources_data

def test_get_thread_messages():
    mock_db = MagicMock()
    repo = PgChatHistoryRepository(db=mock_db)
    
    # query chain
    mock_query = MagicMock()
    mock_db.query.return_value = mock_query
    
    mock_msg1 = MagicMock()
    mock_msg1.id = uuid4()
    mock_msg1.thread_id = uuid4()
    mock_msg1.role = "user"
    mock_msg1.content = "question"
    mock_msg1.sources = None
    
    mock_msg2 = MagicMock()
    mock_msg2.id = uuid4()
    mock_msg2.thread_id = uuid4()
    mock_msg2.role = "assistant"
    mock_msg2.content = "answer"
    mock_msg2.sources = {"used": True}
    
    mock_query.filter().order_by().all.return_value = [mock_msg1, mock_msg2]
    
    messages = repo.get_thread_messages(thread_id=uuid4())
    
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].sources == {"used": True}
