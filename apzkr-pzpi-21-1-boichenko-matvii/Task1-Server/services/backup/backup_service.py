import csv
import os
import zipfile
from io import BytesIO

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import StreamingResponse

from database import db
from database.models import DbBaseModel


class BackupService:
    def __init__(self, db_session: AsyncSession):
        self.db_session: AsyncSession = db_session

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session)):
        return cls(db_session=db_session)

    async def save_to_csv(self, directory_path: str):
        os.makedirs(directory_path, exist_ok=True)
        entity_types = DbBaseModel.__subclasses__()

        for entity_type in entity_types:
            entity_name = entity_type.__name__
            file_path = os.path.join(directory_path, f"{entity_name}.csv")

            result = await self.db_session.execute(select(entity_type))
            entities = result.scalars().all()

            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([column.name for column in entity_type.__table__.columns])
                for entity in entities:
                    writer.writerow([getattr(entity, column.name) for column in entity_type.__table__.columns])

    async def restore_from_csv(self, directory_path: str):
        entity_types = DbBaseModel.__subclasses__()

        for entity_type in entity_types:
            entity_name = entity_type.__name__
            file_path = os.path.join(directory_path, f"{entity_name}.csv")

            if not os.path.exists(file_path):
                continue

            with open(file_path, mode='r') as file:
                reader = csv.DictReader(file)
                entities = [entity_type(**row) for row in reader]

            self.db_session.add_all(entities)
            await self.db_session.commit()

    async def download_as_zip(self, directory_path: str) -> StreamingResponse:
        await self.save_to_csv(directory_path)

        memory_stream = BytesIO()
        with zipfile.ZipFile(memory_stream, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
            csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
            for file_name in csv_files:
                file_path = os.path.join(directory_path, file_name)
                zipf.write(file_path, arcname=file_name)

        memory_stream.seek(0)
        return StreamingResponse(memory_stream, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=backup.zip"})
