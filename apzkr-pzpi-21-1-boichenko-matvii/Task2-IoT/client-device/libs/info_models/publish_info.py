from pydantic import BaseModel


class PublishInfo(BaseModel):
    topic: str
    payload: dict
    qos: int = 0
    retain: bool = False
