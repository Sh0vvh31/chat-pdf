import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from src.application.ports.user_repository import UserDomainModel
from src.infrastructure.db.repositories.user_repository import PgUserRepository
from src.infrastructure.db.models import User as DBUser

def test_user_repository_create():
    # Arrange
    mock_db_session = MagicMock()
    # mock_db_session.add, commit, refresh etc
    
    def side_effect_refresh(obj):
        obj.id = uuid4()
    mock_db_session.refresh.side_effect = side_effect_refresh
    
    repo = PgUserRepository(db=mock_db_session)
    
    # Act
    domain_user = repo.create(username="test_user", hashed_password="fakehash")
    
    # Assert
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    assert mock_db_session.refresh.called
    
    assert domain_user.username == "test_user"
    assert domain_user.hashed_password == "fakehash"
    assert domain_user.id is not None

def test_user_repository_get_by_username():
    mock_db_session = MagicMock()
    repo = PgUserRepository(db=mock_db_session)
    
    # Mocking chain: db.query().filter().first()
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    
    fake_uuid = uuid4()
    mock_filter.first.return_value = DBUser(id=fake_uuid, username="test_user", hashed_password="fakehash")
    
    domain_user = repo.get_by_username("test_user")
    
    assert domain_user.username == "test_user"
    assert domain_user.id == fake_uuid
