from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.application.ports.user_repository import UserRepositoryPort, UserDomainModel
from src.infrastructure.db.models import User as DBUser

class PgUserRepository(UserRepositoryPort):
    def __init__(self, db: Session):
        self.db = db
        
    def _to_domain(self, db_model: DBUser) -> UserDomainModel:
        return UserDomainModel(
            id=db_model.id,
            username=db_model.username,
            hashed_password=db_model.hashed_password
        )

    def get_by_id(self, user_id: UUID) -> Optional[UserDomainModel]:
        db_user = self.db.query(DBUser).filter(DBUser.id == user_id).first()
        return self._to_domain(db_user) if db_user else None

    def get_by_username(self, username: str) -> Optional[UserDomainModel]:
        db_user = self.db.query(DBUser).filter(DBUser.username == username).first()
        return self._to_domain(db_user) if db_user else None

    def create(self, username: str, hashed_password: str) -> UserDomainModel:
        db_user = DBUser(username=username, hashed_password=hashed_password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_domain(db_user)
