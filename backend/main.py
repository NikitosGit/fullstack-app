import random
from typing import List, Optional, Union, Annotated
from faker import Faker
from faker.providers import DynamicProvider
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from fastapi import FastAPI
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#"$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        #пароль - secret
        "hashed_password": "$2a$12$IWdSg11/D4dBbrDxU8R7O.n6QvgSsGW5YrIuoHvr2LG1KVaXSRB7m",
        "disabled": False,
    },
    "admin" : {
        "username": "admin",
        "full_name": "admin",
        "email": "admin@example.com",
        #пароль - admin
        "hashed_password": "$2a$10$YyDxlxIUKH/.Y8kvyRJ8gOfM6nDmxzNN6f38uOHjSPrKKf6cCb1su",
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    print("get_user")
    if username in db:
        user_dict = db[username]
        print(user_dict)
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

abilities_provider = DynamicProvider(
    provider_name = "abilities",
    elements = ["Java", "Python", "C++", "JS", "Angular", "React", "Django", "TypeScript"])

class Item(BaseModel):
    id: int = None
    userName: str = None
    firstName: str = None
    lastName: str = None
    abilities: Optional[list] = None
    description: str = None
    avatarUrl: str = None
  
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake = Faker()
fake.add_provider(abilities_provider)

# OAuth2PasswordRequestForm — это класс из FastAPI, который представляет форму запроса на аутентификацию, 
# включающую поля username и password.
# Depends() — это функция из FastAPI, которая указывает, что значение параметра form_data должно быть получено из запроса.

@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    print("login")
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user



# при каждом вызове функции будет вызываться get_current_active_user
# Annotated[User, Depends(get_current_active_user)] указывает, 
# что параметр current_user будет иметь тип User и его значение будет получено с помощью функции get_current_active_user.

@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/")
def read_root():
    return {"Hello": "World asdasd"}


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, current_user: Annotated[User, Depends(get_current_active_user)],):
    item = Item()
    item.id = item_id
    item.firstName = fake.first_name()
    item.lastName = fake.last_name()
    item.userName = fake.email()
    # set нужен чтобы убрать дубликаты, а потом все заворачиваем в list
    item.abilities = list(set([fake.abilities() for i in range(random.randrange(1,6))]))
    item.description = fake.text()
    
    return item

@app.get("/items/", response_model=List[Item])
async def get_items( #current_user: Annotated[User, Depends(get_current_active_user)],
):
    
    resp = []
 
    for i in range(1, 6):
        item = Item()
        item.id = fake.random_int()
        item.firstName = fake.first_name()
        item.lastName = fake.last_name()
        item.userName = fake.email()
        # set нужен чтобы убрать дубликаты, а потом все заворачиваем в list
        item.abilities = list(set([fake.abilities() for i in range(random.randrange(1,6))]))
        item.description = fake.text()
        item.avatarUrl = "https://api.multiavatar.com/" + str(item.id) + ".svg"
        resp.append(item)
    return resp     