from pydantic import BaseModel


class Person(BaseModel):
    email:str
    name:str
    phone:int
    password:str


class Loginuser(BaseModel):
    email : str
    password : str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Userupdate(BaseModel):
    id : int
    name : str
    phone : int
    email : str

class Get(BaseModel):
    id:int    