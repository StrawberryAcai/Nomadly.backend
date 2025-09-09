import uvicorn
from fastapi import FastAPI
from user.controller.user import router as user
from user.controller.interest import router as interest
from auth.controller.auth import router as auth
from locations.controller.distance import router as locations

# Initialize JWT configuration on startup (like Spring @Configuration)
from util.jwt_config import jwt_config
print(f"🚀 Application starting with JWT configuration...")

app = FastAPI()

app.include_router(router=user)
app.include_router(router=interest)
app.include_router(router=auth)
app.include_router(router=locations)

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8000))
    uvicorn.run("main:app", host='0.0.0.0', port=port, reload=True)
