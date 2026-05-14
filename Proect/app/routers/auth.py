
from fastapi.requests import Request

from fastapi import APIRouter, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app import database, auth, models

router = APIRouter(prefix="/auth",tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/register", response_class= HTMLResponse)
async def register_from(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request,"error": "Username already exists"})
    hashed = auth.get_password_hash(password)
    new_user = models.User(username=username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/auth/login", status_code=303)

@router.get("/login", response_class= HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db,username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request,"error": "Incorrect credentials"})
    access_token = auth.create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/test", status_code=303)
    response.set_cookie(key="access_token", value= f"Bearer {access_token}", httponly=True)
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie(key="access_token")
    return response