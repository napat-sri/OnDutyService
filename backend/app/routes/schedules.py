from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from ..database import get_database
from ..models.schedule import ScheduleCreate, ScheduleUpdate

router = APIRouter(prefix="/schedules", tags=["schedules"])


def schedule_helper(schedule) -> dict:
    return {
        "_id": str(schedule["_id"]),
        "year": schedule["year"],
        "month": schedule["month"],
        "entries": schedule.get("entries", []),
        "created_at": schedule.get("created_at", datetime.utcnow()),
        "updated_at": schedule.get("updated_at", datetime.utcnow()),
    }


@router.get("/")
async def list_schedules():
    db = get_database()
    schedules = []
    async for schedule in db.schedules.find().sort([("year", -1), ("month", -1)]):
        schedules.append(schedule_helper(schedule))
    return schedules


@router.get("/{year}/{month}")
async def get_schedule(year: int, month: int):
    db = get_database()
    schedule = await db.schedules.find_one({"year": year, "month": month})
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule_helper(schedule)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_schedule(data: ScheduleCreate):
    db = get_database()
    existing = await db.schedules.find_one({"year": data.year, "month": data.month})
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Schedule for {data.year}/{data.month} already exists",
        )
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    result = await db.schedules.insert_one(doc)
    created = await db.schedules.find_one({"_id": result.inserted_id})
    return schedule_helper(created)


@router.put("/{year}/{month}")
async def update_schedule(year: int, month: int, data: ScheduleUpdate):
    db = get_database()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    update_data["updated_at"] = datetime.utcnow()
    result = await db.schedules.update_one(
        {"year": year, "month": month}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
    updated = await db.schedules.find_one({"year": year, "month": month})
    return schedule_helper(updated)


@router.delete("/{year}/{month}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(year: int, month: int):
    db = get_database()
    result = await db.schedules.delete_one({"year": year, "month": month})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Schedule not found")
