# TODO: remove mock data 

from fastapi import FastAPI, Path, status
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

# Create a sqlite engine instance
engine = create_engine("sqlite:///medleysm.db")

# Create a DeclarativeMeta instance
Base = declarative_base()

# Define To Do class inheriting from Base
class post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(String(256))
    likes = Column(Integer)
    parent_post = Column(Integer)
    fact_check = Column(Integer)
    user_id = Column(Integer)
    child_posts = Column(Integer)

# Create the database
Base.metadata.create_all(engine)


# Create createPost Base Model
class createPost(BaseModel):
    content: str
    parent_post: int
    user_id: int
    child_posts: int


app = FastAPI()


# some mock data
users = [
            {
                "id": 0,
                "name": "user0"
            },
            {
                "id": 1,
                "name": "user1"
            },
        ]
posts = [
            {
                "id": 0,
                "content": "text",
                "likes": 42,
                "parent_post": None,
                "fact_check": 0,
                "user_id": 0
            },
            {
                "id": 1,
                "content": "text1",
                "likes": 0,
                "parent_post": None,
                "fact_check": 0,
                "user_id": 0
            },
            {
                "id": 2,
                "content": "text",
                "likes": 42,
                "parent_post": None,
                "fact_check": 0,
                "user_id": 0
            },
            {
                "id": 3,
                "content": "text1",
                "likes": 0,
                "parent_post": None,
                "fact_check": 0,
                "user_id": 0
            }
        ]
post = {
            "id": 0,
            "content": "text",
            "likes": 42,
            "parent_post": None,
            "fact_check": 0,
            "user_id": 0,
            "child_posts": posts
        }



@app.get("/")
async def root(start: int = 0, limit: int = 10):
    '''
    return a paginated list of posts
    take int start as first position
    take int limit as number of posts to return
    '''
    return posts[start: start + limit]

@app.get("/post/{post_id}")
async def post(post_id: int):
    return post

@app.post("/post", status_code=status.HTTP_201_CREATED)
async def post(post: createPost):
    return "create post"

@app.put("/post/{post_id}")
async def post(post_id: int):
    return "create post"

@app.get("/user/{user_id}")
async def user(user_id: int):
    return posts
