"""SMS templates and ThriveVas console/live adapters."""
from __future__ import annotations

import os
import re
import time
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from datetime import datetime, timezone

SMS_MODE = os.getenv("SMS_MODE", "console").lower()
THRIVEVAS_API_KEY = os.getenv("THRIVEVAS_API_KEY", "")
THRIVEVAS_SENDER_ID = os.getenv("THRIVEVAS_SENDER_ID", "ThriveVas")
THRIVEVAS_API_BASE_URL = os.getenv("THRIVEVAS_API_BASE_URL", "https://sms.thrivevas.com/v1").rstrip("/")
THRIVEVAS_CALLBACK_URL = os.getenv("THRIVEVAS_CALLBACK_URL", "")
SMS_ALLOWED_RECIPIENTS = {
    re.sub(r"\D", "", number)
    for number in os.getenv("SMS_ALLOWED_RECIPIENTS", "").split(",")
    if number.strip()
}
SMS_LIVE_READY = bool(THRIVEVAS_API_KEY and THRIVEVAS_API_BASE_URL and SMS_ALLOWED_RECIPIENTS)

TEMPLATES = {
    "invite": "Hi {first}, {org} invites you to defend your project {repo}. Start within 72h: {link}",
    "otp": "Your Defend It code is {otp}. It expires in 10 minutes. Don't share it.",
    "reminder": "Reminder: your {org} defence for {repo} closes in 24h. {link}",
    "candidate_done": "Done! Your defence for {org} is submitted. They'll be in touch. Thanks, {first}.",
    "recruiter_done": "{name} defended {repo}: {score}/100 ({band}). Review: {evidence_link}",
    "ingest_failed": "We couldn't read {repo}. Make it public or reply to {org} with another link.",
}

# Process-local event log is for the hackathon demo only; production needs durable storage.
SMS_LOG: list[dict] = []
LAST_SEND: dict[str, list[float]] = {}


class ThriveVasProvider:
    """ThriveVas single-message API client."""

    def send(self, to: str, message: str) -> dict:
        if not SMS_LIVE_READY:
            raise RuntimeError("Live SMS requires THRIVEVAS_API_KEY and at least one SMS_ALLOWED_RECIPIENTS number.")
        recipient = re.sub(r"\D", "", to)
        if recipient not in SMS_ALLOWED_RECIPIENTS:
            raise ValueError("This recipient is not on the configured live SMS test allowlist.")
        payload = {"message": message, "msisdn": to, "sender_id": THRIVEVAS_SENDER_ID}
        if THRIVEVAS_CALLBACK_URL:
            payload["callback_url"] = THRIVEVAS_CALLBACK_URL

        last_error = "Provider request failed."
        for attempt, delay in enumerate((0, 5, 30), start=1):
            if delay:
                time.sleep(delay)
            request = Request(
                f"{THRIVEVAS_API_BASE_URL}/message/send",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-api-key": THRIVEVAS_API_KEY},
                method="POST",
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status_code = response.status
                    try:
                        data = json.loads(response.read().decode("utf-8"))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        data = {"message": "Provider returned a non-JSON response."}
                event = {
                    "to": to,
                    "template": "provider_send",
                    "status": "accepted" if 200 <= status_code < 300 else "failed",
                    "attempt": attempt,
                    "http_status": status_code,
                    "transaction_id": data.get("transaction_id"),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                SMS_LOG.append(event)
                if 200 <= status_code < 300:
                    return {
                        "status": "accepted",
                        "message": data.get("message", "SMS accepted by ThriveVas."),
                        "transaction_id": data.get("transaction_id"),
                        "to": to,
                    }
                last_error = f"ThriveVas returned HTTP {status_code}: {data.get('message', 'request failed')}"
                if status_code < 500 and status_code != 429:
                    raise RuntimeError(last_error)
            except HTTPError as exc:
                try:
                    error_data = json.loads(exc.read().decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    error_data = {"message": "request failed"}
                SMS_LOG.append({"to": to, "template": "provider_send", "status": "failed", "attempt": attempt, "http_status": exc.code, "created_at": datetime.now(timezone.utc).isoformat()})
                last_error = f"ThriveVas returned HTTP {exc.code}: {error_data.get('message', 'request failed')}"
                if exc.code < 500 and exc.code != 429:
                    raise RuntimeError(last_error) from exc
            except (URLError, TimeoutError, OSError) as exc:
                last_error = f"Could not connect to ThriveVas: {exc.__class__.__name__}."
        raise RuntimeError(last_error)


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("0") and len(digits) == 10:
        return "+254" + digits[1:]
    if digits.startswith("254") and len(digits) == 12:
        return "+" + digits
    if phone.startswith("+") and 8 <= len(digits) <= 15:
        return "+" + digits
    raise ValueError("Use a valid international phone number, for example +254712345678.")


def render_message(template: str, values: dict) -> str:
    if template not in TEMPLATES:
        raise ValueError("Unknown SMS template.")
    try:
        return TEMPLATES[template].format(**values)
    except KeyError as exc:
        raise ValueError(f"Missing template value: {exc.args[0]}") from exc


def send_sms(to: str, template: str, values: dict) -> dict:
    """Format an SMS and send it in console or live mode."""
    phone = normalize_phone(to)
    message = render_message(template, values)
    if len(message) > 320:
        raise ValueError("SMS message exceeds the 320-character safety limit.")
    if template == "otp" or SMS_MODE == "live":
        now = time.time()
        recent = [stamp for stamp in LAST_SEND.get(phone, []) if now - stamp < 3600]
        if recent and now - recent[-1] < 60:
            raise ValueError("Please wait 60 seconds before sending another SMS to this number.")
        if len(recent) >= 5:
            raise ValueError("Too many SMS messages sent to this number. Try again in an hour.")
        recent.append(now)
        LAST_SEND[phone] = recent

    if SMS_MODE == "live":
        return ThriveVasProvider().send(phone, message)
    if SMS_MODE != "console":
        raise RuntimeError("SMS_MODE must be either 'console' or 'live'.")

    event = {
        "to": phone,
        "template": template,
        "message": message,
        "status": "console",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    SMS_LOG.append(event)
    print(f"[SMS console] {phone}: {message}")
    return {"status": "console", "template": template, "message": message, "to": phone}
