from uuid import UUID

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from database import db
from database.models import OrderMedicine
from services.base_service import BaseCrudService
from services.medicine.medicine_service import MedicineCrudService
from services.order.order_medicine_schemas import *
from services.order.order_service import OrderCrudService


class OrderMedicineCrudService(BaseCrudService[OrderMedicine]):
    def __init__(self, db_session: AsyncSession, orders_service: OrderCrudService,
                 medicines_service: MedicineCrudService):
        super().__init__(OrderMedicine, db_session)
        self.orders_service: OrderCrudService = orders_service
        self.medicines_service: MedicineCrudService = medicines_service

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session),
                     orders_service: OrderCrudService = Depends(OrderCrudService.get_instance),
                     medicines_service: MedicineCrudService = Depends(MedicineCrudService.get_instance)):
        return cls(db_session=db_session, orders_service=orders_service, medicines_service=medicines_service)

    async def create_order_medicine(self, create_order_medicine_dto: CreateOrderMedicineDto):
        existing_machine_order_medicine = await OrderMedicine.get(
            self.db, {
                "machine_id": create_order_medicine_dto.machine_id,
                "medicine_id": create_order_medicine_dto.medicine_id
            })
        if existing_machine_order_medicine:
            raise HTTPException(status_code=400, detail=ErrorMessages.order.ORDER_HAS_SUCH_MEDICINE)

        order_medicine = await OrderMedicine.create(self.db, **create_order_medicine_dto.model_dump())

        return await db_row_to_pydantic(order_medicine, OrderMedicineResponseDto)

    async def update_order_medicine(self, order_medicine_id: UUID, update_order_medicine_dto: PatchOrderMedicineDto):
        order_medicine = await OrderMedicine.update(self.db, {"id": order_medicine_id}, **update_order_medicine_dto.model_dump())
        return await db_row_to_pydantic(order_medicine, OrderMedicineResponseDto)

    async def get_order_medicine_by_id(self, order_medicine_id: UUID):
        order_medicine = await OrderMedicine.get(self.db, {"id": order_medicine_id})
        if not order_medicine:
            raise HTTPException(status_code=404, detail=ErrorMessages.order.ORDER_MEDICINE_NOT_FOUND)
        return await db_row_to_pydantic(order_medicine, OrderMedicineResponseDto)

    async def delete_order_medicine_by_id(self, order_medicine_id: UUID):
        success = await OrderMedicine.delete(self.db, {"id": order_medicine_id})
        return success

    async def search_order_medicines(self, search_filters: dict):
        order_medicines = await OrderMedicine.get_all(self.db, search_filters)
        return [await db_row_to_pydantic(order_medicine, OrderMedicineResponseDto) for order_medicine in order_medicines]
