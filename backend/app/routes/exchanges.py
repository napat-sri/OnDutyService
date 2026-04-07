from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from datetime import datetime
from ..database import get_database
from ..models.exchange import ExchangeCreate, ExchangeUpdate, ExchangeStatus

router = APIRouter(prefix="/exchanges", tags=["exchanges"])


def exchange_helper(exchange) -> dict:
    return {
        "_id": str(exchange["_id"]),
        "requester_id": exchange["requester_id"],
        "requester_name": exchange["requester_name"],
        "requester_date": exchange["requester_date"],
        "target_id": exchange["target_id"],
        "target_name": exchange["target_name"],
        "target_date": exchange["target_date"],
        "reason": exchange.get("reason"),
        "status": exchange.get("status", ExchangeStatus.pending),
        "admin_note": exchange.get("admin_note"),
        "created_at": exchange.get("created_at"),
        "updated_at": exchange.get("updated_at"),
    }


@router.get("/")
async def list_exchanges():
    db = get_database()
    exchanges = []
    async for exchange in db.exchanges.find().sort("created_at", -1):
        exchanges.append(exchange_helper(exchange))
    return exchanges


@router.get("/{exchange_id}")
async def get_exchange(exchange_id: str):
    db = get_database()
    if not ObjectId.is_valid(exchange_id):
        raise HTTPException(status_code=400, detail="Invalid exchange ID")
    exchange = await db.exchanges.find_one({"_id": ObjectId(exchange_id)})
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange request not found")
    return exchange_helper(exchange)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_exchange(data: ExchangeCreate):
    db = get_database()
    doc = data.model_dump()
    doc["status"] = ExchangeStatus.pending
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    result = await db.exchanges.insert_one(doc)
    created = await db.exchanges.find_one({"_id": result.inserted_id})
    return exchange_helper(created)


@router.put("/{exchange_id}")
async def update_exchange_status(exchange_id: str, data: ExchangeUpdate):
    db = get_database()
    if not ObjectId.is_valid(exchange_id):
        raise HTTPException(status_code=400, detail="Invalid exchange ID")

    exchange = await db.exchanges.find_one({"_id": ObjectId(exchange_id)})
    if not exchange:
        raise HTTPException(status_code=404, detail="Exchange request not found")

    update_data = {"status": data.status, "updated_at": datetime.utcnow()}
    if data.admin_note is not None:
        update_data["admin_note"] = data.admin_note

    await db.exchanges.update_one(
        {"_id": ObjectId(exchange_id)}, {"$set": update_data}
    )

    # If approved, swap the duty entries in the schedule
    if data.status == ExchangeStatus.approved:
        await _apply_exchange_to_schedule(db, exchange)

    updated = await db.exchanges.find_one({"_id": ObjectId(exchange_id)})
    return exchange_helper(updated)


async def _apply_exchange_to_schedule(db, exchange: dict):
    """Swap the two officers' duty dates in the schedule."""
    requester_date = exchange["requester_date"]
    target_date = exchange["target_date"]
    requester_id = exchange["requester_id"]
    target_id = exchange["target_id"]

    # Parse year/month from dates
    r_year, r_month, _ = requester_date.split("-")
    t_year, t_month, _ = target_date.split("-")

    for year, month, date_str, new_officer_id, new_officer_name, old_officer_id in [
        (
            int(r_year), int(r_month), requester_date,
            target_id, exchange["target_name"], requester_id,
        ),
        (
            int(t_year), int(t_month), target_date,
            requester_id, exchange["requester_name"], target_id,
        ),
    ]:
        await db.schedules.update_one(
            {"year": year, "month": month, "entries.date": date_str,
             "entries.officer_id": old_officer_id},
            {
                "$set": {
                    "entries.$.officer_id": new_officer_id,
                    "entries.$.officer_name": new_officer_name,
                    "updated_at": datetime.utcnow(),
                }
            },
        )


@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exchange(exchange_id: str):
    db = get_database()
    if not ObjectId.is_valid(exchange_id):
        raise HTTPException(status_code=400, detail="Invalid exchange ID")
    result = await db.exchanges.delete_one({"_id": ObjectId(exchange_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Exchange request not found")
