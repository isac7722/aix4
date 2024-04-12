from typing import Optional
from pydantic import BaseModel, HttpUrl
import uvicorn
from fastapi import FastAPI

app = FastAPI()

class UserInfo(BaseModel):
    name: str
    password: str
    avatar_url: Optional[HttpUrl] = None


@app.get("/users")
def get_users(limit:int = 100):
    return {"limit":limit}

@app.get("/students")
def get_student(name: str = "홍길동"):
    return {"student":name}

@app.post("/create")
def createUser(user: UserInfo):

    # business logic here

    return user

@app.post("/users/me", response_model=UserInfo)
def getUser(user_info: UserInfo):
    return user_info

if __name__ == "__main__":
    uvicorn.run("main2:app", reload=True)