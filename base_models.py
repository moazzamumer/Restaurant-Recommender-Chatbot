from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str

class User(BaseModel):
    user_id:int
    username: str    