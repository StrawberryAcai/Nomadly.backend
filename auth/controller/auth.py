from fastapi import APIRouter, HTTPException, status, Request, Response
from pydantic import BaseModel
from auth.service import auth as auth_service

router = APIRouter(prefix="/api/auth")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    result: bool

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, response: Response):
    try:
        # access token, refresh token 모두 발급
        access_token, refresh_token = auth_service.authenticate_and_issue_jwt(req.username, req.password)

        # access token은 헤더에
        response.headers["Authorization"] = f"Bearer {access_token}"

        # refresh token은 쿠키에 저장
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,
            secure=True,        # HTTPS 환경에서만 전송
            samesite="strict",  # CSRF 방지
            max_age=60 * 60 * 24 * 7  # 7일
        )
        return TokenResponse(result=True)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@router.post("/reissue", response_model=TokenResponse)
def reissue(request: Request, response: Response):
    refresh_token = request.cookies.get("refreshToken")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token required")

    try:
        # refresh 토큰을 검증 후 새 access 토큰 발급
        new_access_token, new_refresh_token = auth_service.reissue_access_token(refresh_token)

        # access token은 헤더에
        response.headers["Authorization"] = f"Bearer {new_access_token}"

        # refresh token 갱신 시 쿠키에도 다시 저장
        response.set_cookie(
            key="refreshToken",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=60 * 60 * 24 * 7
        )
        return TokenResponse(result=True)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")