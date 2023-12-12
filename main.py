from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Create a sqlite engine instance
engine = create_engine("sqlite:///medleysm.db")

# Create a DeclarativeMeta instance
Base = declarative_base()

# Define To Do class inheriting from Base
class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(String(256))
    likes = Column(Integer)
    parent_post = Column(Integer)
    fact_check = Column(Integer)
    user_name = Column(String(256))
    user_id = Column(Integer)

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    passwordHashed = Column(String)
    moderator = Column(Boolean)

# Create the database
Base.metadata.create_all(engine)

# Create createPost Base Model
class createPost(BaseModel):
    content: str
    parent_post: int

# Create createUser Base Model
class createUser(BaseModel):
    name: str
    password: str
    moderator: bool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/login")
async def login():
    return "login"

@app.get("/api/posts")
async def posts(start: int = 0, limit: int = 10):
    '''
    return a paginated list of posts
    take int start as first position
    take int limit as number of posts to return
    '''
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    posts = session.query(Post).where(Post.id>=start).limit(limit).all()

    # close the session
    session.close()
    return posts

@app.get("/api/post/{post_id}")
async def get_post(post_id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    post = session.query(Post).get(post_id)

    # close the session
    session.close()
    return post

@app.post("/api/post", status_code=status.HTTP_201_CREATED)
async def create_post(post: createPost):
    # get current user
    user_id = 0
    user_name = 'qwerty'
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the medleysmdb database model
    medleysmdb = Post(
        content = post.content,
        parent_post = post.parent_post,
        user_name = user_name,
        user_id = user_id
    )

    # add it to the session and commit it
    session.add(medleysmdb)
    session.commit()

    # grab the id given to the object from the database
    id = medleysmdb.id

    # close the session
    session.close()

    return f"create post {id}"

@app.put("/api/post/{post_id}")
async def update_post(post_id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    post = session.query(Post).get(post_id)

    # update todo item with the given task (if an item with the given id was found)
    if post:
        likes = post.likes + 1
        post.likes = likes
        session.commit()

    # close the session
    session.close()

    # check if todo item with given id exists. If not, raise exception and return 404 not found response
    if not post:
        raise HTTPException(status_code=404, detail=f"Post not found")

    # return post.likes
    return "update post"

@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    user = session.query(Users).get(user_id)

    # close the session
    session.close()
    return user

@app.get("/api/users")
async def users():
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    users = session.query(Users).all()

    # close the session
    session.close()
    return users

@app.post("/api/user")
async def create_user(user: createUser):
    # hash password
    passwordHash = user.password + 'trash'

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the medleysmdb database model
    medleysmdb = Users(
        name = user.name,
        passwordHashed = passwordHash,
        moderator = user.moderator
    )

    # add it to the session and commit it
    session.add(medleysmdb)
    session.commit()

    # grab the id given to the object from the database
    id = medleysmdb.id

    # close the session
    session.close()

    return f"create user {id}"
