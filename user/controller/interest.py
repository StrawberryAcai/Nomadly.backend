from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from user.model.request.interest import CreateInterestRequest
from user.model.response.interest import InterestResponse
from user.service import interest as interest_service
from util.token_factory import TokenFactory
import uuid

router = APIRouter(prefix="/api/interests")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

token_factory = TokenFactory()
def get_current_user_id(token: str = Depends(oauth2_scheme)) -> uuid.UUID:
    payload = token_factory.decode(token=token)
    return uuid.UUID(payload["user_id"])

@router.post("", response_model=InterestResponse)
def create_interest(
    req: CreateInterestRequest,
    user_id: uuid.UUID = Depends(get_current_user_id)
):
    interest_id = interest_service.create_interest(user_id, req.interest)
    interest = interest_service.get_interest(interest_id)
    return interest


@router.delete("/{interest_id}")
def delete_interest(interest_id: int):
    deleted = interest_service.delete_interest(interest_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interest not found")
    return {"msg": "Interest deleted"}

@router.get("", response_model=list[InterestResponse])
def list_interests(user_id: uuid.UUID = Depends(get_current_user_id)):
    interests = interest_service.get_user_interests(user_id)
    return interests