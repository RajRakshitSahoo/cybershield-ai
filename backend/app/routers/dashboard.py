from collections import Counter

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_user
from app.database import get_db, to_list

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
async def summary(user=Depends(require_user)):
    db = get_db()
    cursor = db["scans"].find({"user_id": str(user["_id"])})
    docs = await to_list(cursor)

    verdict_counts = Counter(d["ai_prediction"]["verdict"] for d in docs)
    tld_counts = Counter((d["domain_info"].get("domain") or "").split(".")[-1] for d in docs if d["domain_info"].get("domain"))
    country_counts = Counter(d["domain_info"].get("country") for d in docs if d["domain_info"].get("country"))
    scores = [d["ai_prediction"]["risk_score"] for d in docs]

    by_day = Counter(d["scanned_at"].strftime("%Y-%m-%d") for d in docs)

    return {
        "total_scans": len(docs),
        "verdict_distribution": dict(verdict_counts),
        "top_tlds": dict(tld_counts.most_common(5)),
        "top_countries": dict(country_counts.most_common(5)),
        "average_risk_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "scans_by_day": dict(sorted(by_day.items())),
    }
