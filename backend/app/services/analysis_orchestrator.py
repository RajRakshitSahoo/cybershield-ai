"""
Orchestrates a full URL scan: domain intel -> DNS -> SSL -> headers -> tech
detection -> reputation -> ML prediction -> screenshots, while recording a
step-by-step timeline (used by the frontend's "Threat Timeline" view).
"""
import time
from datetime import datetime, timezone

from app.ml import ml_service
from app.services import (
    domain_service, ssl_service, header_service, tech_detection,
    reputation_service, screenshot_service,
)


def _timed(label, fn, *args, **kwargs):
    start = time.perf_counter()
    try:
        value = fn(*args, **kwargs)
        status = "done"
    except Exception as e:  # noqa: BLE001
        value = None
        status = "failed"
    duration_ms = int((time.perf_counter() - start) * 1000)
    return value, {"step": label, "status": status, "duration_ms": duration_ms}


def run_full_analysis(raw_url: str) -> dict:
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    timeline = []

    domain_result, t1 = _timed("Domain & WHOIS Lookup", domain_service.analyze_domain, url)
    timeline.append(t1)
    domain_result = domain_result or {
        "hostname": url, "registered_domain": url,
        "domain_info": {"domain": url}, "dns_info": {}, "whois_full": {},
    }
    hostname = domain_result["hostname"]

    dns_info, t2 = _timed("DNS Resolution", lambda: domain_result["dns_info"])
    timeline.append(t2)

    ssl_info, t3 = _timed("SSL/TLS Verification", ssl_service.analyze_ssl, hostname)
    timeline.append(t3)
    ssl_info = ssl_info or {"https": False, "valid": False, "hsts": False}

    page_meta, t4 = _timed("Fetching Page Content", domain_service.get_page_meta, url)
    timeline.append(t4)
    page_meta = page_meta or {}
    if ssl_info:
        ssl_info["hsts"] = ssl_service.check_hsts(page_meta.get("headers", {}))

    security_headers, t5 = _timed("Security Header Analysis", header_service.analyze_headers, page_meta.get("headers"))
    timeline.append(t5)

    tech_stack, t6 = _timed("Technology Fingerprinting", tech_detection.detect_technologies,
                             page_meta.get("html"), page_meta.get("headers"))
    timeline.append(t6)
    tech_stack = tech_stack or {}

    reputation, t7 = _timed(
        "Blacklist / Reputation Check", reputation_service.run_all_checks,
        url, domain_result["domain_info"].get("ip_address"),
    )
    timeline.append(t7)
    reputation = reputation or []

    ai_prediction, t8 = _timed(
        "AI Phishing Prediction", ml_service.predict, url,
        domain_result["domain_info"].get("domain_age_days") or -1,
        page_meta.get("redirect_count", 0),
    )
    timeline.append(t8)

    screenshots, t9 = _timed("Capturing Screenshots", screenshot_service.capture_screenshots, url)
    timeline.append(t9)
    screenshots = screenshots or {"desktop": None, "mobile": None}

    domain_info = dict(domain_result["domain_info"])
    domain_info["title"] = page_meta.get("title")
    domain_info["favicon"] = page_meta.get("favicon")

    _, t10 = _timed("Final Score Aggregation", lambda: ai_prediction["risk_score"])
    timeline.append(t10)

    report = {
        "url": url,
        "scanned_at": datetime.now(timezone.utc),
        "domain_info": domain_info,
        "ssl_info": ssl_info,
        "dns_info": dns_info or {},
        "security_headers": security_headers or [],
        "tech_stack": tech_stack,
        "reputation": reputation,
        "ai_prediction": ai_prediction,
        "timeline": timeline,
        "screenshot_desktop": screenshots.get("desktop"),
        "screenshot_mobile": screenshots.get("mobile"),
    }
    return report
