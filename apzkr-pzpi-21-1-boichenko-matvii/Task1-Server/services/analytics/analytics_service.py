from typing import List
from typing import List

from fastapi import Depends
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from common.utils.mapping import db_row_to_pydantic
from database import db
from database.models import Machine
from database.models import Medicine
from database.models import Order
from database.models import OrderMedicine
from database.models import OrderStatus
from database.models import PickupPoint
from .schemas import *
from .schemas import PopularPickupPointsResponse


class AnalyticsService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session)):
        return cls(db_session=db_session)

    async def get_income(self, request: IncomeRequest) -> List[IncomeResponse]:
        limit = offset = None
        if request.pagination:
            limit = request.pagination.limit
            offset = request.pagination.offset

        date_trunc_func = func.date_trunc(request.period, Order.payment_date)
        query = (
            select(date_trunc_func, func.sum(Order.payment_amount))
            .where(Order.payment_date.isnot(None))
            .group_by(date_trunc_func)
            .offset(offset)
            .limit(limit)
            .order_by(date_trunc_func)
        )
        result = await self.db.execute(query)
        income_data = result.all()
        return [IncomeResponse(date=row[0], income=row[1]) for row in income_data]

    async def get_popular_machines(self, request: PopularStatisticRequest) -> List[PopularPickupPointsResponse]:
        order_column = func.count() if request.order_by == 'count' else func.sum(Order.payment_amount)

        query = (
            select(Machine, order_column)
            .join(Order, Machine.id == Order.machine_id)
            .where(Order.payment_date.between(request.start_date, request.end_date))
            .group_by(Machine.id)
            .order_by(desc(order_column))
        )

        result = await self.db.execute(query)
        machines_data = result.all()

        return [PopularPickupPointsResponse(
            machine=await db_row_to_pydantic(row[0], MachineData), sort_value=row[1]) for row in machines_data]

    async def get_popular_medicines(self, request: PopularStatisticRequest) -> List[PopularMedicinesResponse]:
        order_column = func.count() if request.order_by == 'count' else func.sum(Order.payment_amount)

        query = (
            select(Medicine, order_column)
            .join(OrderMedicine, Medicine.id == OrderMedicine.medicine_id)
            .join(Order, Order.id == OrderMedicine.order_id)
            .where(sql.and_(
                Order.payment_date.between(
                    request.start_date, request.end_date),
                Order.status == OrderStatus.completed
            ))
            .group_by(Medicine.id)
            .order_by(desc(order_column))
        )
        result = await self.db.execute(query)
        medicines_data = result.all()

        return [PopularMedicinesResponse(
            medicine=await db_row_to_pydantic(row[0], MedicineData), sort_value=row[1]) for row in medicines_data]

    async def get_popular_pickup_point(self, request: PopularStatisticRequest) -> list[PopularPickupPointsResponse]:
        order_column = func.count() if request.order_by == 'count' else func.sum(Order.payment_amount)

        query = (
            select(PickupPoint, order_column)
            .join(Order, PickupPoint.id == Order.pickup_point_id)
            .where(sql.and_(
                Order.payment_date.between(
                    request.start_date, request.end_date),
                Order.status == OrderStatus.completed
            ))
            .group_by(PickupPoint.id)
            .order_by(desc(order_column))
        )
        result = await self.db.execute(query)
        medicines_data = result.all()

        return [PopularPickupPointsResponse(
            pickup_point=await db_row_to_pydantic(row[0], MedicineData),
            sort_value=row[1]) for row in medicines_data]
