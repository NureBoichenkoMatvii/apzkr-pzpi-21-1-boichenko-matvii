from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from enum import IntEnum, auto
from typing import Dict, Any

from pydantic import BaseModel as PydanticBase, Field, confloat
from sqlalchemy import (
    String, ForeignKey, JSON, Integer, Boolean
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import WriteOnlyMapped
from sqlalchemy.orm import relationship, mapped_column

from common.enums.tables import PostgresTables
from . import DbBaseModel


class MachineLocation(PydanticBase):
    latitude: confloat(gt=-90, lt=90) | None = (
        Field(..., description="Latitude in degrees (-90 to 90)."))
    longitude: confloat(gt=-180, lt=180) | None = (
        Field(..., description="Longitude in degrees (-180 to 180)."))

    @classmethod
    def json_encoders(cls) -> Dict[Any, Any]:
        return {Decimal: lambda v: float(v)}


class MachineStatus(IntEnum):
    unregistered = auto()
    registered = auto()
    dysfunctional = auto()  # not ready for work


class MachineScheduleStatus(IntEnum):
    in_planning = auto()
    active = auto()
    inactive = auto()


class Machine(DbBaseModel):
    __tablename__ = PostgresTables.MACHINE

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    mac: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    location: Mapped[MachineLocation] = mapped_column(JSON, nullable=False)
    admin_user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("user.id"), nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[MachineStatus] = mapped_column(Integer, nullable=False)
    last_maintenance_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    admin = relationship("User", back_populates="machines")
    machine_medicine_slots = relationship("MachineMedicineSlot", back_populates="machine", lazy="selectin")
    machine_statistics = relationship("MachineStatistic", back_populates="machine", lazy="selectin")
    machine_pickup_points: WriteOnlyMapped[MachinePickupPoint] = relationship("MachinePickupPoint", back_populates="machine", lazy="selectin")
    orders = relationship("Order", back_populates="machine")


class MachineStatistic(DbBaseModel):
    __tablename__ = PostgresTables.MACHINE_STATISTIC

    machine_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("machine.id", ondelete="CASCADE"), nullable=False)
    info: Mapped[dict] = mapped_column(JSON, nullable=False)
    # Relationships
    machine = relationship("Machine", back_populates="machine_statistics", lazy="selectin")


# Signify stops of machine on its way
class MachinePickupPoint(DbBaseModel):
    __tablename__ = PostgresTables.MACHINE_PICKUP_POINT

    machine_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("machine.id", ondelete="CASCADE"), nullable=False)
    pickup_point_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("pickup_point.id", ondelete="CASCADE"), nullable=False)
    # order of stops in machine's schedule is defined by their arrival_at date
    arrival_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    departure_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # whether user can order delivery to this stop
    deliver_orders: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    machine = relationship("Machine", back_populates="machine_pickup_points", lazy="selectin")
    pickup_point = relationship("PickupPoint", back_populates="machine_pickup_points", lazy="selectin")


class MachineMedicineSlot(DbBaseModel):
    __tablename__ = PostgresTables.MACHINE_MEDICINE_SLOT

    machine_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("machine.id", ondelete="CASCADE"), nullable=False)
    medicine_id: Mapped[uuid.UUID] = mapped_column(
        UUID, ForeignKey("medicine.id", ondelete="CASCADE"), nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # reserved by orders
    # Relationships
    machine = relationship("Machine", back_populates="machine_medicine_slots", lazy="selectin")
    medicine = relationship("Medicine", back_populates="machine_medicine_slots", lazy="selectin")
