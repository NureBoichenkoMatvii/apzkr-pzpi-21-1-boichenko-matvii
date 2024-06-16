import asyncio
from datetime import timedelta
from datetime import timezone
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from database import db
from database.models import MachinePickupPoint
from database.models import Medicine
from database.models import Order
from database.models import OrderMedicine
from services.base_service import BaseCrudService
from services.medicine.schemas import MedicineResponseDto
from services.mqtt.mqtt_handlers_schemas import NewOrderRequest
from services.mqtt.mqtt_handlers_service import MQTTHandlersService
from services.order.order_schemas import *


class OrderCrudService(BaseCrudService[Order]):
    def __init__(self, db_session: AsyncSession, handlers_service: MQTTHandlersService):
        super().__init__(Order, db_session)
        self.handlers_service: MQTTHandlersService = handlers_service

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session),
                     handlers_service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
        return cls(db_session=db_session, handlers_service=handlers_service)

    async def create_order(self, create_order_dto: CreateOrderDto):
        order_info = create_order_dto.model_dump()

        request_order_medicines = []
        order_medicines = []
        payment_amount = 0.0
        for med in create_order_dto.medicines:
            medicine = await Medicine.get(self.db, {"id": med.id})
            # print("AsyncLazyLoad", await medicine.awaitable_attrs.machine_medicine_slots)
            payment_amount += medicine.price * med.count
            request_order_medicines.append({
                "medicine_type": medicine.type,
                "medicine_name": medicine.name,
                "count": med.count
            })
            order_medicines.append(OrderMedicine(**{
                "medicine_id": med.id,
                "medicine_count": med.count
            }))
        order_info["payment_amount"] = payment_amount
        order_info.pop("medicines")

        order: Order = await Order.create(self.db, **order_info)
        order.order_medicines.add_all(order_medicines)

        # TODO: Execute HERE payment logic, charge user account
        print("Processing payment...")
        await asyncio.sleep(3)
        order = await Order.update(self.db, {"id": order.id}, **{
            "status": OrderStatus.payed,
            "payment_date": datetime.now(tz=timezone.utc)
        })

        request_body = NewOrderRequest(**{
            "order_id": str(order.id),
            "order_medicines": request_order_medicines
        })
        if order.machine:
            await self.handlers_service.send_new_order_request(order.machine.mac, request_body)

        return await db_row_to_pydantic(order, OrderResponseDto)

    async def put_order(self, order_id: UUID, put_order_dto: PutOrderDto):
        order: Order = await Order.update(
            self.db, {"id": order_id}, **put_order_dto.model_dump())
        return await db_row_to_pydantic(order, OrderResponseDto)

    async def patch_order(self, order_id: UUID, patch_order_dto: PatchOrderDto):
        order: Order = await Order.update(
            self.db, {"id": order_id}, **patch_order_dto.model_dump(exclude_unset=True))
        return await db_row_to_pydantic(order, OrderResponseDto)

    async def get_order_by_id(self, order_id: UUID):
        order: Order = await Order.get(self.db, {"id": order_id})

        if not order:
            raise HTTPException(status_code=404, detail=ErrorMessages.order.ORDER_NOT_FOUND)

        resp = await db_row_to_pydantic(order, GetOrderByIdResponseDto, False)

        resp.order_medicines = []
        db_medicines: list[OrderMedicine] = (await self.db.scalars(order.order_medicines.select())).all()
        for db_med in db_medicines:
            order_medicine = await db_row_to_pydantic(db_med, OrderMedicineResponseDto)
            order_medicine.medicine = await db_row_to_pydantic(db_med.medicine, MedicineResponseDto)
            resp.order_medicines.append(order_medicine)

        resp.pickup_point = await db_row_to_pydantic(order.pickup_point, PickupPointResponseDto)
        if order.machine:
            resp.machine = await db_row_to_pydantic(order.machine, MachineResponseDto)
            pickup_point = (await self.db.scalars(
                order.machine.machine_pickup_points.select()
                .where(and_(MachinePickupPoint.pickup_point_id == order.pickup_point_id,
                            MachinePickupPoint.deliver_orders,
                            MachinePickupPoint.arrival_at >= datetime.now(timezone.utc) + timedelta(days=1)))
                .order_by(asc(MachinePickupPoint.arrival_at))
            )).first()
            if pickup_point:
                resp.machine_pickup_point = await db_row_to_pydantic(pickup_point, MachinePickupPointResponseDto)

        return resp

    async def delete_order_by_id(self, order_id: UUID):
        success: bool = await Order.delete(self.db, {"id": order_id})
        return success

    async def search_orders(self, search_filters: dict):
        orders: list[Order] = await Order.get_all(self.db, search_filters)

        results = []
        for order in orders:
            results.append(await db_row_to_pydantic(order, OrderResponseDto))

        return orders
