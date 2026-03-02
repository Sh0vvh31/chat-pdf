from typing import Protocol, Optional
from uuid import UUID

class UserDomainModel:
    def __init__(self, id: UUID, username: str, hashed_password: str):
        self.id = id
        self.username = username
        self.hashed_password = hashed_password

class UserRepositoryPort(Protocol):
    def get_by_id(self, user_id: UUID) -> Optional[UserDomainModel]:
        ...
        
    def get_by_username(self, username: str) -> Optional[UserDomainModel]:
        ...
        
    def create(self, username: str, hashed_password: str) -> UserDomainModel:
        ...
