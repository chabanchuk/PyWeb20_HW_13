from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from src.entity.models import Todo, User
from src.schemas.todo import TodoSchema, TodoUpdateSchema


async def get_todos(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_todos function returns a list of todos for the specified user.
    
    :param limit: int: Limit the number of results returned
    :param offset: int: Specify the offset from the beginning of the list
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the todos by user
    :return: A list of todo objects
    :doc-author: Trelent
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
    The get_all_todos function returns a list of all todos in the database.
    
    :param limit: int: Limit the number of results returned from the database
    :param offset: int: Specify the number of records to skip before returning results
    :param db: AsyncSession: Pass the database session object to the function
    :return: A list of todo objects
    :doc-author: Trelent
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
    The get_todo function retrieves a single todo from the database.
    
    :param todo_id: int: Pass the id of the todo we want to get from the database
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is only able to access their own data
    :return: A todo object or none, if the todo is not found
    :doc-author: Trelent
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
    The create_todo function creates a new todo in the database.
    
    :param body: TodoSchema: Get the data from the request body
    :param db: AsyncSession: Pass the database session object to the function
    :param user: User: Pass the user object to the function
    :return: A todo object
    :doc-author: Trelent
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
    The update_todo function updates an existing todo in the database.
    
    :param todo_id: int: Identify the todo that needs to be updated
    :param body: TodoUpdateSchema: Pass the data for updating a todo
    :param db: AsyncSession: Pass a database session to the function
    :param user: User: Check if the user is authorized to update a particular todo
    :return: A todo object
    :doc-author: Trelent
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
    The delete_todo function deletes a todo from the database by its id.
    
    :param todo_id: int: Specify the id of the todo that is going to be deleted
    :param db: AsyncSession: Pass the database session object to the function
    :param user: User: Ensure that the user is deleting their own todo
    :return: The deleted todo or none if it is not found
    :doc-author: Trelent
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
