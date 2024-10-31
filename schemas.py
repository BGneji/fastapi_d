from pydantic import BaseModel


class UserCreate(BaseModel):
    id: int
    username: str
    password: str
    repeat_password: str



