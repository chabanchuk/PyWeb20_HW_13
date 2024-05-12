from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function is used to retrieve a user from the database by their email address.
    
    :param email: str: Specify the email of the user to be searched for
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object or none if not found
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.
    
    :param body: UserSchema: Specify the schema of the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: An object of type user
    :doc-author: Trelent
    """
    avatar = None
    try:
        # Спробуємо отримати аватар користувача з Gravatar
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        # Обробка конкретних помилок, які можуть статися при роботі з Gravatar
        raise HTTPException(status_code=500, detail="Error getting avatar")

    new_user = User(**body.model_dump(), avatar=avatar)
    try:
        # Додаємо нового користувача до бази даних
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        # Обробка конфліктів унікальності (наприклад, дублікат електронної адреси)
        raise HTTPException(status_code=400, detail="Email already registered")


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the user's access token in the database.
    
    :param user: User: Pass the user object to the function
    :param token: str | None: Pass the new token to the function
    :param db: AsyncSession: Update the database
    :return: Nothing
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirm_email(email: str, db: AsyncSession):
    """
    The confirm_email function confirms the user's email address in the database.
    
    :param email: str: Pass the email of the user to be confirmed
    :param db: AsyncSession: Pass the database session object to the function
    :return: Nothing
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()
    else:
        # Викидаємо виключення HTTPException з кодом 404, якщо користувач не знайдений
        raise HTTPException(status_code=404, detail="User not found")
