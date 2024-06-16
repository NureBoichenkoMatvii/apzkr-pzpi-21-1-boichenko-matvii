from typing import Callable

from pydantic import BaseModel


class SubscribeInfo(BaseModel):
    topic: str
    qos: int = 0
    callback: Callable | None = None
    api_endpoint_path: str | None = None


class HttpRequestBody(BaseModel):
    topic: str
    qos: int = 0
    payload: dict | None = None
    timestamp: float
    msg_timestamp: float  # relative mqtt client timestamp in seconds, not milliseconds. Like 137450.921
