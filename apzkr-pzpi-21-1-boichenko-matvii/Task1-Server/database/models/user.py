from datetime import datetime
from enum import IntEnum

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from common.enums.tables import PostgresTables
from .base import DbBaseModel


class UserRole(IntEnum):
    customer = 1
    deliverer = 2
    admin = 3


class User(DbBaseModel, SQLAlchemyBaseUserTableUUID):
    __tablename__ = PostgresTables.USER

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birthdate: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    role: Mapped[UserRole] = mapped_column(Integer, nullable=False, default=UserRole.customer)
    # Relationships
    orders = relationship("Order", back_populates="user")
    machines = relationship("Machine", back_populates="admin")
