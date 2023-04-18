from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from user import router as UsersRoute
from user import api as UsersAPI
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
from fastapi.middleware.cors import CORSMiddleware


db_url = DATABASE_URL()

middleware = [
    Middleware(SessionMiddleware, secret_key='super-secret')
]

app = FastAPI(middleware=middleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(UsersRoute.router)
app.include_router(UsersAPI.app, tags=["api"])


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://192.168.1.101:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


JWT_SECRET = 'myjwtsecret'

register_tortoise(
    app,
    db_url="postgres://postgres:12345@127.0.0.1/crudinfastapi",
    modules={'models': ['user.models',]},
    generate_schemas=True,
    add_exception_handlers=True
)
