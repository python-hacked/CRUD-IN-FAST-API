from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from . models import *
from json import JSONEncoder
from fastapi.encoders import jsonable_encoder

from passlib.context import CryptContext
from fastapi_login.exceptions import InvalidCredentialsException

from fastapi_login import LoginManager
from .pydantic_models import Person, Loginuser, Token, Userupdate,Get
import uuid
import typing

app = APIRouter()
SECRET = 'your-secret-key'

manager = LoginManager(SECRET, token_url='/user/login/')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@app.post("/")
async def registration(data: Person):
    phone_number = str(data.phone)  # Convert phone number to a string

    if len(phone_number) != 10:
        return {"status": False, "message": "Invalid number"}

    if await User.exists(phone=phone_number):
        return {"status": False, "message": "Phone number already exists"}
    elif await User.exists(email=data.email):
        return {"status": False, "message": "Email already exists"}
    else:
        user_obj = await User.create(
            email=data.email,
            name=data.name,
            phone=phone_number,
            password=get_password_hash(data.password)
        )
        return user_obj



@manager.user_loader()  
async def load_user(email: str):
    if await User.exists(email=email):
        user = await User.get(email=email)   
        return user

# Login in users
@app.post('/login/', )
async def login(data: Loginuser,
                ):
    email = data.email
    user = await load_user(email)
 
    if not user:
        return JSONResponse({'status': False, 'message': 'User not Registered'}, status_code=403)
    elif not verify_password(data.password, user.password):
        return JSONResponse({'status': False, 'message': 'Invalid password'}, status_code=403)
    access_token = manager.create_access_token(
        data={'sub': dict({"id":jsonable_encoder(user.id)}), }
        
    )
    '''test  current user'''
    new_dict = jsonable_encoder(user)
    new_dict.update({"access_token": access_token})
    return Token(access_token=access_token, token_type='bearer')


@app.post("/data/")
async def all_user(data:Get):
    user = await User.get(id=data.id)
    return user


@app.put('/update/')
async def update_user(data:Userupdate):
    user = await User.get(id=data.id)
    if not user:
        return {"status": False, "message": "User not Found"}
    else:
        user_obj = User.filter(id=data.id).update(name = data.name,
                                                  email = data.email, phone = data.phone)
        return user_obj
