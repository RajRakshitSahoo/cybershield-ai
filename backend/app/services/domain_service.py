"""
Domain Intelligence + DNS analysis.

Uses:
 - `whois` (python-whois) for registrar / creation / expiry data
 - `dns.resolver` (dnspython) for A/AAAA/MX/TXT/NS/CNAME/SOA/DNSSEC records
 - `ip-api.com` (free, no key required) for IP geolocation / ASN / org / hosting
 - `socket` for basic A/AAAA resolution fallback
"""
import socket
from datetime import datetime, timezone
from typing import Optional

import dns.resolver
import requests
import tldextract
import whois as pywhois
from bs4 import BeautifulSoup

CDN_ASN_HINTS = {
    "cloudflare": "Cloudflare",
    "akamai": "Akamai",
    "fastly": "Fastly",
    "amazon": "Amazon CloudFront",
    "google": "Google Cloud CDN",
    "microsoft": "Azure CDN",
}

REQUEST_TIMEOUT = 6


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def resolve_records(hostname: str) -> dict:
    records = {"a": [], "aaaa": [], "mx": [], "txt": [], "ns": [], "cname": [], "soa": [], "dnssec": False}
    resolver = dns.resolver.Resolver()
    resolver.timeout = 4
    resolver.lifetime = 4

    def q(rtype):
        try:
            return [str(r).strip() for r in resolver.resolve(hostname, rtype)]
        except Exception:
            return []

    records["a"] = q("A")
    records["aaaa"] = q("AAAA")
    records["mx"] = q("MX")
    records["txt"] = q("TXT")
    records["ns"] = q("NS")
    records["soa"] = q("SOA")
    try:
        cname_answer = resolver.resolve(hostname, "CNAME")
        records["cname"] = [str(r).strip() for r in cname_answer]
    except Exception:
        records["cname"] = []
    try:
        ans = resolver.resolve(hostname, "DNSKEY")
        records["dnssec"] = len(ans) > 0
    except Exception:
        records["dnssec"] = False
    return records


def get_whois(hostname: str) -> dict:
    result = {
        "registrar": None, "creation_date": None, "expiry_date": None,
        "updated_date": None, "name_servers": [], "owner": None,
        "privacy_protection": None, "status": None, "country": None,
        "domain_age_days": None,
    }
    data = _safe(lambda: pywhois.whois(hostname))
    if not data:
        return result

    def first(v):
        if isinstance(v, list):
            return v[0] if v else None
        return v

    creation = first(getattr(data, "creation_date", None))
    expiry = first(getattr(data, "expiration_date", None))
    updated = first(getattr(data, "updated_date", None))

    result["registrar"] = getattr(data, "registrar", None)
    result["creation_date"] = creation.isoformat() if isinstance(creation, datetime) else creation
    result["expiry_date"] = expiry.isoformat() if isinstance(expiry, datetime) else expiry
    result["updated_date"] = updated.isoformat() if isinstance(updated, datetime) else updated
    result["name_servers"] = [ns.lower() for ns in (getattr(data, "name_servers", None) or [])]
    result["owner"] = getattr(data, "org", None) or getattr(data, "name", None)
    result["status"] = first(getattr(data, "status", None))
    result["country"] = getattr(data, "country", None)

    if isinstance(creation, datetime):
        if creation.tzinfo is None:
            creation = creation.replace(tzinfo=timezone.utc)
        result["domain_age_days"] = (datetime.now(timezone.utc) - creation).days

    return result


def get_ip_geo(ip: str) -> dict:
    """Free ip-api.com lookup: country, city, timezone, ASN, org/hosting provider."""
    default = {"country": None, "city": None, "timezone": None, "asn": None,
               "organization": None, "hosting_provider": None}
    if not ip:
        return default
    resp = _safe(lambda: requests.get(
        f"http://ip-api.com/json/{ip}?fields=status,country,city,timezone,isp,org,as",
        timeout=REQUEST_TIMEOUT,
    ))
    if not resp:
        return default
    data = _safe(resp.json, {})
    if data.get("status") != "success":
        return default
    return {
        "country": data.get("country"),
        "city": data.get("city"),
        "timezone": data.get("timezone"),
        "asn": data.get("as"),
        "organization": data.get("org") or data.get("isp"),
        "hosting_provider": data.get("isp"),
    }


def detect_cdn(name_servers, org: Optional[str]) -> Optional[str]:
    haystack = " ".join(name_servers or []).lower() + " " + (org or "").lower()
    for hint, label in CDN_ASN_HINTS.items():
        if hint in haystack:
            return label
    return None


def get_page_meta(url: str) -> dict:
    """Fetches the page to pull <title> and favicon for the report header."""
    result = {"title": None, "favicon": None, "html": None, "headers": {}, "redirect_count": 0}
    resp = _safe(lambda: requests.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True,
                                       headers={"User-Agent": "CyberShieldAI-Scanner/1.0"}))
    if not resp:
        return result
    result["redirect_count"] = len(resp.history)
    result["headers"] = dict(resp.headers)
    soup = _safe(lambda: BeautifulSoup(resp.text, "html.parser"))
    result["html"] = resp.text[:200_000] if resp.text else None
    if soup:
        if soup.title and soup.title.string:
            result["title"] = soup.title.string.strip()
        icon = soup.find("link", rel=lambda v: v and "icon" in v.lower())
        if icon and icon.get("href"):
            href = icon["href"]
            if href.startswith("http"):
                result["favicon"] = href
            else:
                result["favicon"] = requests.compat.urljoin(url, href)
    if not result["favicon"]:
        result["favicon"] = requests.compat.urljoin(url, "/favicon.ico")
    return result


def analyze_domain(url: str) -> dict:
    ext = tldextract.extract(url)
    hostname = ".".join(p for p in [ext.subdomain, ext.domain, ext.suffix] if p) or ext.domain
    registered_domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain

    a_records = _safe(lambda: [i[4][0] for i in socket.getaddrinfo(hostname, None, socket.AF_INET)], [])
    aaaa_records = _safe(lambda: [i[4][0] for i in socket.getaddrinfo(hostname, None, socket.AF_INET6)], [])
    ip_address = a_records[0] if a_records else None
    ipv6 = aaaa_records[0] if aaaa_records else None

    dns_info = resolve_records(hostname)
    whois_info = get_whois(registered_domain)
    geo = get_ip_geo(ip_address)
    cdn = detect_cdn(dns_info.get("ns", []) or whois_info.get("name_servers", []), geo.get("organization"))

    domain_info = {
        "domain": registered_domain,
        "ip_address": ip_address,
        "ipv6": ipv6,
        "registrar": whois_info["registrar"],
        "creation_date": whois_info["creation_date"],
        "expiry_date": whois_info["expiry_date"],
        "updated_date": whois_info["updated_date"],
        "domain_age_days": whois_info["domain_age_days"],
        "name_servers": whois_info["name_servers"] or dns_info.get("ns", []),
        "hosting_provider": geo["hosting_provider"],
        "asn": geo["asn"],
        "country": geo["country"],
        "city": geo["city"],
        "timezone": geo["timezone"],
        "cdn_provider": cdn,
        "organization": geo["organization"],
    }

    whois_full = {
        "owner": whois_info["owner"],
        "registrar": whois_info["registrar"],
        "creation": whois_info["creation_date"],
        "expiration": whois_info["expiry_date"],
        "updated": whois_info["updated_date"],
        "privacy_protection": whois_info["privacy_protection"],
        "country": whois_info["country"],
        "status": whois_info["status"],
    }

    return {
        "hostname": hostname,
        "registered_domain": registered_domain,
        "domain_info": domain_info,
        "dns_info": {**dns_info, "cname": dns_info.get("cname", [])},
        "whois_full": whois_full,
    }
