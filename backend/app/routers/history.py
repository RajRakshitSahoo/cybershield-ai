from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import require_user
from app.database import get_db, to_list
from app.models.schemas import BookmarkRequest

router = APIRouter(prefix="/api/history", tags=["history"])


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    doc.pop("user_id", None)
    doc.pop("user_email", None)
    return doc


@router.get("")
async def get_history(
    user=Depends(require_user),
    search: str = Query(default=""),
    verdict: str = Query(default=""),
):
    db = get_db()
    query = {"user_id": str(user["_id"])}
    if search:
        query["url"] = {"$regex": search, "$options": "i"}
    if verdict:
        query["ai_prediction.verdict"] = verdict
    cursor = db["scans"].find(query).sort("scanned_at", -1)
    docs = await to_list(cursor)
    return [_serialize(d) for d in docs]


@router.get("/{scan_id}")
async def get_scan(scan_id: str, user=Depends(require_user)):
    db = get_db()
    doc = await db["scans"].find_one({"_id": ObjectId(scan_id), "user_id": str(user["_id"])})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    return _serialize(doc)


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, user=Depends(require_user)):
    db = get_db()
    result = await db["scans"].delete_one({"_id": ObjectId(scan_id), "user_id": str(user["_id"])})
    deleted = result.deleted_count if hasattr(result, "deleted_count") else 0
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "deleted"}


@router.post("/bookmark")
async def bookmark(payload: BookmarkRequest, user=Depends(require_user)):
    db = get_db()
    result = await db["scans"].update_one(
        {"_id": ObjectId(payload.report_id), "user_id": str(user["_id"])},
        {"$set": {"bookmarked": True, "note": payload.note}},
    )
    matched = result.matched_count if hasattr(result, "matched_count") else 0
    if not matched:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"status": "bookmarked"}


@router.get("/bookmarks/all")
async def list_bookmarks(user=Depends(require_user)):
    db = get_db()
    cursor = db["scans"].find({"user_id": str(user["_id"]), "bookmarked": True})
    docs = await to_list(cursor)
    return [_serialize(d) for d in docs]
