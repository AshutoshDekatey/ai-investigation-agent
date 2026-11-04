from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")

class Intake(Model):
    transaction_id: str = Field(pattern=r"^[A-Za-z0-9-]{1,64}$")
    question: str = Field(default="Money debited but merchant did not receive it", max_length=1000)
    as_of: date = date(2026, 11, 4)

    @field_validator("question")
    @classmethod
    def redact(cls, value):
        import re
        value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL REDACTED]", value)
        value = re.sub(r"(?i)(bearer\s+\S+|sk-[A-Za-z0-9_-]+)", "[SECRET REDACTED]", value)
        return re.sub(r"\b\d{8,}\b", "[NUMBER REDACTED]", value)

class Transaction(Model):
    id: str
    status: Literal["settled", "failed", "pending", "timeout", "unknown"]
    amount: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    recorded_at: str
    policy_topic: str | None = None

class Ledger(Model):
    status: Literal["settled", "not_settled", "pending", "unknown"]
    amount: Decimal | None = None
    currency: str
    debit_count: int = Field(ge=0)
    reference: str

class Citation(Model):
    chunk_id: str
    policy_id: str
    version: int
    quote: str
    source: str

class ToolEvent(Model):
    tool: str
    attempt: int
    outcome: Literal["ok", "missing", "timeout", "unavailable", "invalid"]

class Report(Model):
    investigation_id: str
    transaction_id: str
    outcome: Literal["confirmed_success", "confirmed_failure", "pending_settlement", "duplicate_debit", "uncertain"]
    recommendation: str
    human_review: Literal[True] = True
    route: Literal["analyst", "reconciliation"]
    uncertainty: list[str]
    citations: list[Citation]
    records: dict
    tool_events: list[ToolEvent]
    retrieved: list[Citation]
    latency_ms: float
    embedding_mode: str
    llm: dict | None = None
