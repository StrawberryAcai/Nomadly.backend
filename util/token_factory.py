import uuid
import jwt
from util.jwt_util import RefreshToken, AccessToken
from util.jwt_config import get_jwt_config

# Get JWT config bean
jwt_config = get_jwt_config()


class TokenFactory:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.token_types = {
                "access": AccessToken,
                "refresh": RefreshToken
            }
            self._initialized = True

    def create_token(self, token_type: str, user_id: uuid.UUID) -> str:
        if token_type not in self.token_types:
            raise ValueError("Invalid token type")
        return self.token_types[token_type](user_id).create()

    def decode(self, token: str) -> dict:
        try:
            return jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")