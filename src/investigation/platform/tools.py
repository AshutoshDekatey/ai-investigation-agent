import httpx
from pydantic import ValidationError
from .schemas import Transaction, Ledger

class BankTools:
    def __init__(self, base_url, token, client=None, timeout=2.0, attempts=2):
        if attempts not in (1, 2, 3) or not 0 < timeout <= 30:
            raise ValueError("Tool budgets out of bounds")
        self.client = client or httpx.Client(base_url=base_url, timeout=timeout, trust_env=False)
        self.token, self.timeout, self.attempts = token, timeout, attempts

    def lookup(self, kind, transaction_id):
        if kind not in ("transactions", "ledger"):
            raise ValueError("Read-only tool not allowed")
        events = []
        for attempt in range(1, self.attempts + 1):
            try:
                response = self.client.get(f"/{kind}/{transaction_id}", headers={"X-Bank-Token": self.token}, timeout=self.timeout)
                if response.status_code == 404:
                    events.append(dict(tool=kind, attempt=attempt, outcome="missing"))
                    return None, events
                response.raise_for_status()
                model = Transaction if kind == "transactions" else Ledger
                data = model.model_validate(response.json()).model_dump(mode="json")
                if kind == "transactions" and data["id"] != transaction_id:
                    raise ValueError("Transaction identifier mismatch")
                events.append(dict(tool=kind, attempt=attempt, outcome="ok"))
                return data, events
            except httpx.TimeoutException:
                outcome = "timeout"
            except httpx.HTTPError:
                outcome = "unavailable"
            except (ValueError, ValidationError):
                outcome = "invalid"
            events.append(dict(tool=kind, attempt=attempt, outcome=outcome))
            if outcome == "invalid" or ('response' in locals() and response.status_code in (401,403)):
                break
        return None, events

    def close(self):
        self.client.close()
