from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from user import router as UsersRoute
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.hash import bcrypt
from tortoise.models import Model
from tortoise import fields
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from configs.connection import DATABASE_URL


db_url = DATABASE_URL()

middleware = [
    Middleware(SessionMiddleware, secret_key='super-secret')
]

app = FastAPI(middleware=middleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(UsersRoute.router)


JWT_SECRET = 'myjwtsecret'

register_tortoise(
    app,
    db_url=db_url,
    modules={'models': ['user.models',]},
    generate_schemas=True,
    add_exception_handlers=True
)
