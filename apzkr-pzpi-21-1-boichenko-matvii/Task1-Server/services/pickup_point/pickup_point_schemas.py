import uuid

from pydantic import BaseModel
from pydantic_partial import create_partial_model

from common.common_schemas import UuidDto
from database.models import Location


class CreatePickupPointDto(BaseModel):
    location: Location
    is_available: bool


PatchPickupPointDto = create_partial_model(CreatePickupPointDto)


class PickupPointResponseDto(CreatePickupPointDto, UuidDto):
    pass
