from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf import config


class Auth:
    # Ініціалізація криптографічного контексту
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        The verify_password function takes a plain-text password and a hashed password,
        and returns True if the passwords match, False otherwise. The verify_password function
        uses the pwd_context object to hash the plain-text password and compare it with 
        the hashed one.
        
        :param self: Represent the instance of the class
        :param plain_password: Pass the password that is entered by the user
        :param hashed_password: Compare the password that is stored in the database with the one provided by a user
        :return: True if the password is correct and false if it is not
        :doc-author: Trelent
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function hashes the password using the pwd_context.hash method.
        
        :param self: Represent the instance of the class
        :param password: str: Specify the password that will be hashed
        :return: A hash of the password
        :doc-author: Trelent
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_access_token function generates an access token.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The time in seconds until the token expires. Defaults to 15 minutes if not specified.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A token that is encoded with the user's data
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        The create_refresh_token function generates a refresh token.
            Args:
                data (dict): A dictionary containing the user's id and username.
                expires_delta (Optional[float]): The number of seconds until the refresh token expires. Defaults to None, which sets it to 7 days from now.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the user's id to the function
        :param expires_delta: Optional[float]: Specify the time of expiration
        :return: An encoded refresh token
        :doc-author: Trelent
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function decodes the refresh token and returns the email of the user.
            If it fails to decode, it raises an HTTPException with a 401 status code.
        
        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(refresh_token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        The get_current_user function is a dependency that returns the current user.
        It uses the token from the Authorization header to decode it and get its payload,
        which contains information about who made this request. It then gets that user's data from our database.
        
        :param self: Represent the instance of a class
        :param token: str: Pass the token to the function
        :param db: AsyncSession: Get the database connection
        :return: The user object
        :doc-author: Trelent
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[config.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        The create_email_token function generates a token for confirming an email.
            Args:
                data (dict): A dictionary containing the user's id and email address.
        
        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the token
        :return: A token that contains a dictionary with the following keys:
        :doc-author: Trelent
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=1)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        If the token is invalid, it raises an HTTPException.
        
        :param self: Represent the instance of the class
        :param token: str: Pass the token to the function
        :return: The email address from the token
        :doc-author: Trelent
        """
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            # Обробка неправильного токену
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


# Створення екземпляру Auth для використання в програмі
auth_service = Auth()
