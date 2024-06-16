from fastapi import APIRouter

from api.users.schemas import UserResponse, UserCreate, UserUpdate
from dependencies.user import fastapi_users, auth_backend

auth_router = APIRouter(prefix="/auth", tags=["auth"])
auth_router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt")
auth_router.include_router(fastapi_users.get_reset_password_router())
auth_router.include_router(fastapi_users.get_register_router(UserResponse, UserCreate))
auth_router.include_router(fastapi_users.get_verify_router(UserResponse))

users_router = APIRouter(prefix="/users", tags=["users"])
users_router.include_router(fastapi_users.get_users_router(UserResponse, UserUpdate))
