from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth.dependencies import require_user
from app.database import get_db
from app.services.pdf_service import generate_pdf_report

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/{scan_id}/pdf")
async def export_pdf(scan_id: str, user=Depends(require_user)):
    db = get_db()
    doc = await db["scans"].find_one({"_id": ObjectId(scan_id), "user_id": str(user["_id"])})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    pdf_bytes = generate_pdf_report(doc)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=cybershield-report-{scan_id}.pdf"},
    )
