from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from src.entity.models import Todo, User
from src.schemas.todo import TodoSchema, TodoUpdateSchema


async def get_todos(limit: int, offset: int, db: AsyncSession, user: User):
    """
    Отримати список завдань (todos) для конкретного користувача з бази даних.

    Args:
        limit (int): Максимальна кількість елементів для отримання.
        offset (int): Зміщення від початку списку.
        db (AsyncSession): Об'єкт сесії бази даних.
        user (User): Об'єкт користувача, для якого шукаються завдання.

    Returns:
        list[Todo]: Список завдань (todos) користувача.

    Raises:
        NoResultFound: Якщо не знайдено жодного результату.
        SQLAlchemyError: Помилка бази даних.
    """
    try:
        stmt = select(Todo).filter_by(user=user).offset(offset).limit(limit)
        todos = await db.execute(stmt)
        return todos.scalars().all()
    except NoResultFound:
        return []
    except SQLAlchemyError as e:
        raise e


async def get_all_todos(limit: int, offset: int, db: AsyncSession):
    """
    Отримати список всіх завдань (todos) з бази даних.

    Args:
        limit (int): Максимальна кількість елементів для отримання.
        offset (int): Зміщення від початку списку.
        db (AsyncSession): Об'єкт сесії бази даних.

    Returns:
        list[Todo]: Список всіх завдань (todos).

    Raises:
        NoResultFound: Якщо не знайдено жодного результату.
        SQLAlchemyError: Помилка бази даних.
    """
    try:
        stmt = select(Todo).offset(offset).limit(limit)
        todos = await db.execute(stmt)
        return todos.scalars().all()
    except NoResultFound:
        return []
    except SQLAlchemyError as e:
        raise e


async def get_todo(todo_id: int, db: AsyncSession, user: User):
    """
    Отримати конкретне завдання (todo) з бази даних за його ідентифікатором.

    Args:
        todo_id (int): Ідентифікатор завдання (todo).
        db (AsyncSession): Об'єкт сесії бази даних.
        user (User): Об'єкт користувача, якому належить завдання.

    Returns:
        Todo | None: Об'єкт завдання (todo) або None, якщо не знайдено.

    Raises:
        NoResultFound: Якщо не знайдено жодного результату.
        SQLAlchemyError: Помилка бази даних.
    """
    try:
        stmt = select(Todo).filter_by(id=todo_id, user=user)
        todo = await db.execute(stmt)
        return todo.scalar_one_or_none()
    except NoResultFound:
        return None
    except SQLAlchemyError as e:
        raise e


async def create_todo(body: TodoSchema, db: AsyncSession, user: User):
    """
    Створити нове завдання (todo) в базі даних.

    Args:
        body (TodoSchema): Дані для створення нового завдання.
        db (AsyncSession): Об'єкт сесії бази даних.
        user (User): Об'єкт користувача, для якого створюється завдання.

    Returns:
        Todo: Нове створене завдання.

    Raises:
        SQLAlchemyError: Помилка бази даних при створенні завдання.
    """
    try:
        todo_data = body.model_dump(exclude_unset=True)
        todo = Todo(**todo_data, user=user)
        db.add(todo)
        await db.commit()
        await db.refresh(todo)
        return todo
    except SQLAlchemyError as e:
        raise e


async def update_todo(todo_id: int, body: TodoUpdateSchema, db: AsyncSession, user: User):
    """
    Оновити існуюче завдання (todo) в базі даних.

    Args:
        todo_id (int): Ідентифікатор завдання (todo) для оновлення.
        body (TodoUpdateSchema): Дані для оновлення завдання.
        db (AsyncSession): Об'єкт сесії бази даних.
        user (User): Об'єкт користувача, якому належить завдання.

    Returns:
        Todo | None: Оновлене завдання або None, якщо не знайдено.

    Raises:
        SQLAlchemyError: Помилка бази даних при оновленні завдання.
    """
    try:
        stmt = select(Todo).filter_by(id=todo_id, user=user)
        result = await db.execute(stmt)
        todo = result.scalar_one_or_none()
        if todo:
            todo.title = body.title
            todo.description = body.description
            todo.completed = body.completed
            await db.commit()
            await db.refresh(todo)
        return todo
    except SQLAlchemyError as e:
        raise e


async def delete_todo(todo_id: int, db: AsyncSession, user: User):
    """
    Видалити завдання (todo) з бази даних за його ідентифікатором.

    Args:
        todo_id (int): Ідентифікатор завдання (todo) для видалення.
        db (AsyncSession): Об'єкт сесії бази даних.
        user (User): Об'єкт користувача, якому належить завдання.

    Returns:
        Todo | None: Видалене завдання або None, якщо не знайдено.

    Raises:
        SQLAlchemyError: Помилка бази даних при видаленні завдання.
    """
    try:
        stmt = select(Todo).filter_by(id=todo_id, user=user)
        todo = await db.execute(stmt)
        todo = todo.scalar_one_or_none()
        if todo:
            db.delete(todo)
            await db.commit()
        return todo
    except SQLAlchemyError as e:
        raise e

