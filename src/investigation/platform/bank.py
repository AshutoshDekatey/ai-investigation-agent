"""Locally hosted synthetic bank: GET endpoints only; no mutation capability."""
import os
import secrets
from fastapi import FastAPI, Header, HTTPException
from .data import load_data

app = FastAPI(title="Fictional read-only banking simulator")
ROWS = load_data("bank.json")

def authorize(token):
    expected = os.getenv("BANK_API_TOKEN")
    if not expected or not token or not secrets.compare_digest(token, expected):
        raise HTTPException(401, "Bank tool authentication required")

@app.get("/health")
def health():
    return {"status": "ok", "synthetic": True}

@app.get("/transactions/{transaction_id}")
def transaction(transaction_id: str, x_bank_token: str | None = Header(default=None)):
    authorize(x_bank_token)
    row = ROWS.get(transaction_id)
    if row and row["unavailable"]:
        raise HTTPException(503, "Synthetic bank unavailable")
    if not row or not row["transaction"]:
        raise HTTPException(404, "Synthetic transaction not found")
    return row["transaction"]

@app.get("/ledger/{transaction_id}")
def ledger(transaction_id: str, x_bank_token: str | None = Header(default=None)):
    authorize(x_bank_token)
    row = ROWS.get(transaction_id)
    if row and row["unavailable"]:
        raise HTTPException(503, "Synthetic ledger unavailable")
    if not row or not row["transaction"]:
        raise HTTPException(404, "Synthetic ledger not found")
    return row["ledger"]
