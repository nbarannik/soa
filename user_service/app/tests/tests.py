import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from jose import jwt
from app.routes.dependencies import create_access_token, get_token, get_current_user
from app.routes.config import settings

class TestDependencies(unittest.TestCase):
    def setUp(self):
        self.user_id = "123"
        self.token = "fake_token"
        self.expire = datetime.utcnow() + timedelta(minutes=30)
        self.payload = {"sub": self.user_id, "exp": self.expire}

    def test_get_token_success(self):
        mock_request = MagicMock()
        mock_request.cookies.get.return_value = self.token
        token = get_token(mock_request)
        self.assertEqual(token, self.token)

    def test_get_token_fail(self):
        mock_request = MagicMock()
        mock_request.cookies.get.return_value = None
        with self.assertRaises(HTTPException) as context:
            get_token(mock_request)
        self.assertEqual(context.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(context.exception.detail, "Token not found")

    @patch("dependencies.jwt.decode")
    @patch("dependencies.crud.get_user_by_id")
    async def test_get_current_user_success(self, mock_get_user_by_id, mock_jwt_decode):
        mock_jwt_decode.return_value = self.payload
        mock_get_user_by_id.return_value = {"id": self.user_id, "username": "test_user"}

        user = await get_current_user(self.token)
        self.assertEqual(user["id"], self.user_id)
        self.assertEqual(user["username"], "test_user")

    @patch("dependencies.jwt.decode")
    async def test_get_current_user_invalid_token(self, mock_jwt_decode):
        mock_jwt_decode.side_effect = jwt.JWTError("Invalid token")
        with self.assertRaises(HTTPException) as context:
            await get_current_user(self.token)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid or expired token")

    @patch("dependencies.jwt.decode")
    async def test_get_current_user_missing_sub(self, mock_jwt_decode):
        mock_jwt_decode.return_value = {"exp": self.expire}
        with self.assertRaises(HTTPException) as context:
            await get_current_user(self.token)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid token")

    @patch("dependencies.jwt.decode")
    @patch("dependencies.crud.get_user_by_id")
    async def test_get_current_user_not_found(self, mock_get_user_by_id, mock_jwt_decode):
        mock_jwt_decode.return_value = self.payload
        mock_get_user_by_id.return_value = None
        with self.assertRaises(HTTPException) as context:
            await get_current_user(self.token)
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")

if __name__ == "__main__":
    unittest.main()