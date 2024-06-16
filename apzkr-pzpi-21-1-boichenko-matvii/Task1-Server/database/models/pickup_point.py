from decimal import Decimal

from pydantic import BaseModel as PydanticBase, confloat, Field
from sqlalchemy import JSON, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from common.enums.tables import PostgresTables
from . import DbBaseModel


class Location(PydanticBase):
    latitude: confloat(gt=-90, lt=90) | None = (
        Field(..., description="Latitude in degrees (-90 to 90)."))
    longitude: confloat(gt=-180, lt=180) | None = (
        Field(..., description="Longitude in degrees (-180 to 180)."))
    country: str | None = None
    address: str | None = None

    @classmethod
    def json_encoders(cls) -> dict[any, any]:
        return {Decimal: lambda v: float(v)}


class PickupPoint(DbBaseModel):
    __tablename__ = PostgresTables.PICKUP_POINT

    location: Mapped[Location] = mapped_column(JSON, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Relationships
    machine_pickup_points = relationship("MachinePickupPoint", back_populates="pickup_point", lazy="selectin")
    orders = relationship("Order", back_populates="pickup_point")
