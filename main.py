import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import os
load_dotenv()
from user.controller.user import router as user
from auth.controller.auth import router as auth
from locations.controller.locations import router as locations
from locations.controller.place_bookmark import router as place_bookmark
from locations.controller.rating import router as rating
from locations.controller.place import router as place
from locations.repository import apply_rating_trigger_migration

app = FastAPI()

@app.on_event("startup")
def _apply_db_triggers():
    try:
        apply_rating_trigger_migration()
    except Exception as e:
        # 필요 시 로깅
        print(f"DB trigger migration skipped: {e}")

# 라우터 등록
app.include_router(router=user)
app.include_router(router=auth)
app.include_router(router=locations)
app.include_router(router=place_bookmark)
app.include_router(router=rating)
app.include_router(router=place)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)