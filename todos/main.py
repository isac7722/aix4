import os
from fastapi import FastAPI, Form, Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
from pydantic import BaseModel

from models import User
import bcrypt

from starlette.middleware.sessions import SessionMiddleware

# 여기서 데이터베이스 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# session middleware 설치
app.add_middleware(SessionMiddleware, secret_key="secret_key")

abs_path = os.path.dirname(os.path.realpath(__file__))

# html 템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
# app.mount("/static", StaticFiles(directory=f"static"))
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"))

# Dependency Injection(의존성 주임을 위한 함수)
# yield :  FastAPI가 함수 실행을 일시 중지하고 DB 세션을 호출자에게 반환하도록 지시


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):

    user_id = request.session.get('user_id')

    print("come here")
    print (user_id)

    if not user_id:
        return templates.TemplateResponse("login.html", {"request": request, "error": "로그인이 필요한 세션입니다"})

    todos = db.query(models.Todo).order_by(models.Todo.id.desc())

    if not todos:
        todos = []  # Make sure todos is always a list, not an integer

    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": todos,
                                       "user_id": user_id})


@app.post("/add")
def add(req: Request, title: str = Form(...), db: Session = Depends(get_db)):
    print(title)
    # Todo 객체 생성
    new_todo = models.Todo(task=title)
    # DB테이블에 create
    db.add(new_todo)
    # db 트랜젝션 완료
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


# 수정할 todo 클릭했을 때
@app.get("/update/{todo_id}")
def update(req: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    print(todo.completed)
    todo.completed = not todo.completed
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

# todo 삭제


@app.get("/delete/{todo_id}")
def delete(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


@app.post("/signup/")
def create_user(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already registered")
    new_user = User(username=username,
                    password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login/")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()

    # 인증된 사용자 없음
    if not db_user or not verify_password(password, db_user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "id or password is wrong"})

    # 로그인 성공시 session 에 사용자 정보(user_id) 담아서 보내줌
    request.session['user_id'] = db_user.id

    print(db_user.id)


    return templates.TemplateResponse("index.html", {"request": request,
                                                     "user_id": db_user.id})


# 로그아웃 기능
@app.post("/logout/")
def logout(request: Request):
    request.session.pop('user_id', None)

    return templates.TemplateResponse("login.html", {"request": request})




# 로그인 페이지
@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 회원가입 페이지


@app.get("/signup")
def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})
