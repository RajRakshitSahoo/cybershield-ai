from collections import Counter

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import require_admin
from app.database import get_db, to_list

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
async def platform_stats(admin=Depends(require_admin)):
    db = get_db()
    total_users = await db["users"].count_documents({})
    scans = await to_list(db["scans"].find({}))

    verdict_counts = Counter(s["ai_prediction"]["verdict"] for s in scans)
    phishing_domains = Counter(
        s["domain_info"].get("domain") for s in scans
        if s["ai_prediction"]["verdict"] == "Phishing" and s["domain_info"].get("domain")
    )
    daily = Counter(s["scanned_at"].strftime("%Y-%m-%d") for s in scans)
    recent = sorted(scans, key=lambda s: s["scanned_at"], reverse=True)[:10]

    return {
        "total_users": total_users,
        "total_scans": len(scans),
        "daily_scans": dict(sorted(daily.items())),
        "verdict_distribution": dict(verdict_counts),
        "top_phishing_domains": dict(phishing_domains.most_common(10)),
        "recent_detections": [
            {
                "url": s["url"],
                "verdict": s["ai_prediction"]["verdict"],
                "risk_score": s["ai_prediction"]["risk_score"],
                "scanned_at": s["scanned_at"],
            }
            for s in recent
        ],
    }


@router.get("/users")
async def list_users(admin=Depends(require_admin)):
    db = get_db()
    users = await to_list(db["users"].find({}))
    return [
        {"id": str(u["_id"]), "name": u["name"], "email": u["email"], "role": u["role"], "created_at": u["created_at"]}
        for u in users
    ]


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin=Depends(require_admin)):
    db = get_db()
    if str(admin["_id"]) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    deleted = result.deleted_count if hasattr(result, "deleted_count") else 0
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "deleted"}


@router.get("/api-health")
async def api_monitoring(admin=Depends(require_admin)):
    from app.config import settings
    return {
        "virustotal_configured": bool(settings.virustotal_api_key),
        "google_safe_browsing_configured": bool(settings.google_safe_browsing_api_key),
        "abuseipdb_configured": bool(settings.abuseipdb_api_key),
        "database_mode": "mongomock (in-memory)" if settings.use_mock_db else "mongodb",
    }
