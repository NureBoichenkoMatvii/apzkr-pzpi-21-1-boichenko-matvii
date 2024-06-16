from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import desc, select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from database.models import MachineStatistic
from common.utils.mapping import db_row_to_pydantic
from services.base_service import BaseCrudService
from services.machine.machine_statistic_schemas import *


class MachineStatisticCrudService(BaseCrudService[MachineStatistic]):
    def __init__(self, db_session: AsyncSession):
        super().__init__(MachineStatistic, db_session)

    async def create_statistic(self, create_statistic_dto: CreateMachineStatisticDto):
        statistic = await MachineStatistic.create(self.db, **create_statistic_dto.model_dump())
        return await db_row_to_pydantic(statistic, MachineStatisticResponseDto)

    async def get_statistic_by_id(self, statistic_id: UUID):
        statistic = await MachineStatistic.get(self.db, {"id": statistic_id})
        if not statistic:
            raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_STATISTIC_NOT_FOUND)
        return await db_row_to_pydantic(statistic, MachineStatisticResponseDto)

    async def search_statistics(self, search_filters: MachineStatisticSearchDto):
        query = select(MachineStatistic)

        if search_filters.column_filters:
            query = query.filter_by(**search_filters.column_filters)

        if search_filters.order_by:
            order_by = search_filters.order_by
            if order_by.desc:
                query = query.order_by(desc(getattr(MachineStatistic, order_by.order_by_column)))
            else:
                query = query.order_by(asc(getattr(MachineStatistic, order_by.order_by_column)))

        if search_filters.pagination:
            pagination = search_filters.pagination
            query = query.offset(pagination.offset).limit(pagination.limit)

        statistics = (await self.db.scalars(query)).all()
        results = []
        for statistic in statistics:
            results.append(await db_row_to_pydantic(statistic, MachineStatisticResponseDto))

        return results
