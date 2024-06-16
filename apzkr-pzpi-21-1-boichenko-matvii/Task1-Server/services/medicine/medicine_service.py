from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import sql
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from common.utils.mapping import db_row_to_pydantic
from database.models import Medicine
from services.base_service import BaseCrudService
from services.medicine.schemas import *


class MedicineCrudService(BaseCrudService[Medicine]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(Medicine, db_session)

    async def post_medicine(self, create_medicine_dto: CreateMedicineDto):
        medicine: Medicine = await Medicine.create(self.db, **create_medicine_dto.model_dump())
        return await db_row_to_pydantic(medicine, MedicineResponseDto)

    async def put_medicine(self, medicine_id: UUID, put_medicine_dto: PutMedicineDto):
        medicine: Medicine = await Medicine.update(
            self.db, {"id": medicine_id}, **put_medicine_dto.model_dump())
        return await db_row_to_pydantic(medicine, MedicineResponseDto)

    async def patch_medicine(self, medicine_id: UUID, patch_medicine_dto: PatchMedicineDto):
        medicine: Medicine = await Medicine.update(
            self.db, {"id": medicine_id}, **patch_medicine_dto.model_dump(exclude_unset=True))
        return await db_row_to_pydantic(medicine, MedicineResponseDto)

    async def get_medicine_by_id(self, medicine_id: UUID):
        medicine: Medicine = await Medicine.get(self.db, {"id": medicine_id})

        if not Medicine:
            raise HTTPException(status_code=404, detail=ErrorMessages.medicine.MEDICINE_NOT_FOUND)

        return await db_row_to_pydantic(medicine, MedicineResponseDto)

    async def delete_medicine_by_id(self, medicine_id: UUID):
        success: bool = await Medicine.delete(self.db, {"id": medicine_id})
        return success

    async def search_medicines(self, search_dto: MedicineSearchDto):
        query = sql.select(Medicine).options()

        if search_dto.search_substring:
            query = query.filter(sql.or_(Medicine.name.ilike(f'%{search_dto.search_substring}%'),
                                 Medicine.description.ilike(f'%{search_dto.search_substring}%')))

        if search_dto.simple_filters:
            query = query.filter_by(**search_dto.simple_filters.model_dump(exclude_unset=True))

        if search_dto.order_by:
            order_by = search_dto.order_by
            if order_by.desc:
                query = query.order_by(desc(getattr(Medicine, order_by.order_by_column)))
            else:
                query = query.order_by(asc(getattr(Medicine, order_by.order_by_column)))

        if search_dto.pagination:
            pagination = search_dto.pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
        print('querylog', query)
        medicines = (await self.db.scalars(query)).all()

        results = []
        for c in medicines:
            results.append(await db_row_to_pydantic(c, MedicineResponseDto))

        return results
