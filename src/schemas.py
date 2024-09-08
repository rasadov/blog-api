from pydantic import BaseModel

class UserRegisterSchema(BaseModel):
    email: str
    password: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class TokenData(BaseModel):
    user_id: int

class PostSchema(BaseModel):
    content: dict
