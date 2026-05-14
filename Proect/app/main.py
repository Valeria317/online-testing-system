from fastapi import FastAPI

from app import auth
from app.database import Base, engine
from app.routers import history, test
from fastapi.responses import RedirectResponse

Base.metadata.create_all(bind = engine)
app = FastAPI(title = "Online Testing System")
app.include_router(auth.router)
app.include_router(test.router)
app.include_router(history.router)

@app.get("/")
async def root():
    # Сразу перенаправляем на страницу входа
    return RedirectResponse(url="/auth/login")