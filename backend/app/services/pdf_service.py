"""Generates a professional PDF security report for a saved analysis."""
import io
from datetime import datetime, timezone

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage,
)

VERDICT_COLORS = {
    "Safe": colors.HexColor("#16a34a"),
    "Suspicious": colors.HexColor("#f59e0b"),
    "Phishing": colors.HexColor("#dc2626"),
}


def _qr_image(url: str) -> RLImage:
    qr = qrcode.QRCode(box_size=4, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return RLImage(buf, width=2.5 * cm, height=2.5 * cm)


def generate_pdf_report(report: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=colors.HexColor("#0f172a"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=colors.HexColor("#1e293b"))
    body = styles["BodyText"]

    verdict = report["ai_prediction"]["verdict"]
    verdict_color = VERDICT_COLORS.get(verdict, colors.grey)

    elements = [
        Paragraph("CyberShield AI &ndash; Security Analysis Report", title_style),
        Spacer(1, 6),
        Paragraph(f"Target: <b>{report['url']}</b>", body),
        Paragraph(f"Scanned at: {report['scanned_at']}", body),
        Spacer(1, 12),
        Paragraph(f"<b>Verdict: <font color='{verdict_color.hexval()}'>{verdict}</font></b> "
                  f"&mdash; Risk Score {report['ai_prediction']['risk_score']}/100 "
                  f"(confidence {report['ai_prediction']['confidence']}%)", h2),
        Spacer(1, 6),
    ]

    reasons = report["ai_prediction"].get("reasons", [])
    if reasons:
        elements.append(Paragraph("Why AI reached this verdict:", styles["Heading3"]))
        for r in reasons:
            elements.append(Paragraph(f"&bull; {r}", body))
        elements.append(Spacer(1, 10))

    di = report["domain_info"]
    domain_rows = [
        ["Domain", di.get("domain")], ["IP Address", di.get("ip_address")],
        ["Registrar", di.get("registrar")], ["Created", di.get("creation_date")],
        ["Expires", di.get("expiry_date")], ["Domain Age (days)", di.get("domain_age_days")],
        ["Hosting Provider", di.get("hosting_provider")], ["Country", di.get("country")],
        ["CDN", di.get("cdn_provider")],
    ]
    elements.append(Paragraph("Domain Intelligence", styles["Heading3"]))
    t = Table(domain_rows, colWidths=[5 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    ssl_info = report["ssl_info"]
    ssl_rows = [
        ["HTTPS", str(ssl_info.get("https"))], ["Valid Certificate", str(ssl_info.get("valid"))],
        ["Issuer", ssl_info.get("issuer")], ["TLS Version", ssl_info.get("tls_version")],
        ["Days Remaining", ssl_info.get("days_remaining")], ["HSTS Enabled", str(ssl_info.get("hsts"))],
    ]
    elements.append(Paragraph("SSL / TLS Analysis", styles["Heading3"]))
    t2 = Table(ssl_rows, colWidths=[5 * cm, 10 * cm])
    t2.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 10))

    header_rows = [["Header", "Status"]] + [
        [h["name"], h["status"]] for h in report.get("security_headers", [])
    ]
    elements.append(Paragraph("Security Headers", styles["Heading3"]))
    t3 = Table(header_rows, colWidths=[7 * cm, 8 * cm])
    t3.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ]))
    elements.append(t3)
    elements.append(Spacer(1, 10))

    rep_rows = [["Source", "Status", "Detail"]] + [
        [r["source"], r["status"], r.get("detail") or ""] for r in report.get("reputation", [])
    ]
    elements.append(Paragraph("Reputation / Blacklist Checks", styles["Heading3"]))
    t4 = Table(rep_rows, colWidths=[4.5 * cm, 3.5 * cm, 7 * cm])
    t4.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ]))
    elements.append(t4)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Recommendations", styles["Heading3"]))
    recs = _recommendations(report)
    for r in recs:
        elements.append(Paragraph(f"&bull; {r}", body))
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("Scan this QR code to revisit the live report:", body))
    elements.append(_qr_image(report["url"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        f"Generated by CyberShield AI on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        ParagraphStyle("Footer", parent=body, textColor=colors.grey, fontSize=8),
    ))

    doc.build(elements)
    buf.seek(0)
    return buf.read()


def _recommendations(report: dict) -> list:
    recs = []
    if not report["ssl_info"].get("https"):
        recs.append("Enable HTTPS with a valid TLS certificate before trusting this site with credentials.")
    if report["ssl_info"].get("days_remaining") is not None and report["ssl_info"]["days_remaining"] < 30:
        recs.append("TLS certificate is close to expiry -- renew soon.")
    missing_headers = [h["name"] for h in report.get("security_headers", []) if h["status"] == "missing"]
    if missing_headers:
        recs.append(f"Add missing security headers: {', '.join(missing_headers)}.")
    if report["ai_prediction"]["verdict"] != "Safe":
        recs.append("Avoid entering credentials or payment details on this site until verified safe.")
        recs.append("Report this URL to your organization's security team if received via email or SMS.")
    if not recs:
        recs.append("No immediate action required -- continue routine monitoring.")
    return recs
