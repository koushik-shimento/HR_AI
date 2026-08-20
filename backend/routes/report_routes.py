"""HTTP routes for recruitment reports and report delivery."""

from __future__ import annotations

import base64
import binascii
import logging
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from flask import Blueprint, jsonify, request

from email_utils import is_valid_email, normalize_email
from services.auth_service import api_login_required
from services.report_service import reports_payload

logger = logging.getLogger(__name__)
report_bp = Blueprint("report_routes", __name__)

DEFAULT_SUBJECT = "Recruitment Report"
DEFAULT_ATTACHMENT_NAME = "report.pdf"
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class SmtpSettings:
    """Validated SMTP settings loaded from the environment."""

    host: str
    port: int
    username: str
    password: str
    from_email: str

    @classmethod
    def from_environment(cls) -> "SmtpSettings":
        username = (os.getenv("SMTP_USER") or "").strip()
        password = (os.getenv("SMTP_PASS") or os.getenv("SMTP_PASSWORD") or "").strip()
        if not username or not password:
            raise RuntimeError("SMTP is not configured.")

        try:
            port = int(os.getenv("SMTP_PORT", "587"))
        except ValueError as exc:
            raise RuntimeError("SMTP_PORT must be an integer.") from exc

        return cls(
            host=(os.getenv("SMTP_HOST") or os.getenv("SMTP_SERVER") or "smtp.gmail.com").strip(),
            port=port,
            username=username,
            password=password,
            from_email=(os.getenv("DEFAULT_FROM_EMAIL") or username).strip(),
        )


def _decode_attachment(attachment: dict[str, Any]) -> tuple[str, bytes] | None:
    encoded_content = attachment.get("content")
    if not encoded_content:
        return None
    if not isinstance(encoded_content, str):
        raise ValueError("Attachment content must be base64 text.")

    try:
        content = base64.b64decode(encoded_content, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Attachment content is not valid base64.") from exc
    if len(content) > MAX_ATTACHMENT_BYTES:
        raise ValueError("Attachment exceeds the 10 MB limit.")

    filename = os.path.basename(str(attachment.get("filename") or DEFAULT_ATTACHMENT_NAME))
    return filename, content


def _build_message(data: dict[str, Any], settings: SmtpSettings) -> MIMEMultipart:
    recipient = normalize_email(data.get("recipient"))
    if not is_valid_email(recipient):
        raise ValueError("A valid recipient email is required.")

    message = MIMEMultipart()
    message["From"] = settings.from_email
    message["To"] = recipient
    message["Subject"] = str(data.get("subject") or DEFAULT_SUBJECT).strip()

    user_message = str(data.get("message") or "").strip()
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    body = (
        f"{user_message}\n\n---\n"
        "This report was generated automatically by Recruitment Assist.\n"
        f"Generated on: {generated_at}\n\n"
        "This is an automated message. Please do not reply."
    )
    message.attach(MIMEText(body, "plain", "utf-8"))

    decoded_attachment = _decode_attachment(data.get("attachment") or {})
    if decoded_attachment:
        filename, content = decoded_attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(part)
    return message


def _send_message(message: MIMEMultipart, settings: SmtpSettings) -> None:
    with smtplib.SMTP(settings.host, settings.port, timeout=20) as server:
        server.starttls()
        server.login(settings.username, settings.password)
        server.send_message(message)


@report_bp.post("/api/report/email")
@api_login_required
def send_report_email():
    """Send a generated report to a validated email address."""
    data = request.get_json(silent=True) or {}
    try:
        settings = SmtpSettings.from_environment()
        message = _build_message(data, settings)
        _send_message(message, settings)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        logger.warning("Report email configuration error: %s", exc)
        return jsonify({"error": str(exc)}), 503
    except smtplib.SMTPAuthenticationError:
        logger.exception("SMTP authentication failed while sending a report")
        return jsonify({"error": "Email delivery authentication failed."}), 503
    except (smtplib.SMTPException, OSError):
        logger.exception("SMTP delivery failed while sending a report")
        return jsonify({"error": "Email delivery failed. Please try again later."}), 503

    return jsonify({"success": True, "message": f"Report sent to {message['To']}."})


@report_bp.get("/api/reports")
@api_login_required
def api_reports():
    """Return report data for dashboards and exports."""
    return jsonify(reports_payload())
