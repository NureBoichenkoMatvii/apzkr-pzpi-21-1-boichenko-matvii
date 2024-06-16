import logging
from datetime import datetime
from datetime import timezone

from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from common.error_messages import ErrorMessages
from database import db
from database.models import Machine
from database.models import MachineMedicineSlot
from database.models import MachineStatistic
from database.models import MachineStatus
from database.models import Order
from database.models import OrderStatus
from logger import CustomLogger
from services.mqtt.mqtt_service import mqtt_service
from .mqtt_handlers_schemas import *


class MQTTHandlersService:
    def __init__(self, db_session: AsyncSession):
        self.db: AsyncSession = db_session
        self.logger = CustomLogger("MQTTService", logging.DEBUG)
        self.logger.setLevel("DEBUG")

    @classmethod
    def get_instance(cls, db_session: AsyncSession = Depends(db.get_session)):
        return cls(db_session=db_session)

    async def handle_order_event(self, body: BaseMessage[OrderEvent]):
        split_topic = body.topic.split("/")

        machine_mac = split_topic[1] if len(split_topic) >= 2 else None

        order_id = split_topic[3] if len(split_topic) >= 4 else None
        order: Order = await Order.get(self.db, {"id": order_id})

        if not order or order.machine.mac != machine_mac:
            raise HTTPException(status_code=404, detail=ErrorMessages.order.ORDER_NOT_FOUND)

        update_body = {"status": OrderStatus.completed}
        if body.payload.status == "fail":
            self.logger.error(f"Failed execution of order {order_id} on machine. Reason: {body.payload.reason}")
            update_body["status"] = OrderStatus.failed
            order = await Order.update(self.db, {"id": order_id}, **{
                "status": OrderStatus.failed
            })
        elif body.payload.status == "success":
            self.logger.info(f"Successfully executed order {order_id} on machine")
            order = await Order.update(self.db, {"id": order_id}, **{
                "status": OrderStatus.completed,
                "completion_date": datetime.now(tz=timezone.utc)
            })
        elif body.payload.status == "start":
            self.logger.info(f"Started executing of order {order_id} on machine")

        return order

    async def handle_machine_connection_update(self, body: BaseMessage[MachineConnection]):
        split_topic = body.topic.split("/")
        machine_mac = split_topic[1] if len(split_topic) >= 2 else None
        machine = await Machine.update(self.db, {"mac": machine_mac}, **{"is_online": body.payload.online})

        if not machine:
            raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_NOT_FOUND)

        return machine

    async def handle_machine_status_info(self, body: BaseMessage[MachineStatusInfo]):
        split_topic = body.topic.split("/")
        machine_mac = split_topic[1] if len(split_topic) >= 2 else None
        machine = await Machine.get(self.db, {"mac": machine_mac})

        if not machine:
            self.logger.debug(f"No machine with such mac {machine_mac} of this statistic found")
            raise HTTPException(status_code=404, detail=ErrorMessages.Machine.MACHINE_NOT_FOUND)

        machine_id: uuid.UUID = machine.id
        self.logger.debug(f"Trying to save statistic for machine {machine_id}")

        statistic = await MachineStatistic.create(
            self.db, **{"machine_id": machine_id, "info": body.payload.model_dump()})

        if machine.status == MachineStatus.unregistered:
            await Machine.update(
                self.db, {"mac": machine_mac},
                **{"status": MachineStatus.registered, "is_online": True,
                   "location": body.payload.location.model_dump()})

        for slot_id, slot_data in body.payload.inventory.items():
            slot = await MachineMedicineSlot.update(
                self.db, {"id": slot_id}, total_count=slot_data.left_amount)
            if not slot:
                self.logger.error(f"Failed to update machine {body.payload.mac} medicine slot {slot_id}")

        return statistic

    async def handle_machine_registration_request(self, body: BaseMessage[RegistrationRequest]):
        machine_mac = body.payload.mac
        response_topic = f"machine/{machine_mac}/register/resp"

        machine = await Machine.get(self.db, {"mac": machine_mac})

        if not machine:
            mqtt_service.publish(response_topic, {"status": "failure"})
        else:
            mqtt_service.publish(response_topic, {"status": "success"})
            if machine.status == MachineStatus.unregistered:
                await Machine.update(self.db, {"mac": machine_mac},
                                     status=MachineStatus.registered, is_online=True)

    async def send_new_order_request(self, machine_mac: str, body: NewOrderRequest):
        topic = f"machine/{machine_mac}/orders/new"
        return mqtt_service.publish(topic, body.model_dump())

    async def send_machine_unregister_request(self, machine_mac: str):
        topic = f"machine/{machine_mac}/unregister"
        return mqtt_service.publish(topic, {})

    async def send_inventory_update_request(self, machine_mac: str, body: dict[str, InventoryItemInfo | None]):
        topic = f"machine/{machine_mac}/inventory/update"
        adapted_body = {k: v.model_dump() for k, v in body.items()}
        return mqtt_service.publish(topic, adapted_body)
