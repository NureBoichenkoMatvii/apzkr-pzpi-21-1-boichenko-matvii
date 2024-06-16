import uuid
from enum import IntEnum, auto, StrEnum

from sqlalchemy import String, Text, Float, Boolean, Integer, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models import DbBaseModel
from common.enums.tables import PostgresTables


class MedicineType(IntEnum):
    liquid = auto()
    tablet = auto()
    capsules = auto()
    topical = auto()
    suppositories = auto()
    drops = auto()
    inhalers = auto()
    injections = auto()
    patches = auto()
    sublingual = auto()


class Currencies(StrEnum):
    usd = "USD"
    eur = "EUR"
    uah = "UAH"


# Medicine
class Medicine(DbBaseModel):
    __tablename__ = PostgresTables.MEDICINE
    __table_args__ = (UniqueConstraint('name', 'type', name='uix_name_type'),)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[MedicineType] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(30), nullable=False, default=Currencies.eur)
    prescription_needed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    order_medicines = relationship("OrderMedicine", back_populates="medicine")
    machine_medicine_slots = relationship("MachineMedicineSlot", back_populates="medicine")
