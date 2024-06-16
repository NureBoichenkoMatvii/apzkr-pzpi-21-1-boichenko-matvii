from pydantic import BaseModel
from pydantic_partial import create_partial_model

from common.common_schemas import OrderByParams
from common.common_schemas import PaginationParams
from common.common_schemas import UuidDto
from database.models import Currencies
from database.models import MedicineType


class CreateMedicineDto(BaseModel):
    type: MedicineType
    name: str
    description: str
    price: float
    currency: Currencies
    prescription_needed: bool
    is_available: bool


PatchMedicineDto = create_partial_model(CreateMedicineDto)


class PutMedicineDto(CreateMedicineDto):
    pass


class MedicineSearchDto(BaseModel):
    simple_filters: PatchMedicineDto | None = None
    search_substring: str | None = None

    pagination: PaginationParams | None = PaginationParams()
    order_by: OrderByParams | None


class MedicineResponseDto(CreateMedicineDto, UuidDto):
    pass
