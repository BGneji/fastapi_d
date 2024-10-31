from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from backend.db import engine, Base, SessionLocal
from models.users import User
from routers import register
from routers.register import templates
from schemas import UserCreate
from fastapi import Request

app = FastAPI(
    title='Mini_fast_api'
)

Base.metadata.create_all(bind=engine)
app.include_router(register.router)


@app.get('/')
def index(request: Request):
    context = {
        'title': 'Главая страница',
        'request': request
    }
    return templates.TemplateResponse("index.html", context)


@app.get('/user/{first_name}/{last_name}')
def us(first_name: str, last_name: str):
    return {'mes': f'{first_name} {last_name}'}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8123)
