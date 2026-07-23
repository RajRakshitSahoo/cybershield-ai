from fastapi import APIRouter

from app.models.schemas import CompareRequest
from app.services.analysis_orchestrator import run_full_analysis

router = APIRouter(prefix="/api/compare", tags=["compare"])


def _verdict_pick(a_val, b_val, lower_is_safer=False):
    if a_val is None or b_val is None:
        return None
    if lower_is_safer:
        return "a" if a_val < b_val else ("b" if b_val < a_val else "tie")
    return "a" if a_val > b_val else ("b" if b_val > a_val else "tie")


@router.post("")
async def compare(payload: CompareRequest):
    report_a = run_full_analysis(payload.url_a)
    report_b = run_full_analysis(payload.url_b)

    comparison = {
        "domain_age_days": {
            "a": report_a["domain_info"].get("domain_age_days"),
            "b": report_b["domain_info"].get("domain_age_days"),
            "safer": _verdict_pick(
                report_a["domain_info"].get("domain_age_days"),
                report_b["domain_info"].get("domain_age_days"),
            ),
        },
        "https": {
            "a": report_a["ssl_info"].get("https"),
            "b": report_b["ssl_info"].get("https"),
        },
        "hosting_country": {
            "a": report_a["domain_info"].get("country"),
            "b": report_b["domain_info"].get("country"),
        },
        "hosting_provider": {
            "a": report_a["domain_info"].get("hosting_provider"),
            "b": report_b["domain_info"].get("hosting_provider"),
        },
        "ai_risk_score": {
            "a": report_a["ai_prediction"]["risk_score"],
            "b": report_b["ai_prediction"]["risk_score"],
            "safer": _verdict_pick(
                report_a["ai_prediction"]["risk_score"],
                report_b["ai_prediction"]["risk_score"],
                lower_is_safer=True,
            ),
        },
        "blacklisted": {
            "a": any(r["status"] == "blacklisted" for r in report_a["reputation"]),
            "b": any(r["status"] == "blacklisted" for r in report_b["reputation"]),
        },
        "missing_security_headers": {
            "a": len([h for h in report_a["security_headers"] if h["status"] == "missing"]),
            "b": len([h for h in report_b["security_headers"] if h["status"] == "missing"]),
        },
        "verdict": {
            "a": report_a["ai_prediction"]["verdict"],
            "b": report_b["ai_prediction"]["verdict"],
        },
    }

    overall_safer = "a" if report_a["ai_prediction"]["risk_score"] < report_b["ai_prediction"]["risk_score"] else "b"

    return {
        "report_a": report_a,
        "report_b": report_b,
        "comparison": comparison,
        "overall_safer": overall_safer,
    }
