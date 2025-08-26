from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from auth.service.auth import token_factory
from user.model.response.user import UserResponse
from user.service import user as user_service
from util.token_factory import TokenFactory
import uuid

router = APIRouter(prefix="/api/users")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

token_factory = TokenFactory()
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    payload = token_factory.decode(token=token)
    return uuid.UUID(payload["user_id"])

class SignupRequest(BaseModel):
    username: str
    profile: str = ""
    password: str

class UpdateProfileRequest(BaseModel):
    profile: str

class UpdatePasswordRequest(BaseModel):
    password: str

@router.post("/signup", response_model=UserResponse)
def signup(req: SignupRequest):
    user_id = user_service.create_user(req.username, req.profile, req.password)
    user = user_service.get_user(user_id)
    return user

@router.get("/profile", response_model=UserResponse)
def get_profile(user_id: uuid.UUID = Depends(get_current_user_id)):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/update/password")
def update_password(
    req: UpdatePasswordRequest,
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    updated = user_service.update_user_password(user_id, req.password)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "Password updated"}

@router.patch("/update/profile")
def update_profile(
    req: UpdateProfileRequest,
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    updated = user_service.update_user_profile(user_id, req.profile)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "Profile updated"}