from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    # coding
    return {"Hello": "World"}


# 경로 매개 변수
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.post("/test")
async def create_item(value: str):
    msg = "%s 님 환영합니다." %value
    return msg




# 추가: 현재 유저를 반환하는 앤드포인트
@app.get("/users/aaa")
def get_current_user():
    return {"user_id": 123}


@app.get("/users/{user_id}")
def get_user(user_id: int):

    return {"user_id": user_id}








if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, reload=True)