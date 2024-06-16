import json
import os
from datetime import datetime
from datetime import timezone
from logging import Logger
from typing import Callable

import requests
from paho.mqtt.client import Client
from paho.mqtt.client import MQTTMessage

from .schemas import HttpRequestBody
from .schemas import SubscribeInfo

ACTIONS_QUEUE: list[Callable] = list()


class ApiBridgeClient(object):
    def __init__(self, logger: Logger):
        self._logger: Logger = logger
        self.client_id: str = os.environ["CLIENT_ID"]

        self.username: str = os.environ["MQTT_USER"]
        self.password: str = os.environ["MQTT_PASS"]

        self.api_host: str = os.environ["HTTP_API_HOST"]
        self.api_key: str = os.environ["HTTP_API_KEY"]

        self.is_inited = False
        self.mqtt_client: Client = self._get_mqtt_client()

        self.http_redirect_rules: list[SubscribeInfo] = []

    def connect_client(self):
        self.mqtt_client.loop_start()
        self.mqtt_client.connect(
            host=os.environ["MQTT_BROKER_HOST"],
            port=1883,
            keepalive=120
        )

    def test_api_availability(self):
        try:
            response = requests.post(
                f"{self.api_host}/api/v1/mqtt-handlers/test",
                json={}, headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"})
            assert response.status_code == 200, "Failed HTTP API availability test"
        except:
            assert False, "Failed HTTP API availability test"

    def _on_connect(self, client, userdata, flags, rc):
        self._logger.debug("Connected with result code " + str(rc))
        self._subscribe_to_all_necessary_topics()
        self.test_api_availability()

    def _on_disconnect(self, client, userdata, rc):
        self._logger.debug("Disconnected with result code " + str(rc))
        self.is_inited = False

    def _on_message(self, client, userdata, msg: MQTTMessage):
        try:
            str_payload = json.dumps(json.loads(msg.payload.decode('utf-8')), indent=3) if msg.payload else msg.payload
            self._logger.debug(f"Received payload: \\ \n{str_payload}")
        except Exception as ex:
            self._logger.exception(ex, exc_info=ex)

    def _get_mqtt_client(self):
        mqtt_client = Client(client_id=self.client_id)
        mqtt_client.enable_logger(self._logger)
        mqtt_client.username_pw_set(self.username, self.password)

        mqtt_client.on_connect = self._on_connect
        mqtt_client.on_disconnect = self._on_disconnect
        mqtt_client.on_message = self._on_message
        # mqtt_client.on_unsubscribe = None
        # mqtt_client.on_log = None

        return mqtt_client

    def _on_test_message(self, client, userdata, msg: MQTTMessage):
        self.mqtt_client.on_message(client, userdata, msg)
        # self._logger.debug(f"Received test message for {msg.topic}")

    def get_subscribe_infos(self) -> list[SubscribeInfo]:
        subscribe_infos = [
            SubscribeInfo(topic="test", callback=self._on_test_message),
            SubscribeInfo(topic="test/handler", api_endpoint_path="/api/v1/mqtt-handlers/test"),
            SubscribeInfo(topic="machine/register/req", api_endpoint_path="/api/v1/mqtt-handlers/machine/register/req"),
            SubscribeInfo(topic="machine/+/orders/+/event", api_endpoint_path="/api/v1/mqtt-handlers/order/event"),
            SubscribeInfo(topic="machine/+/connection", api_endpoint_path="/api/v1/mqtt-handlers/machine/connection"),
            SubscribeInfo(topic="machine/+/status", api_endpoint_path="/api/v1/mqtt-handlers/machine/status"),
        ]

        return subscribe_infos

    def _subscribe_to_all_necessary_topics(self):
        subscribe_infos = self.get_subscribe_infos()
        for subscribe_info in subscribe_infos:
            self.mqtt_client.subscribe(subscribe_info.topic, subscribe_info.qos)

            if subscribe_info.callback:
                self.mqtt_client.message_callback_add(subscribe_info.topic, subscribe_info.callback)

            if subscribe_info.api_endpoint_path:
                self.mqtt_client.message_callback_add(
                    subscribe_info.topic, self._redirect_rule_factory(subscribe_info.api_endpoint_path))

        self.is_inited = True

    def _redirect_rule_factory(self, api_endpoint_path: str):
        def handle_factory(client: Client, userdata: any, msg: MQTTMessage):
            def handle():
                self.mqtt_client.on_message(client, userdata, msg)

                payload: dict | None = json.loads(msg.payload.decode('utf-8')) if msg.payload else msg.payload
                data = HttpRequestBody(
                    topic=msg.topic,
                    qos=msg.qos,
                    msg_timestamp=msg.timestamp,
                    timestamp=datetime.now(tz=timezone.utc).timestamp(),
                    payload=payload
                )

                self._logger.debug(f"POST {self.api_host}{api_endpoint_path} sending..")
                print(data.model_dump())
                try:
                    response = requests.post(f"{self.api_host}{api_endpoint_path}",
                                             json=data.model_dump(),
                                             headers={"X-Api-Key": self.api_key, "Content-Type": "application/json"},
                                             timeout=10)

                    self._logger.debug(
                        f"Received code {response.status_code} and response: {response.content.decode('utf-8')}")

                except Exception as ex:
                    self._logger.exception("Got request error", exc_info=ex)

            ACTIONS_QUEUE.append(handle)

        return handle_factory

    def loop(self):
        # self.try_pull_hub_child_devices()
        if self.is_inited:
            while len(ACTIONS_QUEUE) > 0:
                try:
                    ACTIONS_QUEUE.pop(0)()
                except Exception as ex:
                    self._logger.exception(ex, exc_info=ex)
