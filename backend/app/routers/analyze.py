from bson import ObjectId
from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.schemas import AnalyzeRequest, AnalysisReport
from app.services.analysis_orchestrator import run_full_analysis

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("", response_model=AnalysisReport)
async def analyze(payload: AnalyzeRequest, user=Depends(get_current_user)):
    report = run_full_analysis(payload.url)
    db = get_db()

    doc = dict(report)
    doc["user_id"] = str(user["_id"]) if user else None
    doc["user_email"] = user["email"] if user else None
    result = await db["scans"].insert_one(doc)
    report["id"] = str(result.inserted_id)

    # Update rolling daily stats used by the admin + user dashboards.
    day_key = report["scanned_at"].strftime("%Y-%m-%d")
    verdict = report["ai_prediction"]["verdict"]
    await db["daily_stats"].update_one(
        {"date": day_key},
        {
            "$inc": {
                "total_scans": 1,
                f"verdicts.{verdict}": 1,
            }
        },
        upsert=True,
    )
    return report
