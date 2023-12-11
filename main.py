from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/")
async def root(skip: int = 0, limit: int = 10):
    return "a paginated list of posts"

@app.get("/post/{post_id}")
async def post(post_id: int):
    return "a post"

@app.get("/user/{user_id}")
async def user(user_id: int):
    return "a list of posts from a user"
