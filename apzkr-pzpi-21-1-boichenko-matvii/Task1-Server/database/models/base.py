from __future__ import annotations

import inspect
import uuid
from datetime import datetime
from typing import Sequence

from config import settings
from sqlalchemy import MetaData, Column, TIMESTAMP, Boolean, Row, Uuid
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import expression as sql
from sqlalchemy.sql import func


class DbBaseModel(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(schema=settings.DATABASE_SCHEMA)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True,
                                          server_default=func.uuid_generate_v4(), default=uuid.uuid4, nullable=False)
    _deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, server_default="FALSE")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(),
                                                 server_onupdate=func.now(), nullable=False)

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> "DbBaseModel" | None:
        query = (
            sql.insert(cls)
            .values(**kwargs)
            .returning(cls)
            .execution_options(populate_existing=True)
        )
        item = await db.scalar(query)
        item_id = item.id
        await db.commit()
        item = await db.get(cls, item_id)

        return item

    @classmethod
    async def update(cls, db: AsyncSession, conditions_dict: dict = None, **kwargs) -> "DbBaseModel" | None:
        query = (
            sql.update(cls)
            .filter_by(**(conditions_dict or {}))
            .values(**kwargs)
            .execution_options(synchronize_session="fetch")
            .returning(cls)
        )
        item = await db.scalar(query)

        if not item:
            return item

        item_id = item.id
        await db.commit()
        item = await db.get(cls, item_id)

        return item

    @classmethod
    async def get(cls, db_session: AsyncSession, conditions_dict: dict = None) -> "DbBaseModel" | None:
        # conditions = [getattr(cls, key) == value for key, value in conditions_dict.items()]
        query = sql.select(cls)

        if conditions_dict:
            query = query.filter_by(**conditions_dict)

        # populate_existing = True
        item = await db_session.scalar(query.execution_options(populate_existing=True))
        return item

    @classmethod
    async def get_all(cls, db: AsyncSession, conditions_dict: dict = None) -> Sequence[Row | "DbBaseModel"]:
        query = sql.select(cls)

        if conditions_dict:
            query = query.filter_by(**conditions_dict)

        items = await db.scalars(query.execution_options(populate_existing=True))
        return items.all()

    @classmethod
    async def delete(cls, db: AsyncSession, conditions_dict: dict) -> bool:
        query = sql.delete(cls).returning(cls)

        if conditions_dict:
            query = query.filter_by(**conditions_dict)

        await db.scalar(query)
        await db.commit()
        return True

    def __repr__(self):
        try:
            columns = dict(
                (column.name, getattr(self, column.name)) for column in self.__table__.columns
            )

        except:
            o = {}
            members = inspect.getmembers(self)
            for name, obj in members:
                if type(obj) == Column:
                    o[name] = obj
            columns = o

        column_strings = []
        for column, value in columns.items():
            column_strings.append(f"{column}: {value}")

        _repr = f'<{self.__class__.__name__} {", ".join(column_strings)}>'
        return _repr
