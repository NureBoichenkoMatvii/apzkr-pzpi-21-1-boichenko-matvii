import json
import logging

import paho.mqtt.client as mqtt

from config import settings
from logger import CustomLogger


class MQTTService:
    def __init__(self, broker_address: str = settings.MQTT_BROKER_HOST, port: int = settings.MQTT_BROKER_PORT):
        self.logger = CustomLogger("MQTTService", logging.DEBUG)

        self.broker_address = broker_address
        self.port = port
        self.client = self._get_client()

    def _get_client(self):
        mqtt_client = mqtt.Client(client_id="MqttApiClient")
        mqtt_client.enable_logger(self.logger)
        mqtt_client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)

        mqtt_client.on_connect = self._on_connect
        mqtt_client.on_disconnect = self._on_disconnect
        mqtt_client.on_publish = self._on_publish

        return mqtt_client

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.debug("Connected to MQTT Broker!")
        else:
            self.logger.debug("Failed to connect, return code %d\n", rc)

    def _on_disconnect(self, client, userdata, rc):
        self.logger.debug("Disconnected from MQTT Broker!")

    def _on_publish(self, client, userdata, mid):
        self.logger.debug("Message Published.")

    def connect(self):
        if not self.broker_address:
            print("No broker address, failed to connect")
            return False

        self.client.loop_start()
        print("BROKER", self.broker_address, self.port)
        self.client.connect(self.broker_address, self.port)

        return True

    def disconnect(self):
        self.client.disconnect()

    def publish(self, topic: str, message: str | bytes | dict, qos: int = 0, retain: bool = False) -> bool:
        if not self.broker_address:
            print("No broker address, failed to publish")
            return False

        if isinstance(message, dict):
            message = json.dumps(message)

        self.logger.info(f"Trying to send to topic {topic}")
        self.logger.debug(f"Message: {message}")

        try:
            msg_info = self.client.publish(topic, message, qos, retain)
        except BaseException as e:
            self.logger.exception("MQTT ERR", exc_info=e)
            return False

        self.logger.info(f"Success {msg_info.is_published()}")

        return msg_info.is_published()


mqtt_service: MQTTService = MQTTService()
