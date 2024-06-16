from typing import Callable

from pydantic import BaseModel


class SubscribeInfo(BaseModel):
    topic: str
    qos: int = 0
    callback: Callable | None = None
