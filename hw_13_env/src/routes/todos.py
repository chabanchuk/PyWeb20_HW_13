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
    The get_todos function is used to retrieve a list of Todo objects from the database.
    
    :param limit: int: Get the limit of results to be returned
    :param ge: Specify the minimum value of the parameter
    :param le: Limit the maximum number of results that can be returned
    :param offset: int: Specify the offset of the results
    :param ge: Specify that the value must be greater than or equal to a given value
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of todoresponse objects
    :doc-author: Trelent
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
    The get_all_todos function is used to get a list of all the Todo objects in the database.
    
    :param limit: int: Limit the number of results returned by the function
    :param ge: Specify the minimum value that is allowed for this parameter
    :param le: Limit the number of results returned
    :param offset: int: Specify the offset of the results
    :param ge: Set a minimum value for the parameter
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of todoresponse objects
    :doc-author: Trelent
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
    The get_todo function is used to retrieve a specific Todo object from the database.
    
    :param todo_id: int: Specify the type of data that is expected in the url path
    :param db: AsyncSession: Pass a database session to the function
    :param user: User: Get the current user
    :return: A todoresponse object
    :doc-author: Trelent
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
    The update_todo function updates an existing todo by its identifier.
    
    :param todo_id: int: Specify the id of the todo that you want to update
    :param body: TodoUpdateSchema: Pass the updated data to the function
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A todoresponse object
    :doc-author: Trelent
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
    The delete_todo function deletes a todo by its id.
    
    :param todo_id: int: Specify the type of parameter that will be passed to the function
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: None, but the response type is not none
    :doc-author: Trelent
    """
    try:
        await repositories_todos.delete_todo(todo_id, db, user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
