import os
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from services.get import GetValues
from fastapi.security import OAuth2PasswordBearer

load_dotenv()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=os.getenv('ACCESS_TOKEN_EXPIRE_HOURSACCESS_TOKEN_EXPIRE_HOURS'))

    to_encode.update({"exp":{expire}})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    values : GetValues = Depends(GetValues)
):
    credentials_exeption = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED, 
        detail="Could not validate credentials", 
        headers={"WWW-Autenticate" : "Bearer"}, 
    )

    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])

        email : str = payload.get("sub")

        if email is None:
            raise credentials_exeption
    except JWTError:
        raise credentials_exeption
    
    user_id = values.get_user_id(email)
    if user_id is None: 
        raise credentials_exeption
    
    user = {"email" : email, "id" : user_id}

    return user