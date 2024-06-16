import json
import os
import random
import time
from datetime import datetime
from datetime import timezone
from logging import Logger
from pathlib import Path
from typing import Dict, Callable

from paho.mqtt.client import Client, MQTTMessage

from .info_models import *

ACTIONS_QUEUE: list[Callable] = []


class DeviceMQTTClient(object):
    def __init__(self, logger: Logger):
        self._logger: Logger = logger
        self.machine_mac: str = os.environ["MACHINE_MAC"]
        self.client_id: str = f"Machine-{self.machine_mac}"

        self.username: str = os.environ["MQTT_USER"]
        self.password: str = os.environ["MQTT_PASS"]

        self.api_host: str = os.environ["HTTP_API_HOST"]
        self.api_key: str = os.environ["HTTP_API_KEY"]

        self.is_inited = False
        self.mqtt_client: Client = self._get_mqtt_client()

        self.path_to_machine_info: str = (
            os.path.join(Path(os.path.abspath(__file__)).parent.parent, "machine_info.json"))
        self.machine: MachineInfo = self._load_machine_info()
        self._sleep_until: int = 0

    def connect_client(self):
        self.mqtt_client.loop_start()
        self.mqtt_client.connect(
            host=os.environ["MQTT_BROKER_HOST"],
            port=1883,
            keepalive=120
        )

    def _get_mqtt_client(self):
        mqtt_client = Client(client_id=self.client_id)
        mqtt_client.enable_logger(self._logger)
        mqtt_client.username_pw_set(self.username, self.password)

        # Set up Last Will and Testament (LWT) message
        last_will_message = {
            "online": False
        }
        last_will_topic = f"machine/{self.machine_mac}/connection"
        mqtt_client.will_set(last_will_topic, payload=json.dumps(last_will_message), qos=1, retain=False)

        mqtt_client.on_connect = self._on_connect
        mqtt_client.on_disconnect = self._on_disconnect
        mqtt_client.on_message = self._on_message
        mqtt_client.on_publish = self._on_publish

        return mqtt_client

    def _on_publish(self, client, userdata, mid):
        # print("Message Published.", mid)
        pass

    def _on_connect(self, client, userdata, flags, rc):
        self._logger.debug("Connected with result code " + str(rc))
        self._save_machine_info()
        self.subscribe_mqtt_client_to_all_necessary_topics(self.mqtt_client)
        self._send_initial_message()
        self.is_inited = True

    def _on_disconnect(self, client, userdata, rc):
        self._logger.debug("Disconnected with result code " + str(rc))
        self.is_inited = False

    def _on_message(self, client, userdata, msg: MQTTMessage) -> dict | None:
        try:
            payload = json.loads(msg.payload.decode('utf-8')) if msg.payload else None
            self._logger.debug(f"Received payload: {payload}")

            return payload

        except Exception as ex:
            self._logger.exception(ex, exc_info=ex)

    def _handle_order(self, client, userdata, msg: MQTTMessage):
        """
        Handle an order coming form backend
        """
        def handle():
            payload = self._on_message(client, userdata, msg)
            order = OrderInfo(**payload)

            self._logger.info(f"Start executing order {order.order_id}...")

            message = {"status": "start"}
            self.mqtt_client.publish(f"machine/{self.machine_mac}/orders/{order.order_id}/event", json.dumps(message))

            changes_in_inventory: list[dict[str, InventoryItemInfo | int]] = []
            for med in order.order_medicines:
                inventory_item_change: dict[str, InventoryItemInfo | int] | None = None
                for item in self.machine.inventory.values():
                    if item.medicine_type == med.medicine_type and item.medicine_name == med.medicine_name:
                        inventory_item_change = {"item": item, "count": med.count}
                        break

                if not inventory_item_change or not inventory_item_change.get("item"):
                    self._logger.info("Failed to execute the order. Such medicine not found")
                    message = {"status": "fail", "reason": "Such medicine not found"}
                    self.mqtt_client.publish(f"machine/{self.machine_mac}/orders/{order.order_id}/event",
                                             json.dumps(message))
                    return

                if inventory_item_change["item"].left_amount <= 0:
                    self._logger.info("Failed to execute the order. No medicine left")
                    message = {"status": "fail", "reason": "No medicine left"}
                    self.mqtt_client.publish(f"machine/{self.machine_mac}/orders/{order.order_id}/event",
                                             json.dumps(message))
                    return

                changes_in_inventory.append(inventory_item_change)

            # executing order on device, call to device module to give a medicine
            time.sleep(5)

            for change in changes_in_inventory:
                change["item"].left_amount -= change["count"]
            self._save_machine_info()

            self._logger.info(f"Successfully executed order {order.order_id}")
            message = {"status": "success"}
            self.mqtt_client.publish(f"machine/{self.machine_mac}/orders/{order.order_id}/event",
                                     json.dumps(message))

            self.force_publish_next()

        ACTIONS_QUEUE.append(handle)

    def _update_inventory(self, client, userdata, msg: MQTTMessage):
        """
            Handle an inventory update request coming from backend
        """
        def handle():
            payload: None | dict[int, dict] = self._on_message(client, userdata, msg)

            self._logger.info("Trying to updated inventory info...")

            if not payload:
                self._logger.info("Clearing inventory...")
                self.machine.inventory.clear()
            else:
                for slot_id, slot_info in payload.items():
                    if not slot_info:
                        self._logger.info("Clearing inventory slot...")
                        self.machine.inventory.pop(slot_id)
                        continue

                    new_info = {}
                    if self.machine.inventory.get(slot_id):
                        new_info = self.machine.inventory[slot_id].model_dump()
                    new_info.update(slot_info)

                    item_info = InventoryItemInfo(**new_info)
                    self.machine.inventory[slot_id] = item_info

            self._save_machine_info()
            self._logger.info("Successfully updated inventory")

            self.force_publish_next()

        ACTIONS_QUEUE.append(handle)

    def _send_initial_message(self):
        message = {"online": True}
        self.mqtt_client.publish(f"machine/{self.machine_mac}/connection", json.dumps(message))

    def try_publish_next(self) -> bool:
        if self._sleep_until >= datetime.now(tz=timezone.utc).timestamp():
            return False

        publish_info = self.get_next_publish_info()
        self.mqtt_client.publish(
            topic=publish_info.topic,
            payload=json.dumps(publish_info.payload),
            qos=publish_info.qos,
            retain=publish_info.retain
        )
        self._logger.debug(f"Published payload: \\ \n{json.dumps(publish_info.payload, indent=3)}")
        self._set_next_sleep_until()

        return True

    def force_publish_next(self) -> bool:
        """
        Force publish next action and reset sleep until mark
        """
        self._sleep_until = datetime.now(tz=timezone.utc).timestamp() - 5
        return self.try_publish_next()

    def _set_next_sleep_until(self):
        """
        Set next sleep until date, i.e. no message from device will be emitted
        until current date equals to sleep until date
        """
        status_to_next_sleep_secs_map = {
            MachineStatus.unregistered: 30,
            MachineStatus.registered: 600
        }
        self._sleep_until = datetime.now(tz=timezone.utc).timestamp() + status_to_next_sleep_secs_map[self.machine.status]

    def get_next_publish_info(self) -> PublishInfo:
        status_to_get_info_map = {
            MachineStatus.unregistered: self.get_register_publish_info,
            MachineStatus.registered: self.get_status_publish_info
        }
        publish_info = status_to_get_info_map[self.machine.status]()

        return publish_info

    def get_status_publish_info(self) -> PublishInfo:
        topic = f"machine/{self.machine_mac}/status"
        payload = self.get_statistic()
        publish_info_ = PublishInfo(topic=topic, payload=payload)

        return publish_info_

    def get_statistic(self) -> dict:
        statistic = {
            "mac": self.machine.mac,
            "temperature": random.randint(15, 50),
            "humidity": random.randint(5, 20),
            "location": {
                "latitude": random.randint(40, 50) * 1.0,
                "longitude": random.randint(15, 25) * 1.0
            },
            "firmware_version": self.machine.firmware_version,
            "hardware_version": self.machine.hardware_version,
            "inventory": {k: v.model_dump() for k, v in self.machine.inventory.items()}
        }

        return statistic

    def get_register_publish_info(self):
        topic = "machine/register/req"
        payload = {"mac": self.machine_mac}
        publish_info_ = PublishInfo(topic=topic, payload=payload)

        return publish_info_

    def get_subscribe_infos(self) -> list[SubscribeInfo]:
        """
        Returns info about topics to which device must subscribe and subscibtion details like qos and callback
        """
        subscribe_infos = [
            SubscribeInfo(topic=f"machine/{self.machine_mac}/register/resp", callback=self._register_response_callback),
            SubscribeInfo(topic=f"machine/{self.machine_mac}/unregister", callback=self._unregister_callback)
        ]

        if self.machine.status == MachineStatus.registered:
            subscribe_infos.extend([
                SubscribeInfo(topic=f"machine/{self.machine_mac}/orders/new", callback=self._handle_order),
                SubscribeInfo(topic=f"machine/{self.machine_mac}/inventory/update", callback=self._update_inventory),
            ])

        return subscribe_infos

    def _unregister_callback(self, client: Client, userdata, msg: MQTTMessage):
        payload = self._on_message(client, userdata, msg)
        self.machine.status = MachineStatus.unregistered

        self._logger.debug(f"Updated device status (unregistered). Current: {str(self.machine.status)}")

        self.mqtt_client.reconnect()
        self._set_next_sleep_until()

        return True

    def subscribe_mqtt_client_to_all_necessary_topics(self, mqtt_client: Client):
        subscribe_infos = self.get_subscribe_infos()
        for subscribe_info in subscribe_infos:
            mqtt_client.subscribe(subscribe_info.topic, subscribe_info.qos)

            if subscribe_info.callback:
                mqtt_client.message_callback_add(subscribe_info.topic, subscribe_info.callback)

    def _load_machine_info(self) -> MachineInfo:
        """
        Loads to class data from local file
        """
        try:
            with open(self.path_to_machine_info, "r") as file:
                info = json.load(file)

            info["mac"] = self.machine_mac
        except BaseException as ex:
            self._logger.exception("Got error trying to open file", exc_info=ex)
            with open(self.path_to_machine_info, "x") as file:
                pass
            info = {
                "mac": self.machine_mac,
                "firmware_version": "1.0",
                "hardware_version": "v1",
                "temperature": 0,
                "humidity": 0,
                "location": {"longitude": 23.0, "latitude": 45.0},
                "status": MachineStatus.unregistered,
                "inventory": {}
            }

        return MachineInfo(**info)

    def _save_machine_info(self, info: dict | None = None):
        if not info:
            info = self.machine.model_dump()

        with open(self.path_to_machine_info, "w+") as file:
            json.dump(info, file, indent=3)
            # file.write(info)

    def _register_response_callback(self, client: Client, userdata, msg: MQTTMessage) -> bool:
        client.on_message(client, userdata, msg)
        payload: dict = json.loads(str(msg.payload.decode("utf-8")))
        if payload["status"] == "failure":
            return False

        if self.machine.status == MachineStatus.unregistered:
            self.machine.status = MachineStatus.registered

        self._logger.debug(f"Device with mac {self.machine_mac} successfully registered")
        self._logger.debug(f"Current device status: {str(self.machine.status)}")

        self.mqtt_client.reconnect()

        return True

    def loop(self):
        if self.is_inited:
            while len(ACTIONS_QUEUE) > 0:
                try:
                    ACTIONS_QUEUE.pop(0)()
                except Exception as ex:
                    self._logger.exception(ex, exc_info=ex)

            self.try_publish_next()
