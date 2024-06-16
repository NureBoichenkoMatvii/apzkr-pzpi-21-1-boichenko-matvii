from fastapi import APIRouter
from fastapi import Depends

from services.backup.backup_service import BackupService

backup_router = APIRouter(prefix="/backup", tags=["backup"])


@backup_router.post("/save")
async def save_backup(directory_path: str, backup_service: BackupService = Depends(BackupService.get_instance)):
    await backup_service.save_to_csv(directory_path)
    return {"message": "Backup saved successfully"}


@backup_router.post("/restore")
async def restore_backup(directory_path: str, backup_service: BackupService = Depends(BackupService.get_instance)):
    await backup_service.restore_from_csv(directory_path)
    return {"message": "Backup restored successfully"}


@backup_router.get("/download")
async def download_backup(directory_path: str, backup_service: BackupService = Depends(BackupService.get_instance)):
    zip_bytes = await backup_service.download_as_zip(directory_path)
    return zip_bytes
