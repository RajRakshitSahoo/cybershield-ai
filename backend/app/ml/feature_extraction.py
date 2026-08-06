"""
Extracts a numeric feature vector from a URL (and optionally domain-age /
HTML context) for the phishing-detection model. Kept dependency-light so it
can run both at training time (on bulk datasets) and at inference time
(on a single URL) with identical logic.
"""
import math
import re
from collections import Counter
from urllib.parse import urlparse
 
import tldextract

BRAND_KEYWORDS = [
    "paypal", "bank", "secure", "account", "update", "confirm", "login",
    "signin", "verify", "webscr", "ebay", "amazon", "apple", "microsoft",
    "google", "facebook", "instagram", "netflix", "wallet", "crypto",
    "support", "billing", "password",
]

SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "work", "loan", "gq", "ml", "cf", "tk", "ga",
    "biz", "info", "zip", "review", "country", "kim", "science",
}

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
}

FEATURE_NAMES = [
    "url_length", "num_dots", "num_hyphens", "num_digits", "num_special_chars",
    "num_subdomains", "has_https", "has_ip_address", "has_at_symbol",
    "has_double_slash_redirect", "domain_age_days", "url_entropy",
    "has_brand_keyword", "is_shortened", "suspicious_tld", "num_redirects",
    "path_length", "num_query_params", "has_port", "domain_length",
]


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def _is_ip(host: str) -> bool:
    return bool(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", host or ""))


def extract_features(url: str, domain_age_days: int = -1, num_redirects: int = 0) -> dict:
    """Returns a dict of {feature_name: value} for a single URL."""
    parsed = urlparse(url if "://" in url else f"http://{url}")
    host = parsed.netloc.split(":")[0]
    ext = tldextract.extract(url)
    registered_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain

    features = {
        "url_length": len(url),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(c.isdigit() for c in url),
        "num_special_chars": len(re.findall(r"[^a-zA-Z0-9.\-/:]", url)),
        "num_subdomains": max(len(ext.subdomain.split(".")) if ext.subdomain else 0, 0),
        "has_https": int(parsed.scheme == "https"),
        "has_ip_address": int(_is_ip(host)),
        "has_at_symbol": int("@" in url),
        "has_double_slash_redirect": int(url.rfind("//") > 7),
        "domain_age_days": domain_age_days,
        "url_entropy": round(_shannon_entropy(url), 3),
        "has_brand_keyword": int(any(b in url.lower() for b in BRAND_KEYWORDS)),
        "is_shortened": int(registered_domain.lower() in SHORTENERS),
        "suspicious_tld": int((ext.suffix or "").split(".")[-1] in SUSPICIOUS_TLDS),
        "num_redirects": num_redirects,
        "path_length": len(parsed.path or ""),
        "num_query_params": len(parsed.query.split("&")) if parsed.query else 0,
        "has_port": int(parsed.port is not None),
        "domain_length": len(registered_domain),
    }
    return features


def features_to_vector(features: dict) -> list:
    return [features[name] for name in FEATURE_NAMES]
