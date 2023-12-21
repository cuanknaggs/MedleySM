from datetime import datetime, timedelta
import json 

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import BaseModel

# dont hard code secrets
SECRET_KEY = "65ad7bdd39f2fca35a542897f92202573ed7b7a808174f1b400eb181f5f4ce57"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    name: str | None = None

class User(BaseModel):
    name: str
    moderator: bool | None = None

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
    has_comments = Column(Boolean)
    fact_check = Column(Integer)
    user_name = Column(String(256))
    user_id = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=True)
    passwordHashed = Column(String)
    moderator = Column(Boolean)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class Likes(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    post_id = Column(Integer)

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

class createLike(BaseModel):
    user_id: int
    post_id: int

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user_by_name(name: str):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    user = session.query(Users).where(Users.name == name).first()

    # close the session
    session.close()

    return user

async def authenticate_user(name: str, password: str):
    user = await get_user_by_name(name)
    if not user:
        return False
    if not verify_password(password, user.passwordHashed):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise credentials_exception
        token_data = TokenData(name=name)
    except JWTError:
        raise credentials_exception
    user = await get_user_by_name(name=token_data.name)
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/posts")
async def posts():
    '''
    return a list of posts
    '''
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    posts = session.query(Post).order_by(Post.created_at.desc()).all()

    # close the session
    session.close()
    return posts

@app.get("/api/posts/{user_name}")
async def posts_by_user(user_name: str):
    '''
    return a list of posts for a user
    '''
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    posts = session.query(Post).where(Post.user_name==user_name).order_by(Post.created_at.desc()).all()

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

@app.get("/api/post/{post_id}/comments")
async def get_post(post_id: int):
    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the comment posts by parent post id
    posts = session.query(Post).where(Post.parent_post==post_id).order_by(Post.created_at.desc()).all()

    # close the session
    session.close()
    return posts

@app.post("/api/post", status_code=status.HTTP_201_CREATED)
async def create_post(post: createPost, current_user: User = Depends(get_current_active_user)):
    # get current user
    user = await get_user_by_name(current_user.name)

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    if post.parent_post > -1:
        parent_post = session.query(Post).get(post.parent_post)
        parent_post.has_comments = True

    # create an instance of the medleysmdb database model
    medleysmdb = Post(
        content = post.content,
        parent_post = post.parent_post,
        user_name = user.name,
        user_id = user.id
    )

    # add it to the session and commit it
    session.add(medleysmdb)
    session.commit()

    # grab the id given to the object from the database
    id = medleysmdb.id

    # close the session
    session.close()

    return f"create post {id}"

@app.put("/api/post/{post_id}/like")
async def like_post(post_id: int, current_user: User = Depends(get_current_active_user)):
    # get current user
    user = await get_user_by_name(current_user.name)

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    post = session.query(Post).get(post_id)
    post_likes = session.query(Likes).filter(Likes.post_id == post_id, Likes.user_id == user.id).count()

    # test post exists
    if post and post_likes == 0 and post.user_id != user.id:
        # test if user has already liked post
        medleysmdb = Likes(
            user_id = user.id,
            post_id = post_id
        )
        session.add(medleysmdb)

        likes = post_likes + 1
        post.likes = likes

        session.commit()
    else:
        if post_likes != 0:
            raise HTTPException(status_code=401, detail=f"User already liked post")
        elif post.user_id == user.id:
            raise HTTPException(status_code=401, detail=f"User owns post")
        else:
            raise HTTPException(status_code=404, detail=f"Post not found")

    # close the session
    session.close()

    # return post.likes
    return "update post"

@app.put("/api/post/{post_id}/isFake")
async def is_fake_post(post_id: int, current_user: User = Depends(get_current_active_user)):
    # get current user
    user = await get_user_by_name(current_user.name)

    # create a new database session
    session = Session(bind=engine, expire_on_commit=False)

    # get the post item with the given id
    post = session.query(Post).get(post_id)

    # test post exists
    if post:
        post.fact_check = True

        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"Post not found")

    # close the session
    session.close()

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
    passwordHash = get_password_hash(user.password)

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

@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me/")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    data = {
        "status": "ok",
        "userName": current_user.name,
        "moderator": current_user.moderator
    }
    return data
