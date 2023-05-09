from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from . models import *
from passlib.context import CryptContext
from fastapi_login import LoginManager
import uuid
import typing

router = APIRouter()
SECRET = 'your-secret-key'

manager = LoginManager(SECRET, token_url='/auth/token')
templates = Jinja2Templates(directory="user/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def flash(request: Request, message: typing.Any, category: str = "") -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(
        {"message": message, "category": category})


def get_flashed_messages(request: Request):
    print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []


templates.env.globals['get_flashed_messages'] = get_flashed_messages


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
    })


@router.post("/ragistration/", response_class=HTMLResponse)
async def read_item(request: Request, full_name: str = Form(...),
                    Email: str = Form(...),
                    Phone: str = Form(...),
                    Password: str = Form(...)):
    if await User.filter(email=Email).exists():
        flash(request, "Email alrady ragister")
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    elif await User.filter(phone=Phone).exists():
        flash(request, "Phone number alrady ragister")
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    else:
        await User.create(email=Email, name=full_name,
                          phone=Phone,
                          password=get_password_hash(Password))
        flash(request, "User sucessfull ragister")
        return RedirectResponse("/login/", status_code=status.HTTP_302_FOUND)


@router.get("/login/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
    })


@manager.user_loader()
async def load_user(phone: str):
    if await User.exists(phone=phone):
        user = await User.get(phone=phone)
        return user


@router.post('/loginuser/')
async def login(request: Request, Phone: str = Form(...),
                Password: str = Form(...)):
    Phone = Phone
    user = await load_user(Phone)
    if not user:
        return {'USER NOT REGISTERED'}
    elif not verify_password(Password, user.password):
        return {'PASSWORD IS WRONG'}
    access_token = manager.create_access_token(
        data=dict(sub=Phone)
    )
    if "_messages" not in request.session:
        request.session['_messages'] = []
        new_dict = {"user_id": str(
            user.id), "Phone": Phone, "access_token": str(access_token)}
        request.session['_messages'].append(
            new_dict
        )
    return RedirectResponse('/welcome/', status_code=status.HTTP_302_FOUND)


@router.get("/welcome/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("welcome.html", {
        "request": request,
    })


@router.get("/table/", response_class=HTMLResponse)
async def read_item(request: Request):
    persons = await User.all()
    return templates.TemplateResponse("table.html", {
        "request": request,
        "persons": persons
    })


@router.get("/update/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: int):
    person = await User.get(id=id)
    return templates.TemplateResponse("update.html", {
        "request": request,
        "person": person
    })


@router.post("/update_detials/")
async def update(request: Request, id: int = Form(...),
                 full_name: str = Form(...),
                 Email: str = Form(...),
                 Phone: str = Form(...),
                 ):
    person = await User.get(id=id)
    await person.filter(id=id).update(email=Email,
                                      name=full_name,
                                      phone=Phone
                                      )
    return RedirectResponse('/table/', status_code=status.HTTP_302_FOUND)


@router.get("/delete/{id}", response_class=HTMLResponse)
async def delete(request: Request, id: int):
    person_all = await User.get(id=id).delete()
    return RedirectResponse('/table/', status_code=status.HTTP_302_FOUND)
