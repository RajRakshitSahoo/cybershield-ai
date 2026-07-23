"""Pydantic request/response models shared across routers."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    name: str
    email: EmailStr
    role: str
    created_at: datetime


# ---------- Analysis ----------
class AnalyzeRequest(BaseModel):
    url: str


class DomainInfo(BaseModel):
    domain: str
    title: Optional[str] = None
    favicon: Optional[str] = None
    ip_address: Optional[str] = None
    ipv6: Optional[str] = None
    registrar: Optional[str] = None
    creation_date: Optional[str] = None
    expiry_date: Optional[str] = None
    updated_date: Optional[str] = None
    domain_age_days: Optional[int] = None
    name_servers: List[str] = []
    hosting_provider: Optional[str] = None
    asn: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    cdn_provider: Optional[str] = None
    organization: Optional[str] = None


class SSLInfo(BaseModel):
    https: bool = False
    valid: bool = False
    issuer: Optional[str] = None
    subject: Optional[str] = None
    tls_version: Optional[str] = None
    expiry_date: Optional[str] = None
    days_remaining: Optional[int] = None
    hsts: bool = False
    error: Optional[str] = None


class DNSInfo(BaseModel):
    a: List[str] = []
    aaaa: List[str] = []
    mx: List[str] = []
    txt: List[str] = []
    ns: List[str] = []
    cname: List[str] = []
    soa: List[str] = []
    dnssec: bool = False


class SecurityHeader(BaseModel):
    name: str
    status: str  # present | missing | weak | strong
    value: Optional[str] = None


class TechStack(BaseModel):
    frontend: List[str] = []
    backend: List[str] = []
    cms: List[str] = []
    server: List[str] = []
    cdn: List[str] = []
    analytics: List[str] = []
    other: List[str] = []


class ReputationResult(BaseModel):
    source: str
    status: str  # clean | suspicious | blacklisted | unavailable
    detail: Optional[str] = None


class AIPrediction(BaseModel):
    verdict: str  # Safe | Suspicious | Phishing
    confidence: float
    risk_score: int  # 0-100
    reasons: List[str]
    feature_importances: dict


class TimelineStep(BaseModel):
    step: str
    status: str  # done | skipped | failed
    duration_ms: int


class AnalysisReport(BaseModel):
    id: Optional[str] = None
    url: str
    scanned_at: datetime
    domain_info: DomainInfo
    ssl_info: SSLInfo
    dns_info: DNSInfo
    security_headers: List[SecurityHeader]
    tech_stack: TechStack
    reputation: List[ReputationResult]
    ai_prediction: AIPrediction
    timeline: List[TimelineStep]
    screenshot_desktop: Optional[str] = None
    screenshot_mobile: Optional[str] = None


class CompareRequest(BaseModel):
    url_a: str
    url_b: str


class BookmarkRequest(BaseModel):
    report_id: str
    note: Optional[str] = None
