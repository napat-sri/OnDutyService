from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from ..database import get_database
from ..models.officer import OfficerCreate, OfficerUpdate, DUTY_TYPES

router = APIRouter(prefix="/officers", tags=["officers"])


def officer_helper(officer) -> dict:
    return {
        "_id": str(officer["_id"]),
        "name": officer["name"],
        "rank": officer["rank"],
        "position": officer["position"],
        "department": officer.get("department"),
        "phone": officer.get("phone"),
        "duty_types": officer.get("duty_types", []),
        "created_at": officer.get("created_at"),
    }


@router.get("/duty-types")
async def list_duty_types():
    return DUTY_TYPES


@router.get("/")
async def list_officers():
    db = get_database()
    officers = []
    async for officer in db.officers.find():
        officers.append(officer_helper(officer))
    return officers


@router.get("/{officer_id}")
async def get_officer(officer_id: str):
    db = get_database()
    if not ObjectId.is_valid(officer_id):
        raise HTTPException(status_code=400, detail="Invalid officer ID")
    officer = await db.officers.find_one({"_id": ObjectId(officer_id)})
    if not officer:
        raise HTTPException(status_code=404, detail="Officer not found")
    return officer_helper(officer)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_officer(data: OfficerCreate):
    db = get_database()
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    result = await db.officers.insert_one(doc)
    created = await db.officers.find_one({"_id": result.inserted_id})
    return officer_helper(created)


@router.put("/{officer_id}")
async def update_officer(officer_id: str, data: OfficerUpdate):
    db = get_database()
    if not ObjectId.is_valid(officer_id):
        raise HTTPException(status_code=400, detail="Invalid officer ID")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    result = await db.officers.update_one(
        {"_id": ObjectId(officer_id)}, {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Officer not found")
    updated = await db.officers.find_one({"_id": ObjectId(officer_id)})
    return officer_helper(updated)


@router.delete("/{officer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_officer(officer_id: str):
    db = get_database()
    if not ObjectId.is_valid(officer_id):
        raise HTTPException(status_code=400, detail="Invalid officer ID")
    result = await db.officers.delete_one({"_id": ObjectId(officer_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Officer not found")
