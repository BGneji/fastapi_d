import hashlib
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.db_depends import get_db

from models.users import User
from schemas import UserCreate

router = APIRouter(prefix="/register", tags=["register"])
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
from fastapi import Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select, update
from fastapi import Form

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/all_user", response_class=HTMLResponse)
async def get_all_messages(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    users_all = db.scalars(select(User)).all()
    context = {
        "request": request,
        "db_users": users_all,
        'title': "Все пользователи",
    }
    return templates.TemplateResponse("all_user.html", context)


import bcrypt


@router.post("/", response_class=HTMLResponse)
def register_user(request: Request, username: str = Form(...), password: str = Form(...),
                  repeat_password: str = Form(...), db: Session = Depends(get_db)):
    context = {
        "request": request,
        'error': 'Такой пользователь существует',
        'error1': 'Пароли не совпадают!',
        'username': username
    }
    # Проверка на существование пользователя
    existing_user = db.query(User).filter(User.username == username).first()
    print("Регистрация")
    if existing_user:
        return templates.TemplateResponse("register.html", context)
    if password != repeat_password:
        return templates.TemplateResponse("register.html", context)

    def my_hash(text):
        return hashlib.sha256(text.encode()).hexdigest()

    # Создание нового пользователя
    new_user = User(username=username, password=my_hash(password),
                    repeat_password=my_hash(repeat_password))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return templates.TemplateResponse("access_reg.html", context)


@router.get("/{user_id}")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user_one = db.query(User).filter(User.id == user_id)
    context = {
        'request': request,
        'user': user_one,
        'title': "Об пользователе"
    }
    return templates.TemplateResponse('user_one.html', context)


@router.get("/update_user_form/{user_id}", response_class=HTMLResponse)
async def update_user_form(request: Request, user_id: int):
    return templates.TemplateResponse("update_user.html", {"request": request, "user_id": user_id})


@router.post("/update_user")
async def update_user(
        request: Request,
        user_id: int = Form(...),
        old_password: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        repeat_password: str = Form(...),
        db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    context = {
        'request': request,
        'error1': 'Пароли не совпадают!'
    }
    if password != repeat_password:
        return templates.TemplateResponse("update_user.html", context)

    def my_hash(text):
        return hashlib.sha256(text.encode()).hexdigest()

    if my_hash(old_password) != user.password:
        return templates.TemplateResponse("denied_update.html",  context)



    db.execute(update(User).where(User.id == user_id).values(
        username=username,
        password=my_hash(password),
        repeat_password=my_hash(repeat_password),
    ))
    db.commit()

    return templates.TemplateResponse("access_update.html", context)
