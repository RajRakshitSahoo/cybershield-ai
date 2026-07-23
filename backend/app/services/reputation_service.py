"""
Reputation / blacklist checks.

Each integration is optional and controlled by an API key in the
environment (see .env.example). When a key is missing the check reports
`unavailable` instead of failing the whole scan -- this keeps the platform
fully usable without paid subscriptions while remaining a one-line config
change away from full integration in production.
"""
import base64
import requests

from app.config import settings

REQUEST_TIMEOUT = 6


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def check_virustotal(url: str) -> dict:
    if not settings.virustotal_api_key:
        return {"source": "VirusTotal", "status": "unavailable", "detail": "API key not configured"}
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    resp = _safe(lambda: requests.get(
        f"https://www.virustotal.com/api/v3/urls/{url_id}",
        headers={"x-apikey": settings.virustotal_api_key},
        timeout=REQUEST_TIMEOUT,
    ))
    if not resp or resp.status_code != 200:
        return {"source": "VirusTotal", "status": "unavailable", "detail": "Lookup failed or URL not yet analyzed"}
    stats = resp.json().get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
    malicious = stats.get("malicious", 0) + stats.get("suspicious", 0)
    if malicious == 0:
        return {"source": "VirusTotal", "status": "clean", "detail": "0 vendors flagged this URL"}
    status = "blacklisted" if malicious >= 5 else "suspicious"
    return {"source": "VirusTotal", "status": status, "detail": f"{malicious} vendors flagged this URL"}


def check_google_safe_browsing(url: str) -> dict:
    if not settings.google_safe_browsing_api_key:
        return {"source": "Google Safe Browsing", "status": "unavailable", "detail": "API key not configured"}
    body = {
        "client": {"clientId": "cybershield-ai", "clientVersion": "1.0.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    resp = _safe(lambda: requests.post(
        f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={settings.google_safe_browsing_api_key}",
        json=body, timeout=REQUEST_TIMEOUT,
    ))
    if not resp or resp.status_code != 200:
        return {"source": "Google Safe Browsing", "status": "unavailable", "detail": "Lookup failed"}
    matches = resp.json().get("matches", [])
    if matches:
        return {"source": "Google Safe Browsing", "status": "blacklisted",
                 "detail": f"Flagged for: {', '.join(m['threatType'] for m in matches)}"}
    return {"source": "Google Safe Browsing", "status": "clean", "detail": "No known threats found"}


def check_openphish(url: str) -> dict:
    # OpenPhish's free feed is a plaintext list of active phishing URLs.
    resp = _safe(lambda: requests.get("https://openphish.com/feed.txt", timeout=REQUEST_TIMEOUT))
    if not resp or resp.status_code != 200:
        return {"source": "OpenPhish", "status": "unavailable", "detail": "Feed unreachable"}
    lines = set(resp.text.splitlines())
    if url in lines or url.rstrip("/") in lines:
        return {"source": "OpenPhish", "status": "blacklisted", "detail": "URL present in live OpenPhish feed"}
    return {"source": "OpenPhish", "status": "clean", "detail": "Not present in live OpenPhish feed"}


def check_abuseipdb(ip_address: str) -> dict:
    if not settings.abuseipdb_api_key or not ip_address:
        return {"source": "AbuseIPDB", "status": "unavailable", "detail": "API key not configured"}
    resp = _safe(lambda: requests.get(
        "https://api.abuseipdb.com/api/v2/check",
        params={"ipAddress": ip_address, "maxAgeInDays": 90},
        headers={"Key": settings.abuseipdb_api_key, "Accept": "application/json"},
        timeout=REQUEST_TIMEOUT,
    ))
    if not resp or resp.status_code != 200:
        return {"source": "AbuseIPDB", "status": "unavailable", "detail": "Lookup failed"}
    score = resp.json().get("data", {}).get("abuseConfidenceScore", 0)
    if score >= 50:
        return {"source": "AbuseIPDB", "status": "blacklisted", "detail": f"Abuse confidence score: {score}%"}
    if score >= 10:
        return {"source": "AbuseIPDB", "status": "suspicious", "detail": f"Abuse confidence score: {score}%"}
    return {"source": "AbuseIPDB", "status": "clean", "detail": f"Abuse confidence score: {score}%"}


def run_all_checks(url: str, ip_address: str) -> list:
    return [
        check_virustotal(url),
        check_google_safe_browsing(url),
        check_openphish(url),
        check_abuseipdb(ip_address),
    ]
