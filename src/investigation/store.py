"""Synthetic snapshot lookup. No payment-writing capability is exposed."""
import json
from importlib.resources import files
from .models import Transaction, Policy

def load_data(name):
    return json.loads(files("investigation").joinpath("data", name).read_text())

class TransactionLookup:
    def __init__(self):
        self._rows = {row["id"]: Transaction.model_validate(row) for row in load_data("transactions.json")}

    def lookup(self, transaction_id: str) -> Transaction | None:
        return self._rows.get(transaction_id)

def policies():
    return [Policy.model_validate(row) for row in load_data("policies.json")]
