import uuid
from typing_extensions import override

from fastapi_users import UUIDIDMixin, BaseUserManager
from fastapi import Request
from database.models import User
from config import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.PASSWORD_TOKEN_SECRET
    verification_token_secret = settings.VERIFICATION_TOKEN_SECRET

    @override
    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    @override
    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    @override
    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
