"""
Lightweight technology fingerprinting via regex signatures over HTML source
and response headers. Not exhaustive (that's what Wappalyzer/BuiltWith are
for) but covers the common stacks called out in the project brief.
"""
import re

SIGNATURES = {
    "frontend": {
        "React": [r"react(-dom)?[.\-]", r"__REACT_DEVTOOLS"],
        "Angular": [r"ng-version", r"angular\.js"],
        "Vue": [r"__vue__", r"vue\.js", r"data-v-"],
        "Next.js": [r"__NEXT_DATA__", r"/_next/static"],
        "jQuery": [r"jquery(\.min)?\.js"],
        "Bootstrap": [r"bootstrap(\.min)?\.css"],
        "Tailwind": [r"tailwind(\.min)?\.css", r"tw-"],
    },
    "cms": {
        "WordPress": [r"wp-content", r"wp-includes"],
        "Drupal": [r"sites/default/files", r"Drupal\.settings"],
        "Joomla": [r"/media/jui/", r"Joomla!"],
    },
    "backend": {
        "PHP": [r"\.php(\?|\"|')", r"X-Powered-By:\s*PHP"],
        "Laravel": [r"laravel_session"],
        "Node.js": [r"X-Powered-By:\s*Express"],
        "ASP.NET": [r"__VIEWSTATE", r"X-AspNet-Version"],
    },
    "server": {
        "Apache": [r"Server:\s*Apache"],
        "Nginx": [r"Server:\s*nginx"],
        "IIS": [r"Server:\s*Microsoft-IIS"],
    },
    "cdn": {
        "Cloudflare": [r"Server:\s*cloudflare", r"__cfduid", r"cf-ray"],
        "Fastly": [r"Server:\s*Fastly", r"x-served-by:\s*cache"],
        "Akamai": [r"akamai"],
    },
    "analytics": {
        "Google Analytics": [r"google-analytics\.com", r"gtag\("],
        "Google Tag Manager": [r"googletagmanager\.com"],
        "Hotjar": [r"hotjar"],
    },
}


def detect_technologies(html: str, headers: dict) -> dict:
    html = html or ""
    header_blob = "\n".join(f"{k}: {v}" for k, v in (headers or {}).items())
    haystack = html + "\n" + header_blob

    result = {k: [] for k in SIGNATURES}
    result["other"] = []

    for category, techs in SIGNATURES.items():
        for tech_name, patterns in techs.items():
            for pattern in patterns:
                if re.search(pattern, haystack, re.IGNORECASE):
                    result[category].append(tech_name)
                    break
    for category in result:
        result[category] = sorted(set(result[category]))
    return result
