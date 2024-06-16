import json
import os.path
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

import logger
from dependencies.user import current_active_user
from common.error_messages import ErrorMessages
from extensions.babel import babel

general_router = APIRouter(prefix="/general", tags=["general"], dependencies=[Depends(current_active_user)])


@general_router.post("/general/{locale}", response_model=dict, status_code=200)
async def get_general_localisation(locale: str):
    print("LOCALE", babel.locale)
    try:
        with open(os.path.join(Path(__file__).resolve().parent.parent.parent,
                               "localisation", f"{locale.lower()}.json"), "r") as f:
            resp_body = json.load(f)
    except BaseException as ex:
        logger.Logger.exception("Failed to load localisation file", exc_info=ex)
        raise HTTPException(status_code=404, detail=ErrorMessages.General.GENERAL_LOCALISATION_NOT_FOUND)

    return resp_body
