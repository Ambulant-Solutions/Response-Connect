from __future__ import annotations

import smtplib
from collections.abc import Iterable
from email.message import EmailMessage
from email.utils import formataddr, parseaddr

import uuid

from app.blueprints.jobs.models import Job

from flask import current_app


class EmailConfigurationError(RuntimeError):
    """Raised when outgoing email has not been configured correctly."""


class EmailDeliveryError(RuntimeError):
    """Raised when an email cannot be delivered."""


def send_email(
    *,
    to: str | Iterable[str],
    subject: str,
    text_body: str,
    html_body: str | None = None,
    cc: str | Iterable[str] | None = None,
    bcc: str | Iterable[str] | None = None,
    reply_to: str | None = None,
    sender: str | None = None,
) -> dict[str, object]:
    """
    Send an email through the configured SMTP server.

    This function performs the actual network operation. Application code
    should normally create an EMAIL_SEND job rather than call it directly.
    """

    recipients = _normalise_addresses(to, field_name="to")
    cc_recipients = _normalise_addresses(cc, field_name="cc")
    bcc_recipients = _normalise_addresses(bcc, field_name="bcc")

    if not recipients:
        raise ValueError("At least one recipient email address is required.")

    subject = subject.strip()

    if not subject:
        raise ValueError("An email subject is required.")

    if not text_body or not text_body.strip():
        raise ValueError("A plain-text email body is required.")

    settings = _get_mail_settings()

    sender_address = sender or settings["default_sender"]
    _validate_address(sender_address, field_name="sender")

    if reply_to:
        _validate_address(reply_to, field_name="reply_to")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender_address
    message["To"] = ", ".join(recipients)

    if cc_recipients:
        message["Cc"] = ", ".join(cc_recipients)

    if reply_to:
        message["Reply-To"] = reply_to

    message.set_content(text_body)

    if html_body:
        message.add_alternative(html_body, subtype="html")

    envelope_recipients = list(
        dict.fromkeys(
            recipients
            + cc_recipients
            + bcc_recipients
        )
    )

    try:
        if settings["use_ssl"]:
            with smtplib.SMTP_SSL(
                settings["server"],
                settings["port"],
                timeout=settings["timeout"],
            ) as smtp:
                _authenticate(smtp, settings)
                smtp.send_message(
                    message,
                    to_addrs=envelope_recipients,
                )
        else:
            with smtplib.SMTP(
                settings["server"],
                settings["port"],
                timeout=settings["timeout"],
            ) as smtp:
                smtp.ehlo()

                if settings["use_tls"]:
                    smtp.starttls()
                    smtp.ehlo()

                _authenticate(smtp, settings)
                smtp.send_message(
                    message,
                    to_addrs=envelope_recipients,
                )

    except (
        OSError,
        smtplib.SMTPException,
    ) as exc:
        raise EmailDeliveryError(
            f"SMTP delivery failed: {exc}"
        ) from exc

    return {
        "accepted_recipients": envelope_recipients,
        "recipient_count": len(envelope_recipients),
        "subject": subject,
    }


def _get_mail_settings() -> dict[str, object]:
    """Read and validate outgoing email configuration."""

    server = current_app.config.get("MAIL_SERVER", "").strip()
    port = current_app.config.get("MAIL_PORT", 587)
    username = current_app.config.get("MAIL_USERNAME", "").strip()
    password = current_app.config.get("MAIL_PASSWORD", "")
    use_tls = bool(current_app.config.get("MAIL_USE_TLS", True))
    use_ssl = bool(current_app.config.get("MAIL_USE_SSL", False))
    default_sender = current_app.config.get(
        "MAIL_DEFAULT_SENDER",
        "",
    ).strip()
    timeout = current_app.config.get("MAIL_TIMEOUT", 30)

    if not server:
        raise EmailConfigurationError(
            "MAIL_SERVER has not been configured."
        )

    if use_tls and use_ssl:
        raise EmailConfigurationError(
            "MAIL_USE_TLS and MAIL_USE_SSL cannot both be enabled."
        )

    if not default_sender:
        raise EmailConfigurationError(
            "MAIL_DEFAULT_SENDER has not been configured."
        )

    if bool(username) != bool(password):
        raise EmailConfigurationError(
            "MAIL_USERNAME and MAIL_PASSWORD must either both be set "
            "or both be empty."
        )

    return {
        "server": server,
        "port": int(port),
        "username": username,
        "password": password,
        "use_tls": use_tls,
        "use_ssl": use_ssl,
        "default_sender": default_sender,
        "timeout": int(timeout),
    }


def _authenticate(
    smtp: smtplib.SMTP,
    settings: dict[str, object],
) -> None:
    """Authenticate where SMTP credentials have been configured."""

    username = str(settings["username"])
    password = str(settings["password"])

    if username:
        smtp.login(username, password)


def _normalise_addresses(
    value: str | Iterable[str] | None,
    *,
    field_name: str,
) -> list[str]:
    """Convert an address or iterable of addresses into a validated list."""

    if value is None:
        return []

    if isinstance(value, str):
        addresses = [value]
    else:
        addresses = list(value)

    normalised: list[str] = []

    for address in addresses:
        address = str(address).strip()

        if not address:
            continue

        _validate_address(address, field_name=field_name)
        normalised.append(address)

    return list(dict.fromkeys(normalised))


def _validate_address(address: str, *, field_name: str) -> None:
    """
    Perform basic address validation.

    SMTP servers remain responsible for authoritative mailbox validation.
    """

    _, parsed_address = parseaddr(address)

    if (
        not parsed_address
        or "@" not in parsed_address
        or parsed_address.startswith("@")
        or parsed_address.endswith("@")
    ):
        raise ValueError(
            f"Invalid email address in {field_name}: {address!r}"
        )

def queue_email(
    *,
    to: str | Iterable[str],
    subject: str,
    text_body: str,
    html_body: str | None = None,
    cc: str | Iterable[str] | None = None,
    bcc: str | Iterable[str] | None = None,
    reply_to: str | None = None,
    sender: str | None = None,
    created_by_id=None,
    priority: int = 5,
) -> Job:
    """Create and queue an outgoing email job."""

    # Import locally to prevent the email service and job task modules from
    # creating circular imports during worker startup.
    from app.blueprints.jobs.models import JobType
    from app.blueprints.jobs.services import create_and_queue_job

    payload = {
        "to": _payload_address_value(to),
        "subject": subject,
        "text_body": text_body,
    }

    if html_body is not None:
        payload["html_body"] = html_body

    if cc is not None:
        payload["cc"] = _payload_address_value(cc)

    if bcc is not None:
        payload["bcc"] = _payload_address_value(bcc)

    if reply_to is not None:
        payload["reply_to"] = reply_to

    if sender is not None:
        payload["sender"] = sender

    return create_and_queue_job(
        job_type=JobType.EMAIL_SEND,
        payload=payload,
        created_by_id=created_by_id,
        priority=priority,
    )


def _payload_address_value(
    value: str | Iterable[str],
) -> str | list[str]:
    """Convert iterable address values into JSON-compatible payload values."""

    if isinstance(value, str):
        return value

    return list(value)