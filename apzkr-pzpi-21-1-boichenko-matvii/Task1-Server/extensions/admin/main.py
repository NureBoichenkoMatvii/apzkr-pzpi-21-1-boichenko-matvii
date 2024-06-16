from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.applications import Starlette
from starlette.requests import Request

from config import settings
from database import db
from database import models
from database.managers import UserManager
from extensions.admin.views import MachinePickupPointView
from extensions.admin.views import OrderMedicineView
from extensions.admin.views import PickupPointView

admin: Admin = None


class AdminAuthBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        try:
            async with db.create_async_session() as session:
                user_manager = UserManager(SQLAlchemyUserDatabase(session, models.User))
                user = await user_manager.get_by_email(email)
                print("user", user)
                res: bool = user_manager.password_helper.verify_and_update(password, user.hashed_password)[0]
                res &= user.is_superuser
                request.session.update({"token": user.hashed_password})

            return res
        except BaseException as e:
            print('Admin auth error', e)
            return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return bool(token)


def init_admin(app: Starlette):
    from database import db
    global admin
    admin = Admin(app, db.sync_engine, session_maker=db.create_sync_session,
                  authentication_backend=AdminAuthBackend(settings.JWT_SECRET))

    from .views import UserView, MachineView, MachineMedicineSlotView, MachineStatisticView, OrderView, MedicineView, \
        StatisticsAdmin
    admin.add_view(UserView)
    admin.add_view(MachineView)
    admin.add_view(MachineMedicineSlotView)
    admin.add_view(MachineStatisticView)
    admin.add_view(MachinePickupPointView)
    admin.add_view(MedicineView)
    admin.add_view(OrderView)
    admin.add_view(OrderMedicineView)
    admin.add_view(PickupPointView)

    # admin.add_view(StatisticsAdmin)
