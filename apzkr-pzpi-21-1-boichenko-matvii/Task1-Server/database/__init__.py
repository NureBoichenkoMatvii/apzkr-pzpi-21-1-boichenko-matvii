import os.path
import sys

import sqlalchemy

from config import settings
from sqlalchemy import create_engine, Engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import Session, sessionmaker

from . import models


class Database:
    def __init__(self):
        self.create_async_session: async_sessionmaker[AsyncSession] = None
        self.create_sync_session: sessionmaker[Session] = None
        self.async_engine: AsyncEngine = None
        self.sync_engine: Engine = create_engine(
            settings.SYNC_DATABASE_URI,
            pool_size=settings.DB_POOL_SIZE
        )

    def init_load_medecines(self):
        print("INITACTIONS")
        with open(os.path.join(os.path.dirname(__file__), 'init_medecines_ua.sql'), 'r') as file:
            sql_statements = file.read()

        try:
            with self.sync_engine.connect() as con:
                con.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DATABASE_SCHEMA}"))
                con.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
                con.execute(text(sql_statements))
                con.commit()
        except sqlalchemy.exc.IntegrityError as e:
            print("Failed to execute init actions")
            print(e.orig)

    def connect(self, db_config: dict = None):
        self.async_engine = create_async_engine(
            settings.ASYNC_DATABASE_URI,
            # echo=True,
            execution_options={"server_settings": {"search_path": str(settings.DATABASE_SCHEMA)}},
            pool_size=settings.DB_POOL_SIZE
            # f"search_path%3D%3D{values['DATABASE_SCHEMA']}"}
        )

        self.create_async_session = async_sessionmaker(
            bind=self.async_engine,
            autocommit=False,
            expire_on_commit=False,
        )
        self.create_sync_session = sessionmaker(
            bind=self.sync_engine,
            autocommit=False,
            expire_on_commit=False,
        )

    async def disconnect(self):
        await self.async_engine.dispose()

    async def get_session(self) -> AsyncSession:
        async with db.create_async_session() as session:
            yield session


db = Database()
