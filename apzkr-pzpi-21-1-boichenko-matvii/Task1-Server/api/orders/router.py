from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from common.error_messages import ErrorMessages
from dependencies.user import current_active_user
from services.order.order_schemas import GetOrderByIdResponseDto
from services.order.order_service import OrderCrudService
from services.order.order_schemas import (CreateOrderDto, PatchOrderDto, PutOrderDto, OrderResponseDto)

orders_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(current_active_user)])


@orders_router.post("/", response_model=OrderResponseDto, status_code=status.HTTP_201_CREATED)
async def create_order(create_order_dto: CreateOrderDto, service: OrderCrudService = Depends(OrderCrudService.get_instance)):
    return await service.create_order(create_order_dto)


@orders_router.put("/{order_id}", response_model=OrderResponseDto)
async def update_order(order_id: UUID, put_order_dto: PutOrderDto,
                       service: OrderCrudService = Depends(OrderCrudService.get_instance)):
    return await service.put_order(order_id, put_order_dto)


@orders_router.patch("/{order_id}", response_model=OrderResponseDto)
async def patch_order(order_id: UUID, patch_order_dto: PatchOrderDto,
                      service: OrderCrudService = Depends(OrderCrudService.get_instance)):
    return await service.patch_order(order_id, patch_order_dto)


@orders_router.get("/{order_id}", response_model=GetOrderByIdResponseDto)
async def get_order(order_id: UUID, service: OrderCrudService = Depends(OrderCrudService.get_instance)):
    return await service.get_order_by_id(order_id)


@orders_router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: UUID, service: OrderCrudService = Depends(OrderCrudService.get_instance)):
    success = await service.delete_order_by_id(order_id)

    if not success:
        raise HTTPException(status_code=404, detail=ErrorMessages.order.ORDER_NOT_FOUND)

    return {"detail": "Order deleted successfully"}


@orders_router.post("/search", response_model=list[OrderResponseDto])
async def search_orders(filters: dict, service: OrderCrudService = Depends(OrderCrudService.get_instance)):
    return await service.search_orders(filters)
