import uuid
from typing import List, Optional
from user.repository import user as user_repo
from user.entity.user import User
import hashlib

def create_user(username: str, profile: str, password: str) -> uuid.UUID:
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return user_repo.create_user(username, profile, hashed_password)

from user.model.response.user import UserResponse

def get_user(user_id: uuid.UUID) -> Optional[UserResponse]:
    user = user_repo.get_user(user_id)
    if user:
        return UserResponse(id=str(user.id), username=user.username, profile=user.profile)
    return None

def list_users() -> List[UserResponse]:
    users = user_repo.list_users()
    return [UserResponse(id=u.id, username=u.username, profile=u.profile) for u in users]

def get_user_by_username(username: str) -> Optional[UserResponse]:
    user = user_repo.get_user_by_username(username)
    if user:
        return UserResponse(id=str(user.id), username=user.username, profile=user.profile)
    return None

def update_user_profile(user_id: uuid.UUID, profile: str) -> int:
    return user_repo.update_user_profile(user_id, profile)

def update_user_password(user_id: uuid.UUID, password: str) -> int:
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return user_repo.update_user_password(user_id, hashed_password)

def delete_user(user_id: uuid.UUID) -> int:
    return user_repo.delete_user(user_id)

def verify_password(username, password) -> bool:
    hashed_password = user_repo.get_password_by_username(username)
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed_password