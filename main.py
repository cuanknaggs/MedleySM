from fastapi import FastAPI, Path, status, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
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
    user_id = Column(Integer)

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)

# Create the database
Base.metadata.create_all(engine)

# Create createPost Base Model
class createPost(BaseModel):
    content: str
    parent_post: int

# Create createUser Base Model
class createUser(BaseModel):
    name: str

app = FastAPI()



@app.get("/")
async def root(start: int = 0, limit: int = 10):
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

@app.get("/post/{post_id}")
async def get_post(post_id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    post = session.query(Post).get(post_id)

    # close the session
    session.close()
    return post

@app.post("/post", status_code=status.HTTP_201_CREATED)
async def create_post(post: createPost):
    # get current user
    user_id = 0
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the medleysmdb database model
    medleysmdb = Post(
        content = post.content,
        parent_post = post.parent_post,
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

@app.put("/post/{post_id}")
async def update_post(post_id: int):
    return "update post"

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    user = session.query(Users).get(user_id)

    # close the session
    session.close()
    return user

@app.get("/users")
async def users():
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    users = session.query(Users).all()

    # close the session
    session.close()
    return users

@app.post("/user")
async def create_user(user: createUser):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # create an instance of the medleysmdb database model
    medleysmdb = Users(
        name = user.name
    )

    # add it to the session and commit it
    session.add(medleysmdb)
    session.commit()

    # grab the id given to the object from the database
    id = medleysmdb.id

    # close the session
    session.close()

    return f"create user {id}"
