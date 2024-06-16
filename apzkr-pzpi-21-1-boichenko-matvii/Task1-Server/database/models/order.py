from __future__ import annotations
import uuid
from datetime import datetime
from enum import IntEnum, StrEnum

from sqlalchemy import Column
from sqlalchemy.orm import Relationship
from sqlalchemy.orm import WriteOnlyMapped

from common.enums.tables import PostgresTables
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, ForeignKey, Float, func, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import mapped_column, Mapped, relationship
from pydantic import BaseModel as PydanticBase
from . import DbBaseModel, Currencies
from . import Machine


class PaymentInfo(PydanticBase):
    amount: float
    currency: str = Currencies.eur
    payed_at: datetime | None = None


class OrderStatus(IntEnum):
    created = 0
    payed = 1
    # preoder means no availability on current machines,
    # needs to be confirmed manually by deliverer
    preorder = 2
    in_delivery = 3
    completed = 4
    canceled = 5
    failed = 6


class Order(DbBaseModel):
    __tablename__ = PostgresTables.ORDER

    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("machine.id", ondelete="SET NULL"), nullable=True)
    pickup_point_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("pickup_point.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Integer, nullable=False)
    payment_amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_currency: Mapped[str] = mapped_column(String(30), nullable=False, default=Currencies.eur)
    payment_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="orders", lazy="selectin")
    machine: Mapped[Machine] = relationship(Machine, back_populates="orders", lazy="selectin")
    pickup_point = relationship("PickupPoint", back_populates="orders", lazy="selectin")
    order_medicines: WriteOnlyMapped[OrderMedicine] = relationship("OrderMedicine", back_populates="order")


class OrderMedicine(DbBaseModel):
    __tablename__ = PostgresTables.ORDER_MEDICINE

    order_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    medicine_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("medicine.id", ondelete="CASCADE"), nullable=False)
    medicine_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    medicine = relationship("Medicine", back_populates="order_medicines", lazy="selectin")
    order = relationship(Order, back_populates="order_medicines", lazy="selectin")


