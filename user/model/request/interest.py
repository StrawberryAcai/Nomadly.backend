from pydantic import BaseModel


class CreateInterestRequest(BaseModel):
    interest: str