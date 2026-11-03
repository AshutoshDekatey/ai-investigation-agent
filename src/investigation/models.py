from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

class Transaction(StrictModel):
    id: str
    status: Literal["settled", "failed", "pending", "unknown"]
    amount: Decimal = Field(gt=0)
    currency: str
    updated_at: str
    ledger_reference: str

class Policy(StrictModel):
    id: str
    title: str
    text: str

class Evidence(StrictModel):
    source: str
    detail: str

class Investigation(StrictModel):
    transaction_id: str
    status: Literal["settled", "failed", "pending", "unknown", "missing"]
    evidence: tuple[Evidence, ...]
    recommendation: str
    uncertainty: tuple[str, ...]
    human_review: bool = True
    mode: Literal["offline", "llm"]
    policy_ids: tuple[str, ...]
    llm_summary: str | None = None

class LLMSummary(StrictModel):
    summary: str = Field(min_length=1, max_length=2000)
