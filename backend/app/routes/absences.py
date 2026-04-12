import calendar
from bson import ObjectId
from datetime import date, datetime
from fastapi import APIRouter, HTTPException, Query, status
from ..database import get_database
from ..models.absence import AbsenceCreate, AbsenceUpdate

router = APIRouter(prefix="/absences", tags=["absences"])


def absence_helper(absence) -> dict:
    return {
        "_id": str(absence["_id"]),
        "officer_id": absence["officer_id"],
        "officer_name": absence.get("officer_name"),
        "start_date": absence["start_date"],
        "end_date": absence["end_date"],
        "reason": absence["reason"],
        "created_at": absence.get("created_at"),
    }


@router.get("/")
async def list_absences(
    officer_id: str = Query(None),
    year: int = Query(None),
    month: int = Query(None),
):
    db = get_database()
    query = {}
    if officer_id:
        query["officer_id"] = officer_id

    absences = []
    async for absence in db.absences.find(query).sort("start_date", 1):
        absences.append(absence_helper(absence))

    # Filter by month range if provided
    if year and month:
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        first_str = first_day.isoformat()
        last_str = last_day.isoformat()
        absences = [
            a for a in absences
            if a["start_date"] <= last_str and a["end_date"] >= first_str
        ]

    return absences


@router.get("/{absence_id}")
async def get_absence(absence_id: str):
    db = get_database()
    if not ObjectId.is_valid(absence_id):
        raise HTTPException(status_code=400, detail="Invalid absence ID")
    absence = await db.absences.find_one({"_id": ObjectId(absence_id)})
    if not absence:
        raise HTTPException(status_code=404, detail="Absence not found")
    return absence_helper(absence)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_absence(data: AbsenceCreate):
    db = get_database()
    if data.start_date > data.end_date:
        raise HTTPException(
            status_code=400, detail="start_date must not be after end_date"
        )
    # Look up officer name for convenience
    officer_name = None
    if ObjectId.is_valid(data.officer_id):
        officer = await db.officers.find_one({"_id": ObjectId(data.officer_id)})
        if officer:
            officer_name = f"{officer['rank']} {officer['name']}"
    doc = data.model_dump()
    doc["officer_name"] = officer_name
    doc["created_at"] = datetime.utcnow()
    result = await db.absences.insert_one(doc)
    created = await db.absences.find_one({"_id": result.inserted_id})
    return absence_helper(created)


@router.put("/{absence_id}")
async def update_absence(absence_id: str, data: AbsenceUpdate):
    db = get_database()
    if not ObjectId.is_valid(absence_id):
        raise HTTPException(status_code=400, detail="Invalid absence ID")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    # Validate date ordering if both dates are present
    existing = await db.absences.find_one({"_id": ObjectId(absence_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Absence not found")
    start = update_data.get("start_date", existing["start_date"])
    end = update_data.get("end_date", existing["end_date"])
    if start > end:
        raise HTTPException(
            status_code=400, detail="start_date must not be after end_date"
        )
    await db.absences.update_one(
        {"_id": ObjectId(absence_id)}, {"$set": update_data}
    )
    updated = await db.absences.find_one({"_id": ObjectId(absence_id)})
    return absence_helper(updated)


@router.delete("/{absence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_absence(absence_id: str):
    db = get_database()
    if not ObjectId.is_valid(absence_id):
        raise HTTPException(status_code=400, detail="Invalid absence ID")
    result = await db.absences.delete_one({"_id": ObjectId(absence_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Absence not found")
