from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class AbsenceBase(BaseModel):
    officer_id: str
    start_date: str  # ISO date string YYYY-MM-DD
    end_date: str    # ISO date string YYYY-MM-DD
    reason: str

    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_iso_date(cls, v: str) -> str:
        from datetime import date as _date
        try:
            _date.fromisoformat(v)
        except ValueError:
            raise ValueError('Date must be a valid ISO date in YYYY-MM-DD format')
        return v


class AbsenceCreate(AbsenceBase):
    pass


class AbsenceUpdate(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    reason: Optional[str] = None


class Absence(AbsenceBase):
    id: str = Field(alias="_id")
    officer_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
