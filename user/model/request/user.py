import re
import string
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    # Checks for at least one special character
    if not re.search(f"[{re.escape(string.punctuation)}]", password):
        raise ValueError("Password must contain at least one special character")
    return password


Password = Annotated[str, Field(validate_default=True), field_validator("password", mode="before")(validate_password)]


class SignupRequest(BaseModel):
    username: str
    profile: str = ""
    password: Password


class UpdateProfileRequest(BaseModel):
    profile: str


class UpdatePasswordRequest(BaseModel):
    password: Password
