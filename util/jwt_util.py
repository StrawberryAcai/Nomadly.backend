import uuid
import datetime
import jwt
from abc import ABC, abstractmethod
from util.jwt_config import get_jwt_config

# Get JWT config bean (like Spring @Autowired)
jwt_config = get_jwt_config()

class Token(ABC):
    """토큰 생성을 위한 공통 인터페이스"""
    def __init__(self, user_id: uuid.UUID):
        self.user_id = user_id

    @abstractmethod
    def create(self) -> str:
        pass


class AccessToken(Token):
    def create(self) -> str:
        exp = datetime.datetime.now() + datetime.timedelta(minutes=15)
        payload = {"user_id": str(self.user_id), "type": "access", "exp": exp}
        return jwt.encode(payload, jwt_config.secret_key, algorithm=jwt_config.algorithm)


class RefreshToken(Token):
    def create(self) -> str:
        exp = datetime.datetime.now() + datetime.timedelta(days=7)
        payload = {"user_id": str(self.user_id), "type": "refresh", "exp": exp}
        return jwt.encode(payload, jwt_config.secret_key, algorithm=jwt_config.algorithm)