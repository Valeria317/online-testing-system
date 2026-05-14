import os
from datetime import timedelta, datetime

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, APIRouter, Form, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import models, config, database, schemas
from app.database import get_db
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["authentication"])

templates = Jinja2Templates(directory="app/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пользователь уже существует"})
    hashed = hash_password(password)
    new_user = models.User(username=username, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/auth/login", status_code=303)

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        # Вернуть страницу логина с ошибкой
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse(url="/test/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


