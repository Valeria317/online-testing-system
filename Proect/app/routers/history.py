from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import database, models
from jose import jwt
from app.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/history", tags=["history"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def show_history(request: Request, db: Session = Depends(database.get_db)):
    # Получаем токен из cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            return RedirectResponse(url="/auth/login", status_code=303)
    except Exception:
        return RedirectResponse(url="/auth/login", status_code=303)

    # Получаем все попытки пользователя, сортируем по дате (сначала новые)
    attempts = db.query(models.TestAttempt).filter(
        models.TestAttempt.user_id == user.id
    ).order_by(models.TestAttempt.created_at.desc()).all()

    return templates.TemplateResponse("history.html", {"request": request, "attempts": attempts})