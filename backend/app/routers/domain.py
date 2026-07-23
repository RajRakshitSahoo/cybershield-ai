from fastapi import APIRouter

from app.models.schemas import AnalyzeRequest
from app.services import domain_service

router = APIRouter(prefix="/api/domain", tags=["domain"])


@router.post("/whois")
async def whois_lookup(payload: AnalyzeRequest):
    result = domain_service.analyze_domain(payload.url)
    return {"domain_info": result["domain_info"], "whois_full": result["whois_full"]}


@router.post("/dns")
async def dns_lookup(payload: AnalyzeRequest):
    result = domain_service.analyze_domain(payload.url)
    return result["dns_info"]
