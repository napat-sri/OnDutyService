from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class OfficerBase(BaseModel):
    name: str
    rank: str
    position: str
    department: Optional[str] = None
    phone: Optional[str] = None
    duty_types: List[str] = []


class OfficerCreate(OfficerBase):
    pass


class OfficerUpdate(BaseModel):
    name: Optional[str] = None
    rank: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    duty_types: Optional[List[str]] = None


class Officer(OfficerBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


DUTY_TYPES = [
    "นายทหารเวร",
    "นายทหารเวร (หญิง)",
    "เสมียนเวร",
    "เวรประชาสัมพันธ์",
]
