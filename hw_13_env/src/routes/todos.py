from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User, Role
from src.repository import todos as repositories_todos
from src.schemas.todo import TodoSchema, TodoUpdateSchema, TodoResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/todos', tags=['todos'])

access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/", response_model=list[TodoResponse])
async def get_todos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                    db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Отримати список завдань користувача з обмеженням і зміщенням.

    Args:
        limit (int): Кількість результатів на сторінці.
        offset (int): Зміщення результатів.
        db (AsyncSession): Сесія бази даних.
        user (User): Поточний користувач.

    Returns:
        list[TodoResponse]: Список об'єктів завдань.

    Raises:
        HTTPException: Помилка HTTP при порожньому списку завдань.
    """
    try:
        todos = await repositories_todos.get_todos(limit, offset, db, user)
        return todos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/all", response_model=list[TodoResponse], dependencies=[Depends(access_to_route_all)])
async def get_all_todos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Отримати список всіх завдань з обмеженням і зміщенням для адміністраторів та модераторів.

    Args:
        limit (int): Кількість результатів на сторінці.
        offset (int): Зміщення результатів.
        db (AsyncSession): Сесія бази даних.
        user (User): Поточний користувач.

    Returns:
        list[TodoResponse]: Список всіх об'єктів завдань.

    Raises:
        HTTPException: Помилка HTTP при порожньому списку завдань або доступі.
    """
    try:
        todos = await repositories_todos.get_all_todos(limit, offset, db)
        return todos
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(todo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                   user: User = Depends(auth_service.get_current_user)):
    """
    Отримати конкретне завдання за його ідентифікатором.

    Args:
        todo_id (int): Ідентифікатор завдання.
        db (AsyncSession): Сесія бази даних.
        user (User): Поточний користувач.

    Returns:
        TodoResponse: Об'єкт конкретного завдання.

    Raises:
        HTTPException: Помилка HTTP при неуспішному пошуку завдання.
    """
    try:
        todo = await repositories_todos.get_todo(todo_id, db, user)
        if todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
        return todo
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.post("/", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(body: TodoSchema, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    todo = await repositories_todos.create_todo(body, db, user)
    return todo


@router.put("/{todo_id}")
async def update_todo(todo_id: int, body: TodoUpdateSchema, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    # код

    """
    Оновити існуюче завдання за його ідентифікатором.

    Args:
        todo_id (int): Ідентифікатор завдання, яке потрібно оновити.
        body (TodoUpdateSchema): Об'єкт з оновленими даними для завдання.
        db (AsyncSession): Сесія бази даних.
        user (User): Поточний користувач.

    Returns:
        TodoResponse: Оновлений об'єкт завдання.

    Raises:
        HTTPException: Помилка HTTP при неуспішному оновленні або знайденої помилці.
    """
    try:
        todo = await repositories_todos.update_todo(todo_id, body, db, user)
        if todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
        return todo
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    Видалити існуюче завдання за його ідентифікатором.

    Args:
        todo_id (int): Ідентифікатор завдання, яке потрібно видалити.
        db (AsyncSession): Сесія бази даних.
        user (User): Поточний користувач.

    Raises:
        HTTPException: Помилка HTTP при неуспішному видаленні або знайденої помилці.
    """
    try:
        await repositories_todos.delete_todo(todo_id, db, user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
