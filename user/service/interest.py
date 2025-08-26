from user.repository import interest as interest_repo
from user.entity.interest import Interest
import uuid
from typing import List, Optional

def create_interest(user_id: uuid.UUID, interest: str) -> int:
    return interest_repo.create_interest(user_id, interest)

def get_interest(interest_id: int) -> Optional[Interest]:
    return interest_repo.get_interest(interest_id)

def update_interest(interest_id: int, user_id: uuid.UUID, interest: str) -> int:
    return interest_repo.update_interest(interest_id, user_id, interest)

def delete_interest(interest_id: int) -> int:
    return interest_repo.delete_interest(interest_id)

def list_interests() -> List[Interest]:
    return interest_repo.list_interests()