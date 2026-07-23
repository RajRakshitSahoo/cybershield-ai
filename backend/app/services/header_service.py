"""Analyzes HTTP response headers for common security header best-practices."""

HEADER_CHECKS = [
    ("Content-Security-Policy", "content-security-policy"),
    ("X-Frame-Options", "x-frame-options"),
    ("X-Content-Type-Options", "x-content-type-options"),
    ("Referrer-Policy", "referrer-policy"),
    ("Permissions-Policy", "permissions-policy"),
    ("Strict-Transport-Security", "strict-transport-security"),
    ("X-XSS-Protection", "x-xss-protection"),
]


def _grade(name: str, value: str) -> str:
    v = value.lower()
    if name == "Content-Security-Policy":
        return "strong" if "default-src" in v or "script-src" in v else "weak"
    if name == "X-Frame-Options":
        return "strong" if v in ("deny", "sameorigin") else "weak"
    if name == "X-Content-Type-Options":
        return "strong" if v == "nosniff" else "weak"
    if name == "Referrer-Policy":
        return "strong" if v in (
            "no-referrer", "strict-origin", "strict-origin-when-cross-origin",
            "same-origin",
        ) else "weak"
    if name == "Permissions-Policy":
        return "strong" if len(v) > 0 else "weak"
    if name == "Strict-Transport-Security":
        return "strong" if "max-age" in v and int(_extract_max_age(v) or 0) >= 15552000 else "weak"
    if name == "X-XSS-Protection":
        return "strong" if v.startswith("1") else "weak"
    return "present"


def _extract_max_age(v: str):
    for part in v.split(";"):
        part = part.strip()
        if part.startswith("max-age="):
            try:
                return int(part.split("=", 1)[1])
            except ValueError:
                return None
    return None


def analyze_headers(headers: dict) -> list:
    headers = headers or {}
    lower_map = {k.lower(): v for k, v in headers.items()}
    results = []
    for display_name, key in HEADER_CHECKS:
        value = lower_map.get(key)
        if value is None:
            results.append({"name": display_name, "status": "missing", "value": None})
        else:
            results.append({"name": display_name, "status": _grade(display_name, value), "value": value})
    return results
