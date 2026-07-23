from app.services.header_service import analyze_headers


def test_missing_headers_flagged():
    results = analyze_headers({})
    statuses = {r["name"]: r["status"] for r in results}
    assert statuses["Content-Security-Policy"] == "missing"
    assert statuses["Strict-Transport-Security"] == "missing"


def test_strong_headers_recognized():
    headers = {
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    }
    results = {r["name"]: r["status"] for r in analyze_headers(headers)}
    assert results["Content-Security-Policy"] == "strong"
    assert results["X-Frame-Options"] == "strong"
    assert results["X-Content-Type-Options"] == "strong"
    assert results["Strict-Transport-Security"] == "strong"


def test_weak_hsts_short_max_age():
    headers = {"Strict-Transport-Security": "max-age=60"}
    results = {r["name"]: r["status"] for r in analyze_headers(headers)}
    assert results["Strict-Transport-Security"] == "weak"
