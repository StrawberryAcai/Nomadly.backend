import uuid
from user.service import user as user_service
from util.token_factory import TokenFactory

token_factory = TokenFactory()

def authenticate_and_issue_jwt(username: str, password: str) -> tuple[str, str]:
    user = user_service.get_user_by_username(username)
    if not user or not user_service.verify_password(username, password):
        raise ValueError("Invalid credentials")

    user_id = uuid.UUID(user.id)
    access_token = token_factory.create_token("access", user_id)
    refresh_token = token_factory.create_token("refresh", user_id)
    return access_token, refresh_token


def reissue_access_token(refresh_token: str) -> tuple[str, str]:
    payload = token_factory.decode(refresh_token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token type")

    user_id = uuid.UUID(payload["user_id"])
    new_access = token_factory.create_token("access", user_id)
    new_refresh = token_factory.create_token("refresh", user_id)  # Rotation
    return new_access, new_refresh