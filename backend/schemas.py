from pydantic import BaseModel, EmailStr

"""
schemas.py

These schemas are used for validating the schema of the classes
"""

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None

class LoginUser(BaseModel):
    email: EmailStr
    password: str

    # class Config:
    #     orm_mode = True
    #     use_enum_values = True

class UserBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    image_path: str

class UserRegister(UserBase):
    password: str

# inherits
class User(UserBase):
    id: int

class UserLoginResponse(Token):
    id: str

