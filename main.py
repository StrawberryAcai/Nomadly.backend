import uvicorn
from fastapi import FastAPI
from user.controller.user import router as user
from auth.controller.auth import router as auth
from locations.controller.locations import router as locations

app = FastAPI()

app.include_router(router=user)
app.include_router(router=auth)
app.include_router(router=locations)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)