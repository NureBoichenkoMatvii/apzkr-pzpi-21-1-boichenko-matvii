from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.analytics.router import analytics_router
from api.backup.router import backup_router
from api.general.router import general_router
from api.machines.router import machines_router
from api.medicines.router import medicines_router
from api.mqtt.router import mqtt_router
from api.orders.router import orders_router
from api.pickup_points.router import pickup_points_router
from api.users.router import auth_router
from api.users.router import users_router
from config import settings
from database import db
from database import models
from database.models import User
from dependencies.localisation import get_accept_language
from dependencies.user import current_active_user
from logger import Logger

api = APIRouter(prefix=settings.API_V1_STR,
                dependencies=[Depends(get_accept_language)])

api.include_router(backup_router)
api.include_router(users_router)
api.include_router(auth_router)
api.include_router(machines_router)
api.include_router(medicines_router)
api.include_router(orders_router)
api.include_router(analytics_router)
api.include_router(mqtt_router)
api.include_router(general_router)
api.include_router(pickup_points_router)


@api.get("/test")
async def test(session: AsyncSession = Depends(db.get_session)):
    print(await models.User.get_all(session))
    Logger.debug("Log Test API Success")
    return "Test API Success"


@api.get("/test-auth")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
