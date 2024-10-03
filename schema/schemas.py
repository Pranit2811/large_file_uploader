from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserDisplay(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
