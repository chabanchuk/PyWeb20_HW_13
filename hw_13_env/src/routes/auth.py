from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.repository import users as repositories_users
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Реєстрація нового користувача.

    Args:
        body (UserSchema): Дані нового користувача.
        bt (BackgroundTasks): Об'єкт для виконання фонових завдань.
        request (Request): Об'єкт HTTP запиту.
        db (AsyncSession): Сесія бази даних.

    Returns:
        UserResponse: Інформація про нового користувача.

    Raises:
        HTTPException: Помилка HTTP при конфлікті акаунта або невалідних даних.
    """
    try:
        exist_user = await repositories_users.get_user_by_email(body.email, db)
        if exist_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

        body.password = auth_service.get_password_hash(body.password)
        new_user = await repositories_users.create_user(body, db)
        bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
        return new_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Аутентифікація користувача.

    Args:
        body (OAuth2PasswordRequestForm): Дані для входу.
        db (AsyncSession): Сесія бази даних.

    Returns:
        TokenSchema: Токени доступу та оновлення.

    Raises:
        HTTPException: Помилка HTTP при невалідних даних.
    """
    try:
        user = await repositories_users.get_user_by_email(body.username, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
        if not user.confirmed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
        if not auth_service.verify_password(body.password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "Сергій Багмет"})
        refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
        await repositories_users.update_token(user, refresh_token, db)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Оновлення токена доступу.

    Args:
        credentials (HTTPAuthorizationCredentials): Креденціали доступу.
        db (AsyncSession): Сесія бази даних.

    Returns:
        TokenSchema: Оновлені токени.

    Raises:
        HTTPException: Помилка HTTP при невалідних даних.
    """
    try:
        token = credentials.credentials
        email = await auth_service.decode_refresh_token(token)
        user = await repositories_users.get_user_by_email(email, db)
        if user.refresh_token != token:
            await repositories_users.update_token(user, None, db)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        access_token = await auth_service.create_access_token(data={"sub": email})
        refresh_token = await auth_service.create_refresh_token(data={"sub": email})
        await repositories_users.update_token(user, refresh_token, db)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Підтвердження електронної пошти.

    Args:
        token (str): Токен для підтвердження.
        db (AsyncSession): Сесія бази даних.

    Returns:
        dict: Результат підтвердження.

    Raises:
        HTTPException: Помилка HTTP при невалідних даних.
    """
    try:
        email = await auth_service.get_email_from_token(token)
        user = await repositories_users.get_user_by_email(email, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        await repositories_users.confirmed_email(email, db)
        return {"message": "Email confirmed"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Відправлення запиту на підтвердження електронної пошти.

    Args:
        body (RequestEmail): Дані для запиту.
        background_tasks (BackgroundTasks): Об'єкт для виконання фонових завдань.
        request (Request): Об'єкт HTTP запиту.
        db (AsyncSession): Сесія бази даних.

    Returns:
        dict: Результат операції.

    Raises:
        HTTPException: Помилка HTTP при невалідних даних.
    """
    try:
        user = await repositories_users.get_user_by_email(body.email, db)
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        if user:
            background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
        return {"message": "Check your email for confirmation."}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get('/{username}')
async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Отримання зображення для підтвердження відкриття email.

    Args:
        username (str): Ім'я користувача.
        response (Response): Об'єкт HTTP відповіді.
        db (AsyncSession): Сесія бази даних.

    Returns:
        FileResponse: Зображення.

    Raises:
        HTTPException: Помилка HTTP при невалідних даних.
    """
    try:
        print('--------------------------------')
        print(f'{username} зберігаємо що він відкрив email в БД')
        print('--------------------------------')
        return FileResponse("src/static/test_image.png", media_type="image/png", content_disposition_type="inline")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
