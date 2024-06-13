from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str

class UserLogin(BaseModel):
    username: str

class User(BaseModel):
    user_id:int
    username: str    