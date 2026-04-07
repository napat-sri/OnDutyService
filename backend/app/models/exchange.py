from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ExchangeStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ExchangeBase(BaseModel):
    requester_id: str
    requester_name: str
    requester_date: str  # ISO date string YYYY-MM-DD
    target_id: str
    target_name: str
    target_date: Optional[str] = None  # ISO date string YYYY-MM-DD
    reason: Optional[str] = None


class ExchangeCreate(ExchangeBase):
    pass


class ExchangeUpdate(BaseModel):
    status: ExchangeStatus
    admin_note: Optional[str] = None


class Exchange(ExchangeBase):
    id: str = Field(alias="_id")
    status: ExchangeStatus = ExchangeStatus.pending
    admin_note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
