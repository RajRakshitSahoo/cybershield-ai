"""SSL/TLS certificate inspection using the standard library `ssl` socket API."""
import socket
import ssl
from datetime import datetime, timezone


def _parse_cert_date(value: str):
    # Certificates use e.g. 'Jun  1 12:00:00 2026 GMT'
    return datetime.strptime(value, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)


def analyze_ssl(hostname: str, port: int = 443) -> dict:
    result = {
        "https": False, "valid": False, "issuer": None, "subject": None,
        "tls_version": None, "expiry_date": None, "days_remaining": None,
        "hsts": False, "error": None,
    }
    context = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=6) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                result["https"] = True
                result["tls_version"] = ssock.version()
                issuer = dict(x[0] for x in cert.get("issuer", []))
                subject = dict(x[0] for x in cert.get("subject", []))
                result["issuer"] = issuer.get("organizationName") or issuer.get("commonName")
                result["subject"] = subject.get("commonName")
                not_after = cert.get("notAfter")
                if not_after:
                    expiry = _parse_cert_date(not_after)
                    result["expiry_date"] = expiry.isoformat()
                    result["days_remaining"] = (expiry - datetime.now(timezone.utc)).days
                    result["valid"] = result["days_remaining"] > 0
    except ssl.SSLCertVerificationError as e:
        result["error"] = f"Certificate verification failed: {e.verify_message}"
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as e:
        result["error"] = f"Could not establish TLS connection: {e}"
    except Exception as e:  # noqa: BLE001
        result["error"] = str(e)
    return result


def check_hsts(headers: dict) -> bool:
    keys = {k.lower(): v for k, v in (headers or {}).items()}
    return "strict-transport-security" in keys
