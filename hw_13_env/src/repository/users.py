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
    Отримати користувача за електронною адресою з бази даних.

    Args:
        email (str): Електронна адреса користувача.

    Returns:
        User | None: Знайдений користувач або None, якщо не знайдено.
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Створити нового користувача в базі даних.

    Args:
        body (UserSchema): Дані нового користувача.
        db (AsyncSession, optional): Об'єкт сесії бази даних. Defaults to Depends(get_db).

    Returns:
        User: Новостворений користувач.
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
    Оновити токен доступу користувача в базі даних.

    Args:
        user (User): Об'єкт користувача.
        token (str | None): Новий токен доступу або None.
        db (AsyncSession): Об'єкт сесії бази даних.
    """
    user.refresh_token = token
    await db.commit()


async def confirm_email(email: str, db: AsyncSession):
    """
    Підтвердити електронну адресу користувача в базі даних.

    Args:
        email (str): Електронна адреса користувача.
        db (AsyncSession): Об'єкт сесії бази даних.

    Raises:
        HTTPException: Якщо користувач не знайдений.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()
    else:
        # Викидаємо виключення HTTPException з кодом 404, якщо користувач не знайдений
        raise HTTPException(status_code=404, detail="User not found")
