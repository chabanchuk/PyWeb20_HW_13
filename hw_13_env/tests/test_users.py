import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository import users as users_repository


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.user_data = UserSchema(username="testuser", email="test@example.com", password="password")
        self.user = User(id=1, username="testuser", email="test@example.com", password="password")

    async def test_get_user_by_email(self):
        self.db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=self.user)))
        user = await users_repository.get_user_by_email("test@example.com", self.db_session)
        self.assertEqual(user.email, "test@example.com")

    async def test_create_user(self):
        self.db_session.add = MagicMock()
        self.db_session.commit = AsyncMock()
        self.db_session.refresh = AsyncMock()
        with patch("libgravatar.Gravatar.get_image", return_value="avatar_url"):
            user = await users_repository.create_user(self.user_data, self.db_session)
            self.assertEqual(user.email, "test@example.com")

    async def test_create_user_integrity_error(self):
        self.db_session.add = MagicMock(side_effect=IntegrityError("", "", ""))
        with self.assertRaises(HTTPException) as context:
            await users_repository.create_user(self.user_data, self.db_session)
        self.assertEqual(context.exception.status_code, 400)

    async def test_update_token(self):
        self.db_session.commit = AsyncMock()
        await users_repository.update_token(self.user, "new_token", self.db_session)
        self.assertEqual(self.user.refresh_token, "new_token")

    async def test_confirm_email(self):
        self.db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=self.user)))
        self.db_session.commit = AsyncMock()
        await users_repository.confirm_email("test@example.com", self.db_session)
        self.assertTrue(self.user.confirmed)

    async def test_confirm_email_not_found(self):
        self.db_session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
        with self.assertRaises(HTTPException) as context:
            await users_repository.confirm_email("test@example.com", self.db_session)
        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()