import unittest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import NoResultFound, SQLAlchemyError

from src.entity.models import Todo, User
from src.schemas.todo import TodoSchema, TodoUpdateSchema
from src.repository import todos as repositories_todos


class TestTodosRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        """
        The setUp function is called before each test function.
        It creates a mock database session and a user object to be used in the tests.
        
        :param self: Represent the instance of the class
        :return: An object of type todo
        :doc-author: Trelent
        """
        self.db_session = MagicMock()
        self.user = User(id=1, email="test@example.com")
        self.todo = Todo(id=1, title="Test Todo", user=self.user)

    async def test_get_todos(self):
        """
        The test_get_todos function tests the get_todos function in repositories/todos.py
        	The test_get_todos function is a coroutine, so it must be awaited.
        	The test_get_todos function uses MagicMock to mock the return value of db session execute and scalars all.
        	This allows us to simulate what would happen if we were actually querying our database for data, without having to actually query our database for data (which would slow down testing). 
        
        :param self: Represent the instance of the object
        :return: A list of todos
        :doc-author: Trelent
        """
        todos_mock = MagicMock()
        todos_mock.scalars.return_value.all.return_value = [self.todo]
        self.db_session.execute = AsyncMock(return_value=todos_mock)
        todos = await repositories_todos.get_todos(10, 0, self.db_session, self.user)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "Test Todo")
        
    async def test_get_all_todos(self):
        """
        The test_get_all_todos function tests the get_all_todos function in repositories/todos.py
        The test ensures that the correct number of todos are returned, and that they have the correct title
  
        :param self: Access the class attributes and methods
        :return: A list of todos
        :doc-author: Trelent
        """
        todos_mock = MagicMock()
        todos_mock.scalars.return_value.all.return_value = [self.todo]
        self.db_session.execute = AsyncMock(return_value=todos_mock)	
        todos = await repositories_todos.get_all_todos(10, 0, self.db_session)
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "Test Todo")

    async def test_get_todo(self):
        self.db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=self.todo)))
        todo = await repositories_todos.get_todo(1, self.db_session, self.user)
        self.assertEqual(todo.title, "Test Todo")

    async def test_create_todo(self):
        todo_data = TodoSchema(title="New Todo", description="New Todo Description", completed=False)
        self.db_session.add = MagicMock()
        self.db_session.commit = AsyncMock()
        self.db_session.refresh = AsyncMock()
        todo = await repositories_todos.create_todo(todo_data, self.db_session, self.user)
        self.assertEqual(todo.title, "New Todo")

    async def test_update_todo(self):
        update_data = TodoUpdateSchema(title="Updated Todo", description="Updated Todo Description", completed=True)
        self.db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=self.todo)))
        self.db_session.commit = AsyncMock()
        self.db_session.refresh = AsyncMock()
        todo = await repositories_todos.update_todo(1, update_data, self.db_session, self.user)
        self.assertEqual(todo.title, "Updated Todo")

    async def test_delete_todo(self):
        self.db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=self.todo)))
        self.db_session.delete = MagicMock()
        self.db_session.commit = AsyncMock()
        todo = await repositories_todos.delete_todo(1, self.db_session, self.user)
        self.assertEqual(todo.title, "Test Todo")


if __name__ == "__main__":
    unittest.main()