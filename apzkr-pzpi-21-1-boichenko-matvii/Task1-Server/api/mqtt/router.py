from typing import Dict

from fastapi import APIRouter, Security, Depends

from dependencies.api_key_auth import get_api_key
from services.mqtt.mqtt_handlers_schemas import *
from services.mqtt.mqtt_handlers_service import MQTTHandlersService

mqtt_router = APIRouter(prefix="/mqtt-handlers", tags=["mqtt-handlers"], dependencies=[Security(get_api_key)])


@mqtt_router.post("/test", response_model=Dict)
async def test(body: dict, service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
    return {"message": "Test success"}


@mqtt_router.post("/order/event", response_model=Dict)
async def handle_order_event(body: BaseMessage[OrderEvent],
                             service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
    await service.handle_order_event(body)
    return {"message": "success"}


@mqtt_router.post("/machine/connection", response_model=Dict)
async def handle_machine_connection_update(body: BaseMessage[MachineConnection],
                                           service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
    await service.handle_machine_connection_update(body)
    return {"message": "success"}


@mqtt_router.post("/machine/status", response_model=Dict)
async def handle_machine_status_info(body: BaseMessage[MachineStatusInfo],
                                     service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
    await service.handle_machine_status_info(body)
    return {"message": "success"}


@mqtt_router.post("/machine/register/req", response_model=Dict)
async def handle_machine_registration_request(body: BaseMessage[RegistrationRequest],
                                              service: MQTTHandlersService = Depends(MQTTHandlersService.get_instance)):
    await service.handle_machine_registration_request(body)
    return {"message": "success"}
