from urllib.parse import urlparse

from fastapi import APIRouter

from app.models.schemas import AnalyzeRequest
from app.services import domain_service, ssl_service, header_service

router = APIRouter(prefix="/api/security", tags=["security"])


@router.post("/ssl")
async def ssl_check(payload: AnalyzeRequest):
    url = payload.url if "://" in payload.url else f"https://{payload.url}"
    hostname = urlparse(url).netloc.split(":")[0]
    return ssl_service.analyze_ssl(hostname)


@router.post("/headers")
async def headers_check(payload: AnalyzeRequest):
    url = payload.url if "://" in payload.url else f"https://{payload.url}"
    meta = domain_service.get_page_meta(url)
    return header_service.analyze_headers(meta.get("headers"))
