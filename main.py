import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv()
from starlette.middleware.cors import CORSMiddleware
# 라우터 등록
from user.controller.user import router as user
from user.controller.interest import router as interest
from auth.controller.auth import router as auth
from locations.controller.locations import router as locations
from locations.controller.place_bookmark import router as place_bookmark
from locations.controller.rating import router as rating
from locations.controller.place import router as place
from locations.repository import apply_rating_trigger_migration
from locations.controller.distance import router as locations
from mypage.controller.mypage import router as mypage
from board.controller.document import router as document
from board.controller.like import router as actions
# Initialize JWT configuration on startup (like Spring @Configuration)
from util.jwt_config import jwt_config
print(f"🚀 Application starting with JWT configuration...")

app = FastAPI()

@app.on_event("startup")
def _apply_db_triggers():
    try:
        apply_rating_trigger_migration()
    except Exception as e:
        # 필요 시 로깅
        print(f"DB trigger migration skipped: {e}")

origins = [
    "https://nomadly.bitworkspace.kr"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,   # 쿠키 전달 허용 (refreshToken 쿠키 때문에 필요)
    allow_methods=["*"],      # 모든 HTTP 메서드 허용
    allow_headers=["*"],      # 모든 헤더 허용
    expose_headers=["Authorization"],  # <- 여기 추가
)
app.include_router(router=user)
app.include_router(router=interest)
app.include_router(router=auth)
app.include_router(router=locations)
app.include_router(router=place_bookmark)
app.include_router(router=rating)
app.include_router(router=place)
app.include_router(router=mypage)
app.include_router(router=document)
app.include_router(router=actions)

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host='0.0.0.0', port=port, reload=True)
