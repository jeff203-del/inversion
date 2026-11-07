"""Small API foundation for the Defend It demo."""
from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from sms import SMS_LOG, SMS_LIVE_READY, SMS_MODE, send_sms

app = FastAPI(title="Defend It API", version="0.1.0", description="Evidence-backed developer ownership assessment")
allowed_origins = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080").split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class RoundScores(BaseModel):
    impostor: float = Field(ge=0, le=1)
    explain: float = Field(ge=0, le=1)
    bug: float = Field(ge=0, le=1)
    extend: float = Field(ge=0, le=1)
    scored_items: int = Field(default=4, ge=1)


class InviteRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    organisation: str = Field(min_length=1, max_length=80)
    project: str = Field(min_length=1, max_length=100)
    link: str = Field(min_length=8, max_length=300)
    phone: str = Field(min_length=8, max_length=20)


class DeliveryReport(BaseModel):
    msisdn: str = Field(min_length=8, max_length=20)
    status: int
    status_description: str = ""
    country: str = ""
    network: str = ""
    transaction_id: str = Field(min_length=1, max_length=100)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "defend-it-api", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/config")
def config() -> dict:
    return {"sms_mode": SMS_MODE, "live_sms_ready": SMS_LIVE_READY, "message": "Invite and score APIs are connected; campaign storage remains demo data."}


@app.post("/api/score")
def score_rounds(scores: RoundScores) -> dict:
    weights = {"impostor": 0.15, "explain": 0.35, "bug": 0.30, "extend": 0.20}
    value = round(100 * sum(getattr(scores, key) * weight for key, weight in weights.items()))
    band: Literal["Strong ownership", "Likely owner", "Unclear: needs a human conversation", "Low evidence of ownership"]
    if value >= 80:
        band = "Strong ownership"
    elif value >= 60:
        band = "Likely owner"
    elif value >= 40:
        band = "Unclear: needs a human conversation"
    else:
        band = "Low evidence of ownership"
    return {"ownership_score": value, "band": band, "confidence_note": f"Based on {scores.scored_items} scored items", "decision_support_only": True}


@app.post("/api/demo/invite")
def demo_invite(invite: InviteRequest) -> dict:
    try:
        return send_sms(
            invite.phone,
            "invite",
            {"first": invite.first_name, "org": invite.organisation, "repo": invite.project, "link": invite.link},
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/webhooks/sms")
def sms_delivery_report(report: DeliveryReport) -> dict:
    """Update the in-memory demo log when ThriveVas calls back with a DLR."""
    for event in reversed(SMS_LOG):
        if event.get("transaction_id") == report.transaction_id:
            event.update({
                "delivery_status": report.status,
                "delivery_description": report.status_description,
                "network": report.network,
                "country": report.country,
                "delivery_received_at": datetime.now(timezone.utc).isoformat(),
            })
            return {"status": "recorded"}
    return {"status": "unmatched", "transaction_id": report.transaction_id}
