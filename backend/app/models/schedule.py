from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class DutyEntry(BaseModel):
    officer_id: str
    officer_name: str
    officer_duty: str
    date: str  # ISO date string YYYY-MM-DD


class ScheduleBase(BaseModel):
    year: int
    month: int  # 1-12
    entries: List[DutyEntry] = []


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(BaseModel):
    entries: Optional[List[DutyEntry]] = None


class Schedule(ScheduleBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
